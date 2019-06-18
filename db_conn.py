import pymysql
import pymysql.cursors
import confparse

class db_conn(object):
    def __init__(self, database=''):
        config = confparse.ConfigParser('config.live.ini')
        self.db = config.get_db()
        self.server = config.get_host()
        self.port = config.get_port()
        self.user = config.get_user()
        self.pwd = config.get_pass()
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
        except:
            self.dbConn = 0

            # Backup connection

            if self.backupServer:
                try:
                    self.dbConn = pymysql.connect(self.backupServer, self.user, self.pwd, self.db, cursorclass=pymysql.cursors.DictCursor)
                    self.readOnly = 1
                except:
                    self.dbConn = 0

    def db_close(self):
        '''
        Closes the current database connection
        '''

        if self.dbConn:
            self.dbConn.close()

    def do_query(self, query, output):
        self.db_connect()

        # Save as a list of dictionaries

        query = ''.join(query)
        with self.dbConn.cursor() as cursor:
            num = cursor.execute(query)
            result = cursor.fetchall()
            if num == 0:
                value = {}
                if output == 'txt':
                    value = ' '
            elif num == 1:
                value = {}
                for row in result:
                    for f in row.keys():
                        value[f] = str(row[f])

                # Convert to text output

                if output == 'txt':
                    v = ''
                    for key, val in row.items():
                        v = v + ' ' + str(val)
                    value = v
            else:
                value = []
                count = 0
                for row in result:
                    value.insert(count, {})
                    for f in row.keys():
                        value[count][f] = str(row[f])
                    count += 1

                # Convert to text output

                if output == 'txt':
                    v = ''
                    count = 0
                    for row in value:
                        if count > 0:
                            v = v + '<br>'
                        for key, val in row.items():
                            v = v + ' ' + str(val)
                        count += 1
                    value = v

        self.db_close()
        return value
