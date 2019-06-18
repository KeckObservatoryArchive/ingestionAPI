import json

class ConfigParser:
    def __init__(self, config):
        with open(config,'r') as f:
            conf = json.loads(f.read())
        self.host = conf['host']
        self.port = conf['port']
        self.db = conf['db']
        self.user = conf['user']
        self.word = conf['word']
        del conf

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_user(self):
        return self.user

    def get_pass(self):
        return self.word

    def get_db(self):
        return self.db
