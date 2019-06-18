import db_conn as DBC

class Instrument:
    def __init__(self, date, statusType, status):
        self.date = date
        self.statusType = statusType
        self.status = status
        self.stagedir = ''
        self.types = {
                'lev0':self.lev0Status,
                'lev1':self.lev1Status,
                'lev2':self.lev2Status,
                'trs':self.trsStatus,
                'psfr':self.psfrStatus,
                'weather':self.weatherStatus
                }

    def lev0Status(self):
        #response = ''
        #if self.status == 'good':
        #    pass
        #elif self.status == 'bad':
        #    pass
        #else:
        #    pass
        #return response
        return self.statusType + ' ingestion was ' + self.status

    def lev1Status(self):
        return self.statusType + ' ingestion was ' + self.status

    def lev2Status(self):
        return self.statusType + ' ingestion was ' + self.status

    def trsStatus(self):
        return self.statusType + ' ingestion was ' + self.status

    def psfrStatus(self):
        return self.statusType + ' ingestion was ' + self.status

    def weatherStatus(self):
        return self.statusType + ' ingestion was ' + self.status

