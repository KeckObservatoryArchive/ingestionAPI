import pymysql
#import pymysql.cursors
import confparse

class db_conn(object):
    def __init__(self, database='', test=True):
        config = confparse.ConfigParser('config.live.ini')
        self.db = config.get_db()
        self.server = config.get_host()
        self.port = config.get_port()
        self.user = config.get_user()
        self.pwd = config.get_pass()
        if test == True:
            self.db = 'test'
        self.readOnly = 0
        del config

    def db_connect(self):
        '''
        Connect to the specified database.  If primary server is down and backup
        is specified, then connect to it.  This also set the readOnly flag to 1.
        '''
        try:
            # Primary connection

            self.dbConn = pymysql.connect(self.server, self.user, self.pwd, self.db, cursorclass=pymysql.cursors.DictCursor)
        except Exception as e:
            print(e)
            self.dbConn = 0

            # Backup connection

#if self.backupServer:
#                try:
#                    self.dbConn = pymysql.connect(self.backupServer, self.user, self.pwd, self.db, cursorclass=pymysql.cursors.DictCursor)
#                    self.readOnly = 1
#                except:
#                    self.dbConn = 0

    def db_close(self):
        '''
        Closes the current database connection
        '''

        if self.dbConn:
            self.dbConn.close()

    def do_query(self, query, output=''):
        self.db_connect()

        # Save as a list of dictionaries

        query = ''.join(query)
        result = None
        print(self.dbConn.cursor())
        with self.dbConn.cursor() as cursor:
            print("cursor:\t",cursor)
            num = cursor.execute(query)
            result = cursor.fetchall()
        self.db_close()
        return result
