import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'tmp/app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_INIT = 'SUPER secret init Value!'

    '''
    WEB3_PROVIDER can be ipc or http
    '''
    WEB3_PROVIDER = 'http'
    WEB3_URI = 'http://public-node:8545/'

