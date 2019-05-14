#!/usr/bin/env python

import coloredlogs, logging
logger=logging.getLogger(__name__)
coloredlogs.install(logger=logger,
        level='INFO',
        fmt='%(asctime)s %(hostname)s %(name)s[%(process)d] %(levelname)s %(message)s')

import sys
import os
import time
import json
import click
import itertools
from crawler import TwitterCrawler

WAIT_TIME = 30
CLIENT_ARGS = {"timeout": 30}


def flash_cmd_config(cmd_config, cmd_config_filepath, output_folder):

    with open(os.path.abspath(cmd_config_filepath), 'w') as cmd_config_wf:
        json.dump(cmd_config, cmd_config_wf)

    with open(os.path.abspath('%s/%s'%(output_folder, os.path.basename(cmd_config_filepath))), 'w') as cmd_config_wf:
        json.dump(cmd_config, cmd_config_wf)


#def collect_tweets_by_user_ids(users_config_filepath, output_folder, config):
def collect_tweets_by_user_ids(user_id, output_folder, config):

    #logger.info('Commencing crawl for user id: %s',user_id)

    since_id = 1
    apikeys = list(config['apikeys'].values()).pop()
    #logger.info(apikeys)
    #logger.info(type(apikeys))

    #sys.exit()

    twitterCrawler = TwitterCrawler(apikeys=apikeys, client_args=CLIENT_ARGS, output_folder = output_folder)
    twitterCrawler.fetch_user_timeline(user_id, since_id=since_id)

        #logger.error('Exception: %s',str(e))

    logger.info('Process finished for user id: %s',user_id)


@click.command()
@click.option('--user-id', '-u', 'user_', required=True, type=click.STRING)
@click.option('--output', '-o', 'output_', required=True, type=click.Path(exists=False))
@click.option('--config', '-c', 'config_', required=True, type=click.Path(exists=True))
def run(user_, output_, config_):
    """Simple script to get tweets using the twitter API."""

    logger.info('Start.')

    user_id=user_

    output_folder = os.path.abspath(output_)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    with open(os.path.abspath(config_), 'r') as config_f:
        config = json.load(config_f)

    logger.warn('user-id: %s',user_)
    logger.warn('output: %s',output_)
    logger.warn('Config is %s',config)

    #sys.exit()
    collect_tweets_by_user_ids(user_id, output_folder, config)


if __name__=="__main__":
    run()
