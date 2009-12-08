## A class for players
from Foundation import *
from AppKit import *
import objc
from PyObjCTools import AppHelper
import traceback
import os
from Utility import *
import Player

from Foundation import *
from AppKit import *
from objc import *

class Foom(Player.Player):
    def start(self, args,xtras):
        self.setMplayerBin()
        self.createTask(args)
    def stop(self,args,xtras):
        if not self.runner:
            pass
        else:
            if self.runner and self.runner.isRunning():
            self.sendCommand("quit")
            self.runner.waitUntilExit()
    def volume_set(self, vol):
        if self.runner.isRunning():
            self.sendCommand("volume %d 1" % int(vol))
    def volume(self,args):
        return 0
    def setMplayerBin(self):
        self.cmd_ = ["/opt/local/bin/mplayer", "-slave"]
    def createTask(self,url):
        url=url.split(" ")
        self.cmd = self.cmd_
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
    def mplayerTerminated(self):
        if self.isrunning:
            NSNotificationCenter.defaultCenter().removeObserver_name_object_(self,NSTaskDidTerminateNotification,self.runner)
            self.isrunning = False
        returncode = self.runner.terminationStatus()
        NSLog("mplayer terminated with %d" % returncode)
        
    def readError(self,notif):
        data = notif.userInfo()['NSFileHandleNotificationDataItem']
        if (self.runner.isRunning() or( data and len(data)>0)):
            self.runner.standardError().fileHandleForReading().readInBackgroundAndNotifyForModes_(self.parseRunLoopModes)
        NSLog("ERR:"+str(data))
    def readOutputC(self, notif):
        data = notif.userInfo()['NSFileHandleNotificationDataItem']
        if (self.runner.isRunning() or( data and len(data)>0)):
            self.runner.standardOutput().fileHandleForReading().readInBackgroundAndNotifyForModes_(self.parseRunLoopModes)
        if data:
            data=str(data).strip()
            if data.startswith("Name") or data.startswith("Genre") or data.startswith("Website"):
               NSLog(data)
            elif data.startswith("ICY"):
                NSLog(data)
            elif data.startswith("A:") or data.startswith("V:"):
                pass
            elif data.find("Quit")>0 or data.find("Exit")>0 or data.find("End of file")>0 or data.find("EOF")>0:
                NSLog("Cocoa sent a message and we must quit")
                NSNotificationCenter.defaultCenter().removeObserver_name_object_(self,NSFileHandleReadCompletionNotification,self.runner.standardOutput().fileHandleForReading())
                NSNotificationCenter.defaultCenter().removeObserver_name_object_(self,NSFileHandleReadCompletionNotification,self.runner.standardError().fileHandleForReading())
            else:
                print "wakeup_mplayer_OC:"+(str(data))
                
    def sendCommand(self, cmd):
        cmd = "%s\n" % cmd
        if self.runner and self.runner.isRunning():
            tp = self.runner.standardInput().fileHandleForWriting()
            dta = NSData.alloc().initWithBytes_length_(cmd, len(cmd))
            tp.writeData_(dta)
    def __str__(self):
        return "Mplayer"

