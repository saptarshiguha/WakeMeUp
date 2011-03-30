##    WakeMeUp - Highly Configurable Alarm Clock for OS X
##    Copyright (C) 2009, Saptarshi Guha, saptarshi.guha@gmail.com
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from Foundation import *
from AppKit import *
import objc
objc.setVerbose(True)
from PyObjCTools import AppHelper
import os
from Configurator import Configurator
import traceback
from Utility import *

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

class Administration(NSObject):
    def setConfig(self,config,rnargs=None):
        self.config = Configurator(config)
        self.config.parseConfig()
        if not rnargs:
            self.running=None
        self.srtd=[]
        self.awakelog = AwakeLog.alloc().initWithInfo_Logger( {'filename':__name__})
    def play_string(self, stri):
        resstring = ""
        try:
            import StringIO
            outlog = StringIO.StringIO()
            AwakeLog.toanotherhandle = outlog
            x= self.config.parseConfig(stri)
            if not x==None:
                resstring = "%s\n%s" % (x, outlog.getValue())
                outlog.close()
            else:
                self.srtd = []
                self.schedule()
        finally:
            AwakeLog.toanotherhandle = None
        resstring = outlog.getValue()
        outlog.close()
        return resstring
        ## return a success string
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
        NSObject.cancelPreviousPerformRequestsWithTarget_(self)
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
        self.awakelog.info("Will play %s" % p.title)
        self.stopCurrentRunning()
        self.running = p
        self.running.start()
        
    def scheduleWakeup(self,plyr):
        import datetime
        current_time =  datetime.datetime.today()
        timedelta = (plyr.wake_time - current_time).seconds
        self.performSelector_withObject_afterDelay_("runPlayer",plyr,timedelta)

    def scheduleOne(self,one):
        two = self.config.singleWakeUp(one)
        self.scheduleWakeup(two)
        return str(two)
    def schedule(self):
        self.srtd = self.config.getWakeups()
        self.srtd.sort(key=lambda x: x.wake_time)
        for i in self.srtd:
            self.scheduleWakeup(i)

