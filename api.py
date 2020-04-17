import db_conn
import instrument
import nires
import hires
import deimos
import lris
import kcwi
import nirc2
import nirspec
import osiris
import esi
import mosfire
import weather
import json
import argparse
import logging

from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# Create a dictionare of the instrument Constructors
INSTRUMENTS = {
        'deimos':deimos.Deimos,
        'esi':esi.Esi,
        'hires':hires.Hires,
        'kcwi':kcwi.Kcwi,
        'lris':lris.Lris,
        'mosfire':mosfire.Mosfire,
        'nirc2':nirc2.Nirc2,
        'nires':nires.Nires,
        'nirspec':nirspec.Nirspec,
        'osiris':osiris.Osiris,
        'weather':weather.Weather
        }


@app.route('/tpx_status/', methods=('GET','POST'))
def tpx_status():
    '''
    Method to update the transfer status of koa data

    Arguments for the update will be passed via GET or POST
    instr: the instrument that created the data
    @type instr: string
    date: the utdate the instrument took the data
    @type date: string
    statusType: the type of file transfered
    @type statusType: string
    status: the status of the ingestion from IPAC
    @type status: string
    '''

    # get the arguments passed as a get or post
    log.info(request.args)
    args = request.args
    instr = args['instr'].lower()
    date = args['date']
    statusType = args['statusType']
    status = args['status']
    statusMessage = args.get('statusMessage', 'NULL')
    response = ''
    #print('instr: ', instr, '\ndate: ', date, '\nstatusType: ', statusType, '\nstatus: ', status)

    # Create the instrument subclass object based on instr 
    try:
        instrumentStatus = INSTRUMENTS[instr](instr, date, statusType, status, statusMessage, debug)
    except Exception as e:
        print('error creating the object: ', e)
        response = {'APIStatus':'ERROR', 'Message':'error creating the object'}
    else:
        # execute the status function based on statusType
        try:
            instrumentStatus.myDict['Instrument'] = instrumentStatus.instr
            response = instrumentStatus.types[instrumentStatus.statusType]()
        except Exception as e:
            print('error executing the status type: ', e)
            response = {'APIStatus':'ERROR', 'Message':'error executing the status type'}
        else:
            print(response)
    return json.dumps(response)


def create_logger(name, logdir):
    try:
        #Create logger object
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        #file handler (full debug logging)
        logfile = f'{logdir}/{name}.log'
        handler = logging.FileHandler(logfile)
        handler.setLevel(logging.DEBUG)
        handler.suffix = "%Y%m%d"
        logger.addHandler(handler)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        #stream/console handler (info+ only)
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(' %(levelname)8s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    except Exception as error:
        print (f"ERROR: Unable to create logger '{name}'.\nReason: {str(error)}")



if __name__ == '__main__':

    # define arg parser
    parser = argparse.ArgumentParser(description="Start KOA Ingestion API.")
    parser.add_argument("port", type=int, help="Flask server port.")
    parser.add_argument("--mode", type=str, choices=['dev', 'release'], default='release',
                        help="Determines database access and flask debugging mode.")

    #get args and define inputs
    args = parser.parse_args()
    port = args.port
    mode = args.mode
    debug = False if mode == 'release' else True

    host = '0.0.0.0'

    #create logger first
    logdir = '/tmp' if debug else '/log'
    create_logger('ingestapi', logdir)
    log = logging.getLogger('ingestapi')

    #run flask server
    log.info(f"Starting KOA ingestion API:\nPORT = {port}\nMODE = {mode}")
    app.run(host=host, port=port, debug=debug)
    log.info("Stopping KOA ingestion API.\n")
