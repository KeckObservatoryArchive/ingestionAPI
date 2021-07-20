
'''
This code is called when a return response from IPAC is recieved notifying Keck that data has been 
successfully ingested into KOA.  We can then send a notification email to the PI

Adapted from:
  koaserver:/kroot/archive/tpx/default/tpx_email.php
  koaserver:/kroot/archive/bin/dep_pi_email.php
  koaserver:/kroot/archive/bin/dep_pi_email_send.php

For full night ingestion, this response will contain the date and instrument. 
We need to email all programs that were marked in koapi_send table by DQA for this date as needing notificaiton.
For non-ToO programs, we will cross check with the tel schedule.
'''
from datetime import datetime, timedelta
import db_conn
import urllib.request as URL
import time
import json


#map any instrument names to base name for easy query searching (ie 'nirspec' should search on '%nirsp%')
instrBase = {
    'nirspec': 'nirsp'
}


def dep_pi_email(instr, utdate, level, dev=False):

    instr = instr.lower()

    #We are only dealing with level 0 for now
    if level > 0:
        return False, "ERROR: PI emails only sent for level 0 ingestion"

    #check proc date is not too old
    utdatets = datetime.strptime(utdate, '%Y-%m-%d')
    diff = datetime.now() - utdatets
    if diff.days > 7:
       return False, "ERROR: Processing date is more than 7 days ago"

    #db object
    config_key = 'database_dev' if dev else 'database'
    db = db_conn.db_conn('config.live.ini', configKey=config_key)

    #Find all programs on this utdate and instr that are are still needing notification sent
    #NOTE: PIs will not get notified if there is a hiccup where we don't get the IPAC reciept that day.
    errors = []
    num_sent = 0
    rows = db.query("koa", f"select * from koapi_send where utdate_beg='{utdate}' and instr='{instr}' and send_data=1 and data_notified=0")
    for row in rows:
        semid = row['semid']
        semester, progid = semid.split('_')

        #get program info
        query = f"select pi.*, pr.type from koa_pi as pi, koa_program as pr where pi.piID=pr.piID and pr.semid='{semid}'"
        prog_info = db.query("koa", query, getOne=True)
        if not prog_info:
            errors.append(f'ERROR: Could not find program information for {semid}')
            continue

        #Ensure that it was scheduled for this day (does not apply to ToOs)
        if prog_info['type'] != 'ToO':
            yester = get_delta_date(utdate, -1)
            shortinstr = instrBase.get(instr, instr)
            query = f"select * from telSchedule where Instrument like '%{shortinstr}%' and Date='{yester}' and ProjCode like '%{progid}%'"
            sched = db.query("keckOperations", query, getOne=True)
            if not sched:
                errors.append(f'ERROR: Program {semid} was not scheduled on HST date {yester}')
                continue

        #check for a matching koatpx processed record from koa table and that its metadata_time2 val is set
        #NOTE: Old code looked at metadata_time2, but we are looking at tpx_stat now.
        koatpx = db.query("koa", f"select * from koatpx where utdate='{utdate}' and instr='{instr}' and tpx_stat='DONE'")
        if len(koatpx) == 0: 
            errors.append(f'ERROR: Could not find matching koatpx processed record for utdate {utdate} and instr {instr}')
            continue

        #get needed PI info for this program
        #NOTE: old method gets info from kpa_pi and koa_program.  This is getting from proposal API.
        pp, pp1, pp2, pp3 = get_propint_data(utdate, semid, instr)
        email = getPIEmail(semid)
        if not email:
            errors.append(f'ERROR: Could not get PI info for {semid}')
            continue

        #send email
        to = email
        frm = 'koaadmin@keck.hawaii.edu'
        bcc = 'koaadmin@keck.hawaii.edu'
        subject = f"The archiving and future release of your {instr} data";
        if dev: 
            to = 'jriley@keck.hawaii.edu'
            bcc = ''
            subject = '[TEST] ' + subject
        msg = get_pi_send_msg(instr, semester, progid, pp, pp1, pp2, pp3)
        try:
           send_email(to, frm, subject, msg, bcc=bcc)
        except Exception as e:
            errors.append(f'ERROR: could not send email: {str(e)}')

        #update koapi_send db table
        if not dev:
            query = f"update koapi_send set data_notified=1, dvd_notified=1 where semid='{semid}' and utdate_beg='{utdate}'"
            res = db.query("koa", query)
            if not res:
                errors.append(f'ERROR: Could not update koapi_send for {semid}')
                continue

        #safe guard upper limit on how many notifications can go out
        #NOTE: This used to be set at 2.  But since we will be adding ToOs and Twilight, this is getting bumped up.
        num_sent += 1
        if num_sent > 9: 
            errors.append(f'ERROR: Too many email notifications!')
            break
        time.sleep(1)

    #result
    if len(errors) > 0:
        return False, json.dumps(errors)
    else:
        return True, None


def get_delta_date(datestr, delta):
    date = datetime.strptime(datestr, "%Y-%m-%d")
    newdate = date + timedelta(days=delta)
    return datetime.strftime(newdate, "%Y-%m-%d")        


def get_propint_data(utdate, semid, instr):

    instr = instr.upper()

    #try koa_ppp first
    db = db_conn.db_conn('config.live.ini', configKey='database')
    ppdata = db.query("koa", f"select * from koa_ppp where utdate='{utdate}' and semid='{semid}'", getOne=True)
    if ppdata:
        pp = ''
        pp1 = ppdata['propint1']
        pp2 = ppdata['propint2']
        pp3 = ppdata['propint3']
        if (pp1 == pp2 and pp2 == pp3) or instr != "HIRES":
            pp = pp1
        return pp, pp1, pp2, pp3

    #else try proposals api
    if not ppdata:
        baseurl = 'https://www.keck.hawaii.edu/software/db_api/'
        url = f'{baseurl}proposalsAPI.php?ktn={semid}&cmd=getApprovedPP'
        try:
            result = URL.urlopen(url).read().decode('utf-8')
            result = json.loads(result)
            pp = result['data']['ProprietaryPeriod']
            return pp, pp, pp, pp
        except Exception as e:
            print(f'could not open url: {str(e)}')

    #else give up
    return '', '', '', ''


def getPIEmail (semid):
#TODO: use common function
    baseurl = 'https://www.keck.hawaii.edu/software/db_api/'
    url = f'{baseurl}proposalsAPI.php?ktn={semid}&cmd=getPIEmail'
    try:
        result = URL.urlopen(url).read().decode('utf-8')
        result = json.loads(result)
        email = result['data']['Email']
        return email
    except Exception as e:
        print(f'ERROR: could not get email from API call {url}: {str(e)}')
        return None


def get_pi_send_msg(instr, semester, progid, pp, pp1, pp2, pp3):

    instr = instr.upper()

    msg = f"Dear {instr} program PI,\n\n";
    msg += f"Your {instr} data for\n\n";
    msg += f"Semester: {semester}\n";
    msg += f"Program: {progid}\n\n";
    msg += f"have been archived.  The proprietary period for your program, as approved by\n";
    msg += f"your Selecting Official, is\n\n";
    if pp or instr != "HIRES":
        msg += f"{pp} months\n\n";
    else:
        msg += f"CCD1 = {pp1} months\n";
        msg += f"CCD2 = {pp2} months\n";
        msg += f"CCD3 = {pp3} months\n\n";
    msg += f"from the date of observation, after which the data will be made public via\n";
    msg += f"KOA.  Policy details can be found at\n";
    msg += f"http://www2.keck.hawaii.edu/koa/public/KOA_data_policy.pdf.";
    msg += f"\n\n";
    msg += f"If the proprietary period shown below is not what you expect, please\n";
    msg += f"contact your current Selecting Official.  The most up-to-date list\n";
    msg += f"of Selecting Officials can be found at\n";
    msg += f"http://www2.keck.hawaii.edu/koa/public/soList.html\n\n";

    msg += f"To access your proprietary data, visit the password-protected\n";
    msg += f"KOA User Interface (UI) at\n\n";
    msg += f"http://koa.ipac.caltech.edu\n\n";

    msg += f"If you have forgotten your username or password, or if you would like\n";
    msg += f"to allow your Co-Is access to this program, please submit your request\n";
    msg += f"using the form located at\n\n";

    msg += f"https://koa.ipac.caltech.edu/applications/Helpdesk\n\n";

    msg += f"Provide the program ID and the names and email addresses of the\n";
    msg += f"Co-Is.\n\n";

    msg += f"We encourage you to use the KOA to access your data, and we\n";
    msg += f"welcome any comments and suggestions for improving the archive\n\n";

    msg += f"About KOA:\n";
    msg += f"Funded by NASA, KOA is a collaborative effort between the W. M.\n";
    msg += f"Keck Observatory and the NASA Exoplanet Science Institute (NExScI)\n";
    msg += f"to build, operate and maintain a data archive for Keck Observatory.\n\n";

    msg += f"For more information about KOA, please visit\n\n";
    msg += f"http://www2.keck.hawaii.edu/koa/public/koa.php\n\n";

    msg += f"Check back regularly for news and updates as they become available.\n\n";
    msg += f"Sincerely,\n\n";
    msg += f"The Keck Observatory Archive\n";
    msg += f"koaadmin@keck.hawaii.edu";

    return msg


def send_email(to_email, from_email, subject, message, cc=None, bcc=None):
    '''
    Sends email using the input parameters
    '''
    import smtplib
    from email.mime.text import MIMEText

    # Construct email message
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['To'] = to_email
    msg['From'] = from_email
    if cc: msg['Cc'] = cc
    if bcc: msg['Bcc'] = bcc

    # Send the email
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

