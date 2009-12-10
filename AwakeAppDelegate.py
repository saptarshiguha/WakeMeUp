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
from WakeMeUp import Waka
import objc
objc.setVerbose(True)
import datetime
import os
from Utility import *

class AwakeAppDelegate(NSObject):
    logcontroller = objc.ivar(u"logcontroller")
    def awakeFromNib(self):
        self.awakelog = AwakeLog.alloc().initWithInfo_Logger( {'filename':__name__},self.logcontroller)
        
        self.awakelog.info("Awake did finish launching.")
        self.cfgfile = NSHomeDirectory()+os.path.sep+".wakeuprc"
        self.awakelog.info("Using the following wakeupfile:"+self.cfgfile)
        self.waka = Waka.alloc().init()
        self.waka.setConfig(self.cfgfile)
        self.waka.schedule()
        self.notifyfromsleep()
        self.setAlarmForNextDay() #added once, does it have to added again?
    def applicationDidFinishLaunching_(self, sender):
        if self.waka.getEnv().get(HOOKS['ONFINISHLAUNCH'],None):
            self.waka.getEnv()[HOOKS['ONFINISHLAUNCH']](sender)

    def cancelAllPerforms(self):
        # NSObject.cancelPreviousPerformRequestsWithTarget_(self.waka)
        self.waka.cancelRequests()
        NSObject.cancelPreviousPerformRequestsWithTarget_(self)

    def setAlarmForNextDay(self):
        v = datetime.datetime.today()
        delta= datetime.timedelta(days=1)
        tgt = (v+delta).replace(hour=0,minute=1,second=1)
        sec= (tgt-v).seconds
        self.awakelog.info("Set reload alarm for:"+str(tgt))
        self.performSelector_withObject_afterDelay_("refreshme",None,sec)
    def refreshme(self):
        self.awakelog.info("A new day has started, let's reload")
        self.reload_(None)
    def notifyfromsleep(self):
        nc = NSWorkspace.sharedWorkspace().notificationCenter()
        nc.addObserver_selector_name_object_(
            self,"receiveWakeNote:",NSWorkspaceDidWakeNotification,None)
    def applicationShouldTerminate_(self,sender):
        self.awakelog.info("Quiting Awake")
        self.waka.stopCurrentRunning((2,sender))
        if(self.waka.getEnv().get(HOOKS['ONQUIT'],None)):
           self.waka.getEnv()[HOOKS['ONQUIT']](sender)
        return True
    def stop_(self,sender):
        self.awakelog.info("Stopping Currently Playing Music")
        if(not type(sender)==tuple):
            self.waka.stopCurrentRunning((-1,sender))
        else:
            self.waka.stopCurrentRunning(sender)
    def reload_(self,sender):
        self.awakelog.info("Reloading rc file")
        if(self.waka.getEnv().get(HOOKS['ONRELOAD'],None)):
           self.waka.getEnv()[HOOKS['ONRELOAD']](sender)
        self.cancelAllPerforms()
        self.waka.setConfig(self.cfgfile,True)
        self.waka.schedule()
        self.setAlarmForNextDay()
        
    def receiveWakeNote_(self,note):
        self.awakelog.info("Awoke from sleep, Awake is awoken:)")
        if(self.waka.getEnv().get(HOOKS['ONAWAKE'],None)):
           self.waka.getEnv()[HOOKS['ONAWAKE']](note)
        self.stop_((1,None))
        self.reload_(None)

    def snooze_(self,sender):
        self.waka.snooze()
