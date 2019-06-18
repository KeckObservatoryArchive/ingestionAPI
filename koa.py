from flask import Flask, render_template, request, redirect, url_for, session
from tpx_gui import tpx_gui 
#from api import *

#import tpx_gui
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#establish tpxgui route
@app.route('/tpxgui/',methods=['POST','GET'])
def tpxgui():
    return tpx_gui()

@app.route('/tpx_status/',methods=['POST','GET'])
def tpx_status():
    return 

#run on port 50001
if __name__ == '__main__':
    host = '0.0.0.0'
    port = 50001
    debug = True
    app.run(host=host,port=port,debug=debug)
