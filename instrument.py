import db_conn as DBC
from datetime import datetime as DT
import sys
import confparse

sys.path.append('/kroot/archive/common/default')
from send_email import send_email

class Instrument:
    '''
    Base instrument class that handles all the general definitions
    for the tpx_status ingestion api.

    This API assumes that records are being entered during the
    DQA processing in DEP.

    Member Variables:
    obsDate: date of observation of the file(s) being ingested
    currentDate: Date of when the ingestion is happening
    curentTime: Time of when the ingestion is happening
    statusType: Type of file(s) being ingested
        lev0, lev1, lev2, trs, psfr, weather
    status: Status of the ingestions
        DONE, ERROR, NA
    statusMessage: Any message associated with the status, usually
        for errors. Defaults to NULL

    Member Methods:
    lev0Status(): API call to report the status of lev0 files
    lev1Status(): API call to report the status of lev1 files
    lev2Status(): API call to report the status of lev2 files
    trsStatus(): API call to report the status of TRS files
    psfrStatus(): API call to report the status of PSFR files
    weatherStatus(): API call to report the status of weather files
    '''
    def __init__(self, date, statusType, status, statusMessage='NULL'):
        self.obsDate = date
        self.currentDate = DT.strftime(DT.utcnow(), '%Y-%m-%d')
        self.currentTime = DT.strftime(DT.utcnow(), '%Y%m%d %H:%M:%S')
        self.statusType = statusType
        self.status = status
        self.statusMessage = statusMessage
        self.datadir = ''
        self.stagedir = ''
        self.instr = ''
        self.emailTo = 'koaadmin@keck.hawaii.edu'
        self.emailFrom = 'koaadmin@keck.hawaii.edu'

        # Dictionary of all the status methods by statusType keyword
        self.types = {
                'meta':self.metaStatus,
                'lev0':self.lev0Status,
                'lev1':self.lev1Status,
                'lev2':self.lev2Status,
                'trs':self.trsStatus,
                'psfr':self.psfrStatus,
                'weather':self.weatherStatus
                }

        self.config = confparse.ConfigParser(None, None, 'config.live.ini')

    def lev0Status(self):
        '''
        API command to update the status of the TPX transfers
        '''
        query = ''.join(['UPDATE koatpx SET tpx_stat="', self.status,
            '", tpx_time="', self.currentTime[:-3], '", comment=', self.statusMessage,
            ' WHERE utdate="', self.obsDate, '" and instr="', self.instr,'";'])

        # Future query for file-by-file ingestion
        # query = ''.join(['UPDATE koatpx SET tpx_stat=', self.status,
        #     ', tpx_time=', self.currentTime, ' WHERE koaid=', self.koaid,])
#        db = DBC.db_conn()
#        if self.status not in ['DONE','ERROR']:
#            self.status == 'NA'
#        db.do_query(query)
        return self.statusType + ' ingestion was ' + self.status

    def lev1Status(self):
        '''
        API command to update the status of the TPX transfers
        '''
        query = ''.join(['UPDATE koatpx SET lev1_stat="', self.status,
            '", lev1_time="', self.currentTime[:-3], '", comment=', self.statusMessage,
            ' WHERE utdate="', self.obsDate, '" and instr="', self.instr,'";'])

        # Future query for file-by-file ingestion
        # query = ''.join(['UPDATE koatpx SET lev1_stat=', self.status,
        #     ', lev1_time=', self.currentTime, ' WHERE koaid=', self.koaid,])
#        db = DBC.db_conn()
#        if self.status not in ['DONE','ERROR']:
#            self.status == 'NA'
#        db.do_query(query)
        return self.statusType + ' ingestion was ' + self.status

    def lev2Status(self):
        '''
        API command to update the status of the TPX transfers
        '''
#        query = ''.join(['UPDATE koatpx SET lev2_stat="', self.status,
#            '", lev2_time="', self.currentTime[:-3], '", comment=', self.statusMessage,
#            ' WHERE utdate="', self.obsDate, '" and instr="', self.instr,'";'])
#
#        # Future query for file-by-file ingestion
#        # query = ''.join(['UPDATE koatpx SET lev2_stat=', self.status,
#        #     ', lev2_time=', self.currentTime[:-3], ' WHERE koaid=', self.koaid,])
#        db = DBC.db_conn()
#        if self.status not in ['DONE','ERROR']:
#            self.status == 'NA'
#        db.do_query(query)
        return self.statusType + ' ingestion was ' + self.status

    def trsStatus(self):
        '''
        API command to update the status of the TPX transfers
        '''
        # set up return dictionary
        myString = self.statusType + ' ingestion was ' + self.status
        ingestTime = DT.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        myDict = {}
        myDict['APIStatus'] = 'COMPLETE'
        myDict['UTDate'] = self.obsDate
        myDict['Instrument'] = self.instr
        myDict['statusType'] = 'trs'
        myDict['status'] = self.status
        myDict['Message'] = myString
        myDict['Timestamp'] = ingestTime

        subject = 'trsStatus error'

        # Check to see what the status from IPAC was
        if self.status in ['DONE','ERROR']:
            #query = ('UPDATE psfr SET ',
            #         'ingest_time="',
            query = ('UPDATE psfr SET ingest_stat="',
                     self.status,
                     '", ingest_time="',
                     ingestTime,
                     '"',
                     ' WHERE utdate="',
                     self.obsDate,
                     '" and instr="',
                     self.instr,
                     '"')

#        # Future query for file-by-file ingestion
#        # query = ''.join(['UPDATE koatpx SET trs_stat=', self.status,
#        #     ', trs_time=', self.currentTime, ' WHERE koaid=', self.koaid,])
            try:
                db = DBC.db_conn("mysql","koa",test=False)
            except Exception as e:
                print('Error setting up the connection object: ', e)
            else:
                try:
                    test = db.do_query(query)
                except Exception as e:
                    print('could not complete the query')

            if self.status == 'ERROR':
                self.sendEmail(subject, myDict)
        else:
            myDict['APIStatus'] = 'INCOMPLETE'
            self.sendEmail(subject, myDict)

        return myDict

    def psfrStatus(self):
        '''
        API command to update the status of the TPX transfers
        '''
#        query = ''.join(['UPDATE psfr SET ingest_stat="', self.status,
#            '", ingest_time="', self.currentTime, '",
#            ' WHERE utdate="', self.obsDate, 
#            '" and instr="', self.instr,'";'])
#
#        # Future query for file-by-file ingestion
#        # query = ''.join(['UPDATE psfr SET ingest_stat=', self.status,
#        #     ', ingest_time=', self.currentTime, ' WHERE koaid=', self.koaid])
#        db = DBC.db_conn()
#        if self.status not in ['DONE','ERROR']:
#            self.status == 'NA'
#        db.do_query(query)
        return self.statusType + ' ingestion was ' + self.status

    def metaStatus(self):
        '''
        API command to update the status of the TPX transfers
        '''
        query = ''.join(['UPDATE koatpx SET metadata_stat="', self.status,
            '", metadata_time="', self.currentTime[:-3], '", comment=', self.statusMessage,
            ' WHERE utdate="', self.obsDate, '" and instr="', self.instr,'";'])

        # Future query for file-by-file ingestion
        # query = ''.join(['UPDATE koatpx SET psfr_stat=', self.status,
        #     ', psfr_time=', self.currentTime, ' WHERE koaid=', self.koaid,])
#        db = DBC.db_conn()
#        if self.status not in ['DONE','ERROR']:
#            self.status == 'NA'
#        db.do_query(query)
        return self.statusType + ' ingestion was ' + self.status

    def weatherStatus(self):
        return self.statusType + ' ingestion was ' + self.status

    def sendEmail(self, subject, myDict):
        '''
        '''
        
        body = ''
        for key,value in myDict.items():
            body = f"{body}\n{key} -- {value}"
        send_email(self.config.get_emailto(), self.config.get_emailfrom(), subject, body)

