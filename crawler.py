#!/usr/bin/env python

import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger,
        level='INFO',
        fmt='%(asctime)s,%(msecs)03d %(hostname)s %(name)s [%(process)d] %(levelname)s %(message)s')

import os
import time
import json
import datetime
import re

import twython
import copy
import sys

#from exceptions import MissingArgs
class MissingArgs(Exception):
    pass


MAX_RETRY_CNT = 3
WAIT_TIME = 30

class TwitterCrawler(twython.Twython):

    def __init__(self, *args, **kwargs):

        logger.info('Initing TwitterCrawler.')

        # get apikeys
        apikeys = copy.copy(kwargs.pop('apikeys', None))
        if not apikeys:
            raise MissingArgs('apikeys is missing')
        self.apikeys = copy.copy(apikeys)
        #logger.info('API keys obtained.')

        # get output folder
        self.output_folder = kwargs.pop('output_folder')
        #logger.info('Output folder obtained.')

        # init twython, get access token
        logger.info('APIKeys: %s',self.apikeys)
        #twitter = twython.Twython(apikeys['app_key'], apikeys['app_secret'], apikeys['oauth_token'], apikeys['oauth_token_secret'], oauth_version=2)
        twitter = twython.Twython(apikeys['app_key'], apikeys['app_secret'],oauth_version=2)
        logger.info('Fetching access token...')
        access_token = twitter.obtain_access_token()
        logger.info('Access token obtained: %s',access_token)
        #try:
        #    logger.info(twitter.verify_credentials())
        #except Exception as e:
        #    logger.error('Cannot authenticate with Twitter API.')
        #    sys.exit()

        # set access token in kwargs
        kwargs['access_token'] = access_token
        # inject api keys into kwargs
        apikeys.pop('app_secret')
        kwargs.update(apikeys)

        logger.info('kwargs: %s',kwargs)

        super(TwitterCrawler, self).__init__(*args, **kwargs)



    def rate_limit_error_occured(self, resource, api):

        logger.warn('Rate limit reached')

        # twitter returns what your rate-limit status for the specified resource is.
        rate_limits = self.get_application_rate_limit_status(resources=[resource])

        # copied from stack overflow
        wait_for = int(rate_limits['resources'][resource][api]['reset']) - time.time() + WAIT_TIME

        if wait_for < 0:
            wait_for = 60
        logger.info('Sleep for %d seconds.',wait_for)

        time.sleep(wait_for)
        logger.info('Resume.')


    def fetch_user_timeline(self, user_id = None, since_id = 1):

        logger.info('Commencing tweet crawl for user_id: %s',user_id)

        if not user_id:
            raise Exception("user_timeline: user_id cannot be None")

        #handle_output_folder = os.path.abspath('%s/%s',self.output_folder, user_id)

        filename = os.path.join(self.output_folder, user_id)
        logger.info('Output file: %s',filename)

        num_times_api_called=0

        current_since_id = since_id

        prev_max_id = -1
        current_max_id = 0
        cnt = 0
        retry_cnt = MAX_RETRY_CNT

        while (current_max_id != prev_max_id and retry_cnt > 0):

            try:

                logger.info('Get more tweets...')

                if current_max_id > 0:
                    logger.debug('current max id (%d) > 0',current_max_id)
                    tweets = self.get_user_timeline(user_id=user_id, tweet_mode='extended', since_id = since_id, max_id=current_max_id - 1, count=200)
                else:
                    logger.debug('current max id (%d) <= 0',current_max_id)
                    tweets = self.get_user_timeline(user_id=user_id, tweet_mode='extended', since_id = since_id, count=200)

                num_times_api_called=num_times_api_called+1
                logger.info('Number of calls issued to Twitter API so far: %d',num_times_api_called)

                prev_max_id = current_max_id # if no new tweets are found, the prev_max_id will be the same as current_max_id

                logger.info('File write begins: %s',filename)

                with open(filename, mode='ab') as f:

                    f.write('[\n')

                    for idx,tweet in enumerate(tweets):
                        #logger.info('Wrote tweet #%d',idx)
                        f.write('%s,\n',json.dumps(tweet))
                        if current_max_id == 0 or current_max_id > int(tweet['id']):
                            current_max_id = int(tweet['id'])
                        if current_since_id == 0 or current_since_id < int(tweet['id']):
                            current_since_id = int(tweet['id'])

                    f.write('\n]\n')

                # no new tweets found
                if (prev_max_id == current_max_id):
                    logger.info('breaking: %s',user_id)
                    break

                cnt += len(tweets)
                time.sleep(1)



            except twython.exceptions.TwythonRateLimitError:
                self.rate_limit_error_occured('statuses', '/statuses/user_timeline')
            except Exception as e:
                logger.error('Exception: %s',e)
                logger.error('Encountered while crawling tweets for user_id: %s',user_id)
                return since_id, True

        logger.warn('Finished crawling for user id: %d',user_id)
        logger.warn('Num tweets found: %d',cnt)

        return current_since_id, False

