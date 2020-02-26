import json

class ConfigParser:
    def __init__(self, dbm, svc, config):
        with open(config,'r') as f:
            conf = json.loads(f.read())

            self.host = conf[dbm][svc]['host']
        self.port = conf[dbm][svc]['port']
        self.db = conf[dbm][svc]['db']
        self.user = conf[dbm][svc]['user']
        self.word = conf[dbm][svc]['word']
        self.emailto = conf['emailto']
        self.emailfrom = conf['emailfrom']
        
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

    def get_emailto(self):
        return self.emailto

    def get_emailfrom(self):
        return self.emailfrom
