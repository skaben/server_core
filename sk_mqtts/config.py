# -*- encoding: utf-8

import os
import yaml
import redis
import logging
from rq import Queue
from collections import namedtuple

basedir = os.path.abspath(os.path.dirname(__file__))
confpath = f'{basedir}/config.yaml'
assert os.path.exists(confpath), \
     confpath
#    logging.error(f'[!] {confpath} file is missing')


def configure(confpath):
    config = dict()

    try:
        #  loading parameters from yaml config file
        with open(confpath) as conf:
            config.update(yaml.safe_load(conf))
    except:
        raise

    if not config.get('timeout'):
        # TODO: error handling
        print('[!] config {} section missing'.format(k))
        raise SystemExit

    basic_to = config['timeout'].get('basic', 1)
    alive_to = config['timeout'].get('alive', 5)

    rec_to = int(basic_to) * len(config['dev_types'])

    if alive_to < rec_to:
        print("[?] timeout {} is less than recommended {}".format(alive_to,
                                                                  rec_to))

    return namedtuple("config", config.keys())(*config.values())

config = configure(confpath)
