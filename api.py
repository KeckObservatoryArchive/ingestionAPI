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
    args = request.args
    #print(args)
    instr = args['instr'].lower()
    date = args['date']
    statusType = args['statusType']
    status = args['status']
    statusMessage = args.get('statusMessage', 'NULL')
    #print(statusMessage)
    response = ''
    #print('instr: ', instr, '\ndate: ', date, '\nstatusType: ', statusType, '\nstatus: ', status)

    # Create the instrument subclass object based on instr 
    try:
        instrumentStatus = INSTRUMENTS[instr](instr, date, statusType, status, statusMessage)
    except Exception as e:
        print('error creating the object: ', e)
        response = {'APIStatus':'ERROR', 'Message':'error creating the object'}
    else:
        # execute the status function based on statusType
        try:
            response = instrumentStatus.types[instrumentStatus.statusType]()
        except Exception as e:
            print('error executing the status type: ', e)
            response = {'APIStatus':'ERROR', 'Message':'error executing the status type'}
        else:
            print(response)
    return json.dumps(response)

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 50202
    debug = True
    app.run(host=host,port=port,debug=debug)
