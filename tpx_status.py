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

from flask import Flask, render_template, request, redirect, url_for, session

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
    print(args)
    instr = args['instr']
    date = args['date']
    statusType = args['statusType']
    status = args['status']
    statusMessage = args.get('statusMessage', 'NULL')
    print(statusMessage)
    response = ''

    # Create the instrument subclass object based on instr 
    try:
        instrumentStatus = INSTRUMENTS[instr](instr, date, statusType, status, statusMessage)
    except Exception as e:
        print(e)
        print('error creating the object')
        response = 'error creating the object'
    else:
        # execute the status function based on statusType
        try:
            response = instrumentStatus.types[instrumentStatus.statusType]()
        except Exception as e:
            print(e)
            print('error executing the status type')
            response = 'error executing the status type'
        else:
            print(response)
    return response

