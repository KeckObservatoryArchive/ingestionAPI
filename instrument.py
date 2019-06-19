import db_conn as DBC
from datetime import datetime as DT

class Instrument:
    def __init__(self, date, statusType, status):
        self.obsDate = date
        self.currentDate = DT.strftime(DT.now(), '%Y-%m-%d')
        self.currentTime = DT.strftime(DT.now(), '%Y%m%d %H:%M')
        self.statusType = statusType
        self.status = status
        self.stagedir = ''
        self.instr = ''
        self.types = {
                'lev0':self.lev0Status,
                'lev1':self.lev1Status,
                'lev2':self.lev2Status,
                'trs':self.trsStatus,
                'psfr':self.psfrStatus,
                'weather':self.weatherStatus
                }

    def lev0Status(self):
        '''
        API command to update the status of the TPX transfers

        TODO: Add a statusMessage to the table
        '''
        print(self.obsDate)
        query = ''.join(['UPDATE koatpx SET tpx_stat="', self.status,
            '", tpx_time="', self.currentTime, '" WHERE utdate="', self.obsDate,
            '" and instr="', self.instr,'";'])
        print(query)

        # Future query for file-by-file ingestion
        # query = ''.join(['UPDATE koatpx SET tpx_stat=', self.status,
        #     ', tpx_time=', self.currentTime, ' WHERE koaid=', self.koaid,])
        db = DBC.db_conn()
        if self.status not in ['DONE','ERROR']:
            self.status == 'NA'
        db.do_query(query)
        print('did the query')
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

