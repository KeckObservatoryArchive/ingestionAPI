from flask import Flask, render_template, request, redirect, url_for, session
import numpy as np
import db_conn
import datetime

def tpx_gui(dev=False):
    #return
    #get currently selected instrument, default all
    instr = request.args.get("instrument","%")
    if not instr:
        instr = '%'
    #get system time
    cur_date = datetime.datetime.today()
    #get static dates for later use
    static_date = datetime.datetime.now()
    static_year = static_date.year
    static_month = static_date.month
    static_day = static_date.day
    #grab selected parameters from drop-down menu
    year = request.args.get("year")
    month = request.args.get("month")
    day = request.args.get("day")
    table = request.args.get("table")
 
    #if nothing selected, default to today's date
    if year == None and month == None and day == None:
        date = str(static_year)+'-'+str(static_month).zfill(2)+'-'+str(static_day).zfill(2)
        year = static_year
        month = static_month
        day = static_day
        table = 'koatpx'
    else:  
    	#if day is 0, choose entire month of data
        if day != "0":
            date = str(year)+'-'+str(month).zfill(2)+'-'+str(day).zfill(2)
        else:
            date = str(year)+'-'+str(month).zfill(2)+'%'

    #print(date)
    #connect to database
    db = db_conn.db_conn('config.live.ini', configKey='database')
    #db.db_connect()
    #koatpx database SQL query/header
    if table=='koatpx':
        query = ("select koatpx.*,koadrp.endTime as lev1_done from koatpx left join koadrp ",
                 "on koatpx.instr=koadrp.instr and koatpx.utdate=koadrp.utdate where ",
                 "koatpx.instr like '",instr,"' and koatpx.utdate like '",
                 date,"' order by utdate desc, instr asc")
        #establish new header
        page_header = ['UT Date of Observation','Tel Instr','PI','# Original Files','# Archived Files',
                   'Science Files','Size(GB)','Summit Disk (sdata#)','Data On Stage Disk','Files Archive-Ready',
                   'Metadata Sent','2 DVDs Written','DVD Stored @ CARA','Data Sent to NExScI',
                   'TPX Complete','L1 Done','L1 Sent to NExScI','L1 Complete']
    #koadrp database SQL query/header
    else:
        query = ("select * from koadrp where instr like '",instr,"' and utdate like '",
                 date,"' order by utdate desc, instr asc")
        #establish new header
        page_header = ['UT Date of Observation','Instrument','Phase','Files','Reduced','Start Time', 'Start Reduce',
                       'End Time','Time Lost','Notes']

    #do query
    result = db.query(query)
    #if query does not exist, do not make data table, render template
    if not result:
        return render_template('tpx_gui.html',data=result,page_header=page_header,
                            instrument=instr,year=int(year),month=int(month),
                            staticyear=int(static_year),staticmonth=int(static_month),
                            staticday=int(static_day),day=int(day),table=table)
    else:
	    #if koatpx database    
	    if table=='koatpx':
	    	#for each dictionary
	        for d in result:
	            #for key and value in dictionary item
	            for k, v in d.items():
	                #if value is None or N/A, do not populate cell
	                if (v is None) or (v == "N/A"):
	                    d[k] = ""
	            #add line break for Level 1 Done
	            if d["lev1_done"]:
	                d["lev1_done"] = 'DONE<br>'+d["lev1_done"].strftime("%Y%m%d %H:%M")
	            #add line break for DRP Sent
	            if d["drpSent"]:
	                d["drpSent"] = 'DONE<br>'+d["drpSent"]
	            #if file size exists, convert MB -> GB, round to 1/100ths place
	            if d["size"]:
	                d["size"] /= 1000.
	                d["size"] = round(d["size"],2)
	            #if On Disk Time exists
	            if d["ondisk_time"]:
	                #but On Disk Status does not
	                if d["ondisk_stat"] != 'DONE':
	                	#set On Disk Status to done
	                   d["ondisk_stat"] = 'DONE'
	           	#if Archive Time exists
	            if d["arch_time"]:
	                #but Archive Status does not
	                if d["arch_stat"] != 'DONE':
	                    #set Archive Status to done
	                    d["arch_stat"] = 'DONE'
	    #if koadrp database
	    else:
	        #for each dictionary
	        for d in result:
	            #for key and value in dictionary item
	            for k, v in d.items():
	                #if value is None or N/A, do not populate cell
	                if (v is None) or (v == "N/A"):
	                    d[k] = ""
	    #if data exists, render template to populate cells
	    return render_template('tpx_gui.html',data=result,page_header=page_header,
	                            instrument=instr,year=int(year),month=int(month),
	                            staticyear=int(static_year),day=int(day),
	                            table=table)
