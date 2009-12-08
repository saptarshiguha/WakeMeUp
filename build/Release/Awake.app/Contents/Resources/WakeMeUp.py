from Foundation import *
from AppKit import *
import objc
from PyObjCTools import AppHelper
import os
from Configurator import Configurator
import traceback
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
        if not rnarg:
            sself.running=None
        self.srtd=[]
    def stopCurrentRunning(self):
        if self.running:
            self.running.stop(None)

    # def vol_fade_in(self):
    #     result = self.running.volume_fade_in()
    #     if result:
    #         self.performSelector_withObject_afterDelay_("vol_fade_in",None)

    def cancelRequests(self):
        for i in self.srtd:
            if i:
                i.cancel()
        if self.running:
            self.runnng.cancel()
    
    def runPlayer(self, p):
        self.stopCurrentRunning()
        self.running = p
        self.running.start()
        
    def schedule(self):
        import datetime
        wks = self.config.getWakeups()
        self.srtd = sort(wks)
        current_time =  datetime.datetime.today()
        for i in self.srtd:
            # timedelta = (i.getStartTime() - current).seconds
            i.schedule_to_play(current_time)

