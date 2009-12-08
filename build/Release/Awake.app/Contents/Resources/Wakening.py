
class Runner(NSObject):
    def create(title,play,wake_time,end_time,fadein,fadeout,xtr):
        #play is of class Playables
        self.title = title
        self.play_info = play
        self.wake_time = wake_time
        self.end_time = end_time
        self.fadein = fadein
        self.fadeout = fadeout
        self.extras = xtr
        self.controller = None

    def stop(self):
        if self.controller:
            self.controller.stop()
        if self.extras.get('post_stop',None):
            self.extras['post_stop'](self.play_info,self.extras)
    def start(self):
        if self.extras.get('pre_play',None):
            self.extras['pre_play'](self.play_info,self.extras)
        self.controller = self.play_info.play_claz.alloc().init()
        if self.end_time:
            delta = (self.wake_time - self.end_time).seconds
            self.performSelector_withObject_afterDelay_("stop",None,delta)
        self.controller.start(self.play_info.how,self.extras)
        self.vol_fade_in()
        
    def schedule_to_play(self,basetime):
        timedelta = (self.wake_time - basetime).seconds
        self.performSelector_withObject_afterDelay_("start",None,timedelta)
    def cancel(self):
        NSObject.cancelPreviousPerformRequestsWithTarget_(self)

    def _vol_fade_in(self,o):
        s,e,f,t,d = o
        self.controller.volume_set( f(s,e,t) )
        if t > d:
            return
        else:
            t = (t+1.0)/d
            self.performSelector_withObject_afterDelay_("_vol_fade_in",(s,e,f,t,d),1)

    def vol_fade_in(self):
        s = self.fadein.get('start',0)
        e = self.fadein.get('end',0)
        d = float(self.fadein.get('dur',float(120)))
        f = self.fadein.get('F',self.linear_vol_change)
        t = 0.0
        self.performSelector_withObject_afterDelay_("_vol_fade_in",(s,e,f,t,d),1)
    def linear_vol_change(self, svol,evol,t):
        # 0<=t<=1
        return svol+(evol-svol)*t
    def __cmp__(self,other):
        return cmp(self.wake_time,other.wake_time)
    def __str__(self):
        return """[wakeup]
        Title:%s
        Type:%s 
        When:%s
        End:%s
        Play:%s""" % (self.title, self.player_type, self.wake_time.ctime(),self.end_time.ctime(), self.play_info.title)
