#
#  AwakeAppDelegate.py
#  Awake
#
#  Created by Saptarshi  Guha on 11/7/09.
#  Copyright __MyCompanyName__ 2009. All rights reserved.
#

from Foundation import *
from AppKit import *
from WakeMeUp import Waka
import datetime
import os

runonce = True
class AwakeAppDelegate(NSObject):
    cfgfile = "/Users/yanger/mystuff/wakemeup"
    finishlaunch = True
    def applicationDidFinishLaunching_(self, sender):
        global runonce
        NSLog("Awake did finish launching.")
        self.cfgfile = NSHomeDirectory()+os.path.sep+".wakeuprc"
        NSLog("Using the following wakeupfile:"+self.cfgfile)
        self.waka = Waka.alloc().init()
        self.waka.setConfig(self.cfgfile)
        self.waka.schedule()
        self.notifyfromsleep()
        self.setAlarmForNextDay() #added once, does it have to added again?


    def cancelAllPerforms(self):
        # NSObject.cancelPreviousPerformRequestsWithTarget_(self.waka)
        self.waka.cancelRequests()
        
    def setAlarmForNextDay(self):
        v = datetime.datetime.today()
        delta= datetime.timedelta(days=1)
        tgt = (v+delta).replace(hour=0,minute=1,second=1)
        sec= (tgt-v).seconds
        NSLog("Set reload alarm for:"+str(tgt))
        self.performSelector_withObject_afterDelay_("refreshme",None,sec)

    def refreshme(self):
        NSLog("A new day has started, let's reload")
        self.reload_(None)
    def notifyfromsleep(self):
        nc = NSWorkspace.sharedWorkspace().notificationCenter()
        nc.addObserver_selector_name_object_(
            self,"receiveWakeNote:",NSWorkspaceDidWakeNotification,None)
    def applicationShouldTerminate_(self,sender):
        NSLog("Quiting Awake")
        self.waka.stopCurrentRunning()
        return True
    def stop_(self,sender):
        NSLog("Stopping Currently Playing Music")
        self.waka.stopCurrentRunning()
    def reload_(self,sender):
        NSLog("Reloading rc file")
        self.cancelAllPerforms()
        self.waka.setConfig(self.cfgfile)
        self.waka.schedule()
        self.setAlarmForNextDay()
    def receiveWakeNote_(self,note):
        NSLog("Awoke from sleep, Awake is awoken:)")
        self.stop_(None)
        self.reload_(None)

