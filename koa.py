from flask import Flask, render_template, request, redirect, url_for, session
from tpx_gui import tpx_gui 
from tpx_status import tpx_status, INSTRUMENTS
import argparse
import logging


app = Flask(__name__)

def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)

app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#establish tpxgui route
@app.route('/tpxgui/',methods=['POST','GET'])
def tpxgui():
    return tpx_gui(dev=debug)

@app.route('/tpx_status/',methods=['POST','GET'])
def tpx_status():
    return tpx_status()


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
        print (f"ERROR: Unable to create logger '{name}' in dir {logfile}.\nReason: {str(error)}")



if __name__ == '__main__':

    # define arg parser
    parser = argparse.ArgumentParser(description="Start KOA Ingestion API.")
    parser.add_argument("port", type=int, help="Flask server port.")
    parser.add_argument("mode", type=str, choices=['dev', 'release'], 
                        help="Determines database access and flask debugging mode.")

    #get args and define inputs
    args = parser.parse_args()
    port = args.port
    mode = args.mode
    debug = False if mode == 'release' else True
    host = '0.0.0.0'

    #create logger first
    logdir = '/tmp' if debug else 'home/koaadmin/log'
    create_logger('tpxgui', logdir)
    log = logging.getLogger('tpxgui')

    #run flask server
    log.info(f"Starting KOA TPX GUI:\nPORT = {port}\nMODE = {mode}")
    app.run(host=host, port=port, debug=debug)
    log.info("Stopping KOA TPX GUI.\n")
