#!/usr/bin/env python

import coloredlogs, logging
logger = logging.getLogger(__name__)
coloredlogs.install(logger=logger,
        level='INFO',
        fmt='%(asctime)s,%(msecs)03d %(hostname)s %(name)s [%(process)d] %(levelname)s %(message)s')

import os
import time
import json


import twython
import copy
import sys, traceback


#from exceptions import MissingArgs
class MissingArgs(Exception):
    pass


MAX_RETRY_CNT = 3
WAIT_TIME = 30

NUM_TWEETS_IN_A_SINGLE_FETCH=200

def full_stack():
    exc = sys.exc_info()[0]
    stack = traceback.extract_stack()[:-1]  # last one would be full_stack()
    if not exc is None:  # i.e. if an exception is present
        del stack[-1]       # remove call of full_stack, the printed exception
                            # will contain the caught exception caller instead
    trc = 'Traceback (most recent call last):\n'
    stackstr = trc + ''.join(traceback.format_list(stack))
    if not exc is None:
         stackstr += '  ' + traceback.format_exc().lstrip(trc)
    return stackstr

class TwitterCrawler():

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
        APP_KEY=apikeys['app_key']
        APP_SECRET=apikeys['app_secret']

        #twitter = twython.Twython(apikeys['app_key'], apikeys['app_secret'], apikeys['oauth_token'], apikeys['oauth_token_secret'], oauth_version=2)
        twitter = twython.Twython(APP_KEY, APP_SECRET, oauth_version=2)
        #logger.info('Fetching access token...')
        ACCESS_TOKEN = twitter.obtain_access_token()
        logger.info('Access token obtained: %s',ACCESS_TOKEN)
        #try:
        #    logger.info(twitter.verify_credentials())
        #except Exception as e:
        #    logger.error('Cannot authenticate with Twitter API.')
        #    sys.exit()

        # set access token in kwargs
        #kwargs['access_token'] = access_token
        # inject api keys into kwargs
        #apikeys.pop('app_secret')
        #kwargs.update(apikeys)

        #logger.info('kwargs: %s',kwargs)
        self.twitter = twython.Twython(APP_KEY, access_token=ACCESS_TOKEN)
        logger.info('constructor call finished.')
        #super(TwitterCrawler, self).__init__(*args, **kwargs)



    def rate_limit_error_occured(self, resource, api):

        logger.warning('Rate limit reached')

        # twitter returns what your rate-limit status for the specified resource is.
        rate_limits = self.twitter.get_application_rate_limit_status(resources=[resource])

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
        num_tweets = 0
        retry_cnt = MAX_RETRY_CNT

        with open(filename, mode='w') as f:
            f.write('[\n')

        while (current_max_id != prev_max_id and retry_cnt > 0):

            try:

                logger.info('Get more tweets...')

                if current_max_id > 0:
                    tweets = self.twitter.get_user_timeline(user_id=user_id, tweet_mode='extended', since_id=since_id, max_id=current_max_id-1, count=NUM_TWEETS_IN_A_SINGLE_FETCH)
                else:
                    tweets = self.twitter.get_user_timeline(user_id=user_id, tweet_mode='extended', since_id=since_id, count=NUM_TWEETS_IN_A_SINGLE_FETCH)

                num_times_api_called=num_times_api_called+1
                logger.info('Number of calls issued to Twitter API so far: %d', num_times_api_called)

                logger.info('I found %d tweets to write.', len(tweets))
                num_tweets += len(tweets)
                logger.info('Total tweets collected so far: %d', num_tweets)

                logger.info('will write to file...')

                prev_max_id = current_max_id
                with open(filename, mode='a') as f:

                    for idx, tweet in enumerate(tweets):
                        f.write(json.dumps(tweet)+',\n')

                        if current_max_id == 0 or current_max_id > int(tweet['id']):
                            current_max_id = int(tweet['id'])


                logger.info('done.')

                # no new tweets found
                if (prev_max_id == current_max_id):
                    logger.info('breaking: %s',user_id)
                    break


                time.sleep(1)



            except twython.exceptions.TwythonRateLimitError:
                self.rate_limit_error_occured('statuses', '/statuses/user_timeline')
            except Exception as e:
                logger.error('Exception: %s',str(e))
                logger.error('StackTrace: %s', full_stack())
                logger.error('Encountered while crawling tweets for user_id: %s',user_id)
                return since_id, True

        with open(filename, mode='a') as f:
            f.write(']\n')

        logger.warn('Finished crawling for user id: %s',user_id)
        logger.warn('Num tweets found: %d',num_tweets)


