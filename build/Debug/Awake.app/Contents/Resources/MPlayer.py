## A class for players
from Foundation import *
from AppKit import *
import objc
objc.setVerbose(True)
from PyObjCTools import AppHelper
import traceback
import os
from  Utility import *
import Player
import time
from Foundation import *
from AppKit import *
from objc import *



class MPlayer(Player.Player):
    cdesc = 'MPlayer'
    def initWithValue_(self,value):
        self = super(MPlayer, self).initWithValue_(value)
        if self is None: return None
        self.runner=None
        self.awakelog = AwakeLog.alloc().initWithInfo_( {'filename':__name__})
        return self
    def start(self, args,xtras=None):
        self.setMplayerBin(self.info.get("mplayer_opt",{}))
        self.createTask(args)
    def stop(self,args=None,xtras=None):
        if not self.runner:
            pass
        else:
            if self.runner and self.runner.isRunning():
                self.sendCommand("quit")
                self.runner.waitUntilExit()
    def volume_set(self,vol):
        if self.runner and self.runner.isRunning():
            self.sendCommand("volume %d 1" % int(vol))
    def volume(self,args):
        return 0
    def setMplayerBin(self,cmd):
        if type(cmd)!=dict:
            raise ValueError("mplayer_opt must be a dictionary")
        self.cmd = [cmd.get('bin','/opt/local/bin/mplayer'),'-slave','-quiet']
        if cmd.has_key('opt') and not (type(cmd['opt'])==list or type(cmd['opt'])==tuple):
            raise ValueError('the opt key in mplayer_opt must be tuple or list')
        for x in cmd.get('opt',[]):
            self.cmd.extend([x,])
    def createTask(self,url):
        url=url.split(" ")
        self.cmd.extend(url)
        self.runner= NSTask.alloc().init()
	self.runner.setStandardInput_(NSPipe.pipe())
	self.runner.setStandardOutput_(NSPipe.pipe())
	self.runner.setStandardError_(NSPipe.pipe())
        self.parseRunLoopModes = (NSDefaultRunLoopMode,)
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self,
            self.mplayerTerminated,
            NSTaskDidTerminateNotification,
	    self.runner)
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self,
            self.readOutputC,
            NSFileHandleReadCompletionNotification,
	    self.runner.standardOutput().fileHandleForReading())
        NSNotificationCenter.defaultCenter().addObserver_selector_name_object_(
            self,
            self.readError,
            NSFileHandleReadCompletionNotification,
	    self.runner.standardError().fileHandleForReading())
        self.runner.setLaunchPath_(self.cmd[0])
        self.runner.setArguments_(self.cmd[1:])
        aenv = NSProcessInfo.processInfo().environment().mutableCopy()
        aenv["DYLD_BIND_AT_LAUNCH"] = "1"
        self.runner.setEnvironment_( aenv)
        self.runner.standardOutput().fileHandleForReading().readInBackgroundAndNotifyForModes_(self.parseRunLoopModes)
        self.runner.standardError().fileHandleForReading().readInBackgroundAndNotifyForModes_(self.parseRunLoopModes)
        self.isrunning = True
        self.runner.launch()
        # time.sleep(2)
        self.volume_set(0)
        # self.sendCommand("loadfile %s\n" % str(url))
    def mplayerTerminated(self):
        if self.isrunning:
            NSNotificationCenter.defaultCenter().removeObserver_name_object_(self,NSTaskDidTerminateNotification,self.runner)
            self.isrunning = False
        returncode = self.runner.terminationStatus()
        self.awakelog.info("mplayer terminated with %d" % returncode)
        
    def readError(self,notif):
        data = notif.userInfo()['NSFileHandleNotificationDataItem']
        if (self.runner.isRunning() or( data and len(data)>0)):
            self.runner.standardError().fileHandleForReading().readInBackgroundAndNotifyForModes_(self.parseRunLoopModes)
        for l in str(data).split("\n"):
            self.awakelog.info("MPlayer ERR:"+str(l))
    def readOutputC(self, notif):
        data = notif.userInfo()['NSFileHandleNotificationDataItem']
        if (self.runner.isRunning() or( data and len(data)>0)):
            self.runner.standardOutput().fileHandleForReading().readInBackgroundAndNotifyForModes_(self.parseRunLoopModes)
        if data:
            data=str(data).strip()
            if data.lower().find("name")>0 or data.lower().startswith("genre") or data.lower().startswith("website") or data.lower().find("author")>0:
                for l in str(data).split("\n"):
                    self.awakelog.info("MPlayer:"+str(l))
            elif data.startswith("ICY"):
                for l in str(data).split("\n"):
                    self.awakelog.info("MPlayer:"+str(l))
            elif data.find("Clip Info")>=0:
                self.awakelog.info(data)
            elif data.startswith("A:") or data.startswith("V:"):
                pass
            elif data.find("Quit")>0 or data.find("Exit")>0 or data.find("End of file")>0 or data.find("EOF")>0:
                self.awakelog.info("Cocoa sent a message and we must quit")
                NSNotificationCenter.defaultCenter().removeObserver_name_object_(self,NSFileHandleReadCompletionNotification,self.runner.standardOutput().fileHandleForReading())
                NSNotificationCenter.defaultCenter().removeObserver_name_object_(self,NSFileHandleReadCompletionNotification,self.runner.standardError().fileHandleForReading())
            else:
                # print "OC:"+(str(data))
                pass
                
    def sendCommand(self, cmd):
        cmd = "%s\n" % cmd
        if self.runner and self.runner.isRunning():
            tp = self.runner.standardInput().fileHandleForWriting()
            dta = NSData.alloc().initWithBytes_length_(cmd, len(cmd))
            tp.writeData_(dta)
    def __str__(self):
        return "Mplayer"

