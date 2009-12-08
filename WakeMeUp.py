from Foundation import *
from AppKit import *
import objc
objc.setVerbose(True)
from PyObjCTools import AppHelper
import os
from Configurator import Configurator
import traceback
from Utility import HOOKS
#def sbapp(name):
#    workspace=NSWorkspace.sharedWorkspace()
#    path = workspace.fullPathForApplication_(name)
#    if path:
#        x = path.stringByAppendingPathComponent_("Contents/Info.plist")
#        infoplist = NSDictionary.dictionaryWithContentsOfFile_(x)
#        z= infoplist.objectForKey_("CFBundleIdentifier")
#        return SBApplication.applicationWithBundleIdentifier_(z)


##This is not designed to be multi threaded
##If two wakeups occur at same time?
##I have no idea what happens

class Waka(NSObject):
    def setConfig(self,config,rnargs=None):
        self.config = Configurator(config)
        self.config.parseConfig()
        if not rnargs:
            self.running=None
        self.srtd=[]
    def stopCurrentRunning(self,info=None):
        if self.running:
            self.running.stop(info)
            self.running = None
    def getEnv(self):
        return self.config.getEnv()
    
    def cancelRequests(self):
        for i in self.srtd:
            if i:
                i.cancel()
        if self.running:
            self.running.cancel()
    def snooze(self):
        if self.running:
            self.running.stop({'snooze':True})
            if self.getEnv().get(HOOKS['ONSNOOZE'],None):
                self.getEnv()[HOOKS['ONSNOOZE']](self.running)
            snooze_time = self.getEnv().get(HOOKS['SNOOZETIME'],15)
            self.performSelector_withObject_afterDelay_("snoozeOff",self.running,snooze_time)
    def snoozeOff(self,p):
        self.stopCurrentRunning()
        self.running = p
        self.running.fadein['dur']=float(15)
        self.running.start()
    def runPlayer(self, p):
        self.stopCurrentRunning()
        self.running = p
        self.running.start()
        
    def scheduleWakeup(self,plyr):
        import datetime
        current_time =  datetime.datetime.today()
        timedelta = (plyr.wake_time - current_time).seconds
        self.performSelector_withObject_afterDelay_("runPlayer",plyr,timedelta)
        
    def schedule(self):
        self.srtd = self.config.getWakeups()
        self.srtd.sort(key=lambda x: x.wake_time)
        for i in self.srtd:
            self.scheduleWakeup(i)

