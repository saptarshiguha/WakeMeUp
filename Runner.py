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
from Utility import *

class WakeItem(NSObject):
    def create(self,title,play,wake_time,end_time,fadein,fadeout,xtr):
        #play is of class Playables
        self.title = title
        self.play_info = play
        self.wake_time = wake_time
        self.end_time = end_time
        self.fadein = fadein
        self.fadeout = fadeout
        self.extras = xtr
        self.controller = None
    def playInfo(self):
        return self.play_info
    def extraArgs(self):
        return self.extras
    def stop(self,info=None):
        if self.controller:
            self.controller.stop()
            if self.extras.get(HOOKS['ONPOSTSTOP'],None):
                self.extras['INFO']=info
                self.extras[HOOKS['ONPOSTSTOP']](self)
            NSObject.cancelPreviousPerformRequestsWithTarget_(self)
        self.controller = None
    def start(self):
        if self.extras.get(HOOKS['ONPREPLAY'],None):
            willplay = self.extras[HOOKS['ONPREPLAY']](self)
            if willplay is None: willplay = True
        else:
            willplay = True
        if willplay:
            self.controller = self.play_info.play_claz.alloc().initWithValue_(self.extras)
            if self.end_time:
                delta = (self.end_time - self.wake_time).seconds
                self.performSelector_withObject_afterDelay_("stop",None,delta)

            s=self.fadein.get('start',0)
            self.extraArgs().get(HOOKS['ONSETVOLUME'],self.controller.volume_set)(s)
            self.controller.start(self.play_info.how,self.extras)
            self.vol_fade_in()
        
    def schedule_to_play(self,basetime):
        timedelta = (self.wake_time - basetime).seconds
        self.performSelector_withObject_afterDelay_("start",None,timedelta)
    def cancel(self):
        NSObject.cancelPreviousPerformRequestsWithTarget_(self)

    def _vol_fade_in(self,o):
        s,e,f,t,d = o
        # self.controller.volume_set( f(s,e,float(t)/d) )
        self.extraArgs().get(HOOKS['ONSETVOLUME'],self.controller.volume_set)(f(s,e,float(t)/d))
        if t > d:
            return
        else:
            t = t+1
            self.performSelector_withObject_afterDelay_("_vol_fade_in",(s,e,f,t,d),1)

    def vol_fade_in(self):
        if self.play_info.play_claz.isMusical() and self.extras.get('volfade',True):
            s = self.fadein.get('start',self.extras.get('fade_start',0))
            e = self.fadein.get('end',self.extras.get('fade_end',100))
            d = float(self.fadein.get('dur',float(self.extras.get('fade_dur',90))))
            f = self.fadein.get('F',self.extras.get('fade_F',self.linear_vol_change))
            if(self.fadein.has_key('F') and self.fadein['F'] is None):
                f  = self.linear_vol_change
            t = 0.0
            self.performSelector_withObject_afterDelay_("_vol_fade_in",(s,e,f,t,d),0.1)
    def linear_vol_change(self, svol,evol,t):
        # 0<=t<=1
        return svol+(evol-svol)*t
    def __cmp__(self,other):
        return cmp(self.wake_time,other.wake_time)
    def __str__(self):
        if self.end_time:
            et = self.end_time.ctime()
        else:
            et = "Doesn't stop"
        return """[wakeup] Title:%s Play:%s (%s) When:%s End:%s""" % (self.title, self.play_info.title,self.play_info.play_claz.cdesc, self.wake_time.ctime(),et)
