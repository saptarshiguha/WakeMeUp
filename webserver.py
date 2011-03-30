#Copyright Jon Berg , turtlemeat.com
from Foundation import *
from AppKit import *
from Administration import Administration
import objc
objc.setVerbose(True)
import sys
import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import traceback
from Utility import *
from socket import *      #im

class MyServer:
    def __init__(self, conffile, port,delegate):
        self.serv = socket( AF_INET,SOCK_STREAM)
        self.port = port
        self.serv.bind((('',self.port)))
        self.appdelegate = delegate
        self.awakelog = AwakeLog.alloc().initWithInfo_( {'filename':__name__})
    def startnow(self):
        self.awakelog.info("Will listen on %s" % str(self.port))
        while True:
            self.serv.listen(5)
            conn,addr = self.serv.accept()
            self.awakelog.info("Got a connection from %s" % str((addr)))
            request = conn.recv(1024*5).strip()
            if request == "info":
                self.awakelog.info("User wanted 'info'")
                conn.send("""OK 
## if subject is info/help, just reply with conf file
## First line is music e.g. 'play ['KCRW...'  as in natural parse
## {'stop','dur','duration'} and then a time  to stop at time
## {minvol,volmin,min}[SPACE]#
## {maxvol, volmax, max}[SPACE]#
## {fadein}[SPACE]# """ +"\n\n" + open(self.appdelegate.cfgfile,"r").read()+"\n")
            elif request.startswith("play"):
                pr = request.split(" ",1)[1]
                self.awakelog.info("User wanted to 'play' : %s" %pr)
                ## so bad in threadsafety ...
                self.appdelegate.performSelectorOnMainThread_withObject_waitUntilDone_("run_server_play",pr,True)
                result =self.appdelegate.last_status
                conn.send(result)
            elif request.startswith("stop"):
                self.appdelegate.performSelectorOnMainThread_withObject_waitUntilDone_("stop_server_play",None,True)
                result =self.appdelegate.last_status
                conn.send(result)
            else:
                conn.send("NOTOK Please don't send me rubbish: %s" % request)
            conn.close()
            self.awakelog.info("Processed Remote User Input")
class AwakeServer(NSObject):
    def initWithInfo_(self, info):
        self = super(AwakeServer, self).init()
        if self is None: return None
        self.server = MyServer(info[0],int(info[1]),info[2])
        return self
    def startnow(self):
        self.pool=NSAutoreleasePool.alloc().init()
        self.server.startnow()

