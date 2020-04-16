import db_conn as DBC
from datetime import datetime as DT
import sys
import confparse
import urllib.request as URL
from dep_pi_email import dep_pi_email

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
    def __init__(self, date, statusType, status, statusMessage='NULL', dev=False):
        self.obsDate = date
        self.currentDate = DT.strftime(DT.utcnow(), '%Y-%m-%d')
        self.currentTime = DT.strftime(DT.utcnow(), '%Y%m%d %H:%M:%S')
        self.statusType = statusType
        self.status = status
        self.statusMessage = statusMessage
        self.dev = dev
        self.datadir = ''
        self.stagedir = ''
        self.instr = ''
        self.emailTo = 'koaadmin@keck.hawaii.edu'
        self.emailFrom = 'koaadmin@keck.hawaii.edu'
        self.BASEURL = 'https://www.keck.hawaii.edu/software/db_api/'

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

        # Dictionary with information to return back to user
        self.myDict = {}
        self.myDict['APIStatus'] = 'COMPLETE'
        self.myDict['UTDate'] = self.obsDate
        self.myDict['Instrument'] = self.instr
        self.myDict['statusType'] = self.statusType
        self.myDict['status'] = self.status
        self.myDict['statusMessage'] = self.statusMessage
        self.myDict['message'] = self.statusType + ' ingestion was ' + self.status
        self.myDict['Timestamp'] = self.currentTime

        self.config = confparse.ConfigParser(None, None, 'config.live.ini')

        #db conn object (toggle for dev or release)
        config_key = 'database_dev' if self.dev else 'database'
        self.db = DBC.db_conn('config.live.ini', configKey=config_key)

    def lev0Status(self):
        '''
        API command to update the status of the TPX transfers
        '''

        ingestTime = DT.utcnow().strftime('%Y%m%d %H:%M')

        # Check to see what the status from IPAC was
        if self.status in ['DONE','ERROR']:
            query = ('UPDATE koatpx SET tpx_stat="',
                     self.status,
                     '", tpx_time="',
                     ingestTime,
                     '"',
                     ' WHERE utdate="',
                     self.obsDate,
                     '" and instr="',
                     self.instr,
                     '"')
            try:
                if self.dev: print("DEV: NO QUERY: ", ''.join(query))
                else: test = self.db.query(query)
            except Exception as e:
                print('could not complete the query')

            if self.status == 'ERROR':
                self.sendEmail('lev0 error', self.myDict)
            elif self.status == 'DONE':
                dep_pi_email(self.instr, self.obsDate, 0)

        else:
            self.myDict['APIStatus'] = 'INCOMPLETE'
            self.sendEmail('lev0 error', self.myDict)

        return self.myDict

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
#        if self.status not in ['DONE','ERROR']:
#            self.status == 'NA'
#        self.db.query(query)
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
#        if self.status not in ['DONE','ERROR']:
#            self.status == 'NA'
#        self.db.query(query)
        return self.statusType + ' ingestion was ' + self.status

    def trsStatus(self):
        '''
        API command to update the status of the TPX transfers
        '''

        ingestTime = DT.utcnow().strftime('%Y-%m-%d %H:%M:%S')

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
                pass
#                    test = self.db.query(query)
            except Exception as e:
                print('could not complete the query')

            if self.status == 'ERROR':
                self.sendEmail(subject, self.myDict)
        else:
            self.myDict['APIStatus'] = 'INCOMPLETE'
            self.sendEmail(subject, self.myDict)

        return self.myDict

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
#        if self.status not in ['DONE','ERROR']:
#            self.status == 'NA'
#        self.db.query(query)
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
#        if self.status not in ['DONE','ERROR']:
#            self.status == 'NA'
#        self.db.query(query)
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

    def getPIEmail (self, semid):
        result = None
        url = f'{self.BASEURL}proposalsAPI.php?ktn={semid}&cmd=getPIEmail'
        try:
            result = URL.urlopen(url).read().decode('utf-8')
        except Exception as e:
            print(f'could not open url: {e}')
        return result

