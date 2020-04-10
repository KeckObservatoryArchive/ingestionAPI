
'''
This code is called when a return response from IPAC is recieved notifying Keck that data has been 
successfully ingested into KOA.  

For full night ingestion, this response will contain the date and instrument. 
Given a date and instr, we need to email all programs that were scheduled on that instrument for that date.  
This is problematic for ToOs and Twilight b/c they are not on the schedule.  
One solution would be to add instrument column to koapi_send.  Then we don't need to cross-reference the schedule.

NOTE: The following koatpx vars are updated via IPAC receipt procmail before email code is called:

system("/kroot/archive/bin/mysql_tpx_update $utdate $instrument metadata_time2 '$time'");
system("/kroot/archive/bin/mysql_tpx_update $utdate $instrument tpx_stat DONE");
system("/kroot/archive/bin/mysql_tpx_update $utdate $instrument tpx_time '$time'");
if ($type == "nirc2" || $type == "osiris")
{
        system("/kroot/archive/bin/mysql_tpx_update $utdate $instrument lev1_stat DONE");
        system("/kroot/archive/bin/mysql_tpx_update $utdate $instrument lev1_time '$time'");
}

'''
from datetime import datetime, timedelta



#-----------------------------------------------------------------------------------------------------------------
# CURRENT METHOD (no koapi_send.instr column, considers runs):
# Ported from koaserver:/kroot/archive/bin/dep_pi_email.php
# NOTE: If we don't care about runs, and want to send a notification each day, nothing changes here.  We just put
# more entries in koapi_send for each date.  See updateKoapiSend in koa_api.py 
#-----------------------------------------------------------------------------------------------------------------
def dep_pi_email_OLD(instr, utdate):

    #Get yesterday date string
    hstdate = get_delta_date(utdate, '-1 days')
    hstdate = datetime.strptime(utdate, '%Y-%m-%d') - timedelta(1)
    hstdate = hstdate.strftime("%Y-%m-%d")

    #Find all programs on this utdate that are are still needing notification sent
    #NOTE: PIs will not get notified if there is a hiccup where we don't get the IPAC reciept that day.
    rows = query("koa", f"select * from koapi_send where utdate_beg='{utdate}' and send_data=1 and data_notified=0")

    #For each program, cross-reference it in the schedule (using hstdate of course)
    #NOTE: If a program takes data that was not on the schedule, they will not get notified.
    num_sent = 0
    for row in rows:

        #safe guard upper limit on how many notifications can go out
        if num_sent > 3: 
            continue

        #check for matching sched prog
        #NOTE: fixing bug here where check failed if program was scheduled twice in one night on same instr
        pcode = row[semid]
        progs = query("keckOperations", f"select * from telSchedule where Instrument like '%{instr}%' and Date='{hstdate}' and ProjCode like '%{pcode}%'")
        if len(progs) == 0: 
            continue

        #check for a matching processed record from koa table
        utdate_beg = row['utdate_beg']
        koatpx = query("koa", select * from koatpx where utdate='{utdate_beg}' and instr='{instr}'")
        if len(koatpx) == 0: 
            continue

        #check that metadata_time2 has a value
        #TODO: NOTE: metadata_time2 is set by the root procmail script that calls this one
        if not koatpx[0]['metadata_time2']:
            continue

        #gather info for this program from koa tables
        info = query("koa", f"select pi.* from koa_pi as pi, koa_program as pr where pi.piID = pr.piID and pr.semid='{pcode}'")
        if len(info) != 1:
            continue

        #send email
        info = info[0]
        dep_pi_email_send(utdate, instr, info[semid], 
                          info[pi_lastname], info[pi_firstname], info[pi_email], 
                          info[pi_username], info[pi_password])

        #update koapi_send
        query(f"update koapi_send set data_notified=1,dvd_notified=1 where semid='{pcode}' and utdate_beg='{utdate}'")
        sleep(1)
        num_sent += 1



#-----------------------------------------------------------------------------------------------------------------
# NEW METHOD (has koapi_send.instr column, does not consider runs):
# TODO: Script that calls this needs to set metadata_time2, tpx_stat, and tpx_time
# TODO: Add koapi_send.instr column
# TODO: Update dep_dqa.py to pass instr to koa_api.updateKoapiSend
# TODO: Update koa_api.updateKoapiSend to insert into new instrument col
# TODO: (optional) Update koa_api.updateKoapiSend to forget about runs and insert a record for every night per program per instrument. 
# TODO: Does all this work for ToOs and Twilight?
#-----------------------------------------------------------------------------------------------------------------
def dep_pi_email(instr, utdate):

    #Get yesterday date string
    hstdate = get_delta_date(utdate, '-1 days')
    hstdate = datetime.strptime(utdate, '%Y-%m-%d') - timedelta(1)
    hstdate = hstdate.strftime("%Y-%m-%d")

    #Find all programs on this utdate and instr that are are still needing notification sent
    #NOTE: PIs will not get notified if there is a hiccup where we don't get the IPAC reciept that day.
    num_sent = 0
    rows = query("koa", f"select * from koapi_send where utdate_beg='{utdate}' and instr='{instr}' and send_data=1 and data_notified=0")
    for row in rows:
        semid = row['semid']

        #check for a matching koatpx processed record from koa table and that its metadata_time2 val is set
        #TODO: NOTE: metadata_time2 is set by the root procmail script that calls this one
        koatpx = query("koa", f"select * from koatpx where utdate='{utdate}' and instr='{instr}' and metadata_time2 not null")
        if len(koatpx) == 0: 
            log('ERROR: ???')
            continue

        #get needed PI info for this program
        #NOTE: old method gets info from kpa_pi and koa_program.  This is getting from proposal API.
        semester, progid = semid.split('_')
        pp, pp1, pp2, pp3 = getPropintData(utdate, semid)
        email = getPIEmail(semid)
        if not email:
            log('ERROR: ???')
            continue

        #send email
        to = email
        frm = 'koaadmin@keck.hawaii.edu'
        bcc = 'koaadmin@keck.hawaii.edu'
        subject = f"The archiving and future release of your {instr} data";
        msg = get_pi_send_msg(instr, semester, progid, pp, pp1, pp2, pp3)
        send_email(to, frm, subject, msg, bcc=bcc)

        #update koapi_send db table
        query("koa", f"update koapi_send set data_notified=1, dvd_notified=1 where semid='{semid}' and utdate_beg='{utdate}'")

        #safe guard upper limit on how many notifications can go out
        #NOTE: This used to be set at 2.  But since we will be adding ToOs and Twilight, this is getting bumped up.
        num_sent += 1
        if num_sent > 9: 
            log('ERROR: ???')
            break
        sleep(1)


def getPropintData(utdate, semid):

    ppdata = query("koa", f"select * from koa_ppp where utdate='{utdate}' and semid='{semid}'")
    if not ppdata:
        return '', '', '', ''

    pp = ''
    pp1 = ppdata['propint1']
    pp2 = ppdata['propint2']
    pp3 = ppdata['propint3']
    if (pp1 == pp2 and pp2 == pp3) or instr != "HIRES":
        pp = pp1;
    return pp, pp1, pp2, pp3


def get_pi_send_msg(instr, semester, progid, pp, pp1, pp2, pp3):

    msg = f"Dear {instr} program PI,\n\n";
    msg += f"Your {instr} data for\n\n";
    msg += f"Semester: {semester}\n";
    msg += f"Program: {progid}\n\n";
    msg += f"have been archived.  The proprietary period for your program, as approved by\n";
    msg += f"your Selecting Official, is\n\n";
    if pp || instr != "HIRES":
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


def send_email(toEmail, fromEmail, subject, message, cc=None, bcc=None):
    '''
    Sends email using the input parameters
    '''
    import smtplib
    from email.mime.text import MIMEText

    # Construct email message
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['To'] = toEmail
    msg['From'] = fromEmail
    if cc: msg['Cc'] = cc
    if bcc: msg['Bcc'] = bcc

    # Send the email
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()