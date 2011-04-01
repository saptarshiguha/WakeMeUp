#!/usr/bin/python
import time,os,email,re
## We are just going to look at emails in last 1 minute which would
## roughly correspond to recent emails ideally i would record the time
## in pre-sync and post-sync and find emails in between
SERVERPORT = 8080
MAILDIR = ("/Users/yanger/MyMail/.songrequest/cur/",)#,"/Users/sguha/MozMail/INBOX/new/")
# MAILDIR=("/Users/sguha/MozMail/INBOX/new/",)
TIMEWINDOW = 60
def checkValidTo(msg):
    to=email.Utils.parseaddr(msg['To'])[1]
    fro=email.Utils.parseaddr(msg['From'])[1]
    code =  to == "saptarshi.guha+play@gmail.com" and fro=="saptarshi.guha@gmail.com"
    if(not code):
        print "Rejected %s:%s" %(to,fro)
    return code

    # return to == "sguha+play@mozilla.com"
gmail_name,gmail_pass = [x.strip() for x in open("/Users/yanger/mystuff/conf/sec","r").readlines()]
def mailViaGmail(to, subject, text,attach=None,gmailuser=gmail_name, gmailpwd=gmail_pass):
    try:
        import smtplib
        from email.MIMEMultipart import MIMEMultipart
        from email.MIMEBase import MIMEBase
        from email.MIMEText import MIMEText
        from email import Encoders
        import os,glob,sys
        msg = MIMEMultipart()
        msg['From'] = gmailuser
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(text))
        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmailuser, gmailpwd)
        mailServer.sendmail(gmailuser, to, msg.as_string())
        mailServer.close()
        return True
    except:
        import sys
        sys.stderr.write("GMAIL ERROR:\n")
        import traceback
        traceback.print_exc()
        return False

## if subject is info, just reply with conf file
## First line is music e.g. 'KCRW...' no quotes, can be preceded with a 'play'
## after that (if quotes, must be first word on sentence):
## time ... e.g. in 5 minutes, at 7:00 pm today
## {'stop','dur','duration'} and then a time  to stop at time
## {minvol,volmin,min}[SPACE]#
## {maxvol, volmax, max}[SPACE]#
## {fadein}[SPACE]#

def read_body(subject,lines):
    try:
        results = {'error':False,'info':False,'max':80,'min':0,'when':'in 30 minutes','stop':False}
        if subject.lower().find("info")>=0 or subject.lower().find("help")>=0:
            results['info']=True
            return results
        if subject.lower().find("stop")>=0 or subject.lower().find("kill")>=0:
            results['stop'] = True
            return results
        results['natural'] = lines[0].strip()
        for c in lines[1:]:
            c=c.lower()
            if c.startswith("#"):
                next
            c = c.strip()
            if c.startswith("maxvol") or c.startswith("volmax") or c.startswith("max"):
                results['max'] = str(re.split(" ",c,1)[1])
            elif c.startswith("minvol") or c.startswith("volmin") or c.startswith("min"):
                        results['min'] = str(re.split(" ",c,1)[1])
            elif c.startswith("dur") or c.startswith("fade"):
                results['dur'] = str(eval(re.split(" ",c,1)[1]))
            else:
                pass
    except Exception:
        import traceback
        return {'error':True,'errordoc':traceback.format_exc()}
    return results

def getData(sock):
    data = sock.recv(1024)
    string = ""
    while len(data):
        string = string + data
        data = sock.recv(1024)
    return string
def send_message_to_server(result):
    import socket,sys
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', SERVERPORT))
    if result['info']:
        sock.send('info')
        string = getData(sock)
        sock.close()
        return string
    elif result['stop']:
        sock.send('stop')
        string = getData(sock)
        sock.close()
        return string
    else:
        x="play %(natural)s\n%(min)s\n%(max)s\n" % result
        if result.get('dur',None)!=None:
            x="%s%s" % (x, result['dur'])
        sock.send(x)
        string = getData(sock)
        sock.close()
        return string
def main():
    new_dir = MAILDIR
    recent_window = TIMEWINDOW
    curr_time = time.time()
    old=set([])
    for n in new_dir:
        recent_emails = set.union(old,set([ n+x for x in os.listdir(n) if (curr_time- os.path.getctime(n+x)) < recent_window]))
    recent_emails = list(recent_emails)
    for x in recent_emails:
        # print x
## Scan emails to see which one is to saptarshi.guha+playmusic@gmail.com
        x=open(x,'r')
        p=email.Parser.Parser()
        msg=p.parse(x)
        to_address = email.Utils.parseaddr(msg['To'])[1]
        subject = msg['Subject']
        if checkValidTo(msg):
            print "Found a valid song request message: %s" % subject
            body= msg.get_payload()
            result = read_body(subject, body.split("\n"))
            if not result['error']:
                res,resp = send_message_to_server(result).split(" ",1)
                if msg['Reply-To']:
                    to = msg['Reply-To']
                else:
                    to = msg['From']
                mailViaGmail(to,"Play-Info:%s" % res,resp)
            else:
                mailViaGmail(to,"Play-Info:Error",result['errordoc'])
        else:
            print "Ignored message with subject %s" % subject

if __name__ == "__main__":
    main()
