import os,sys
import datetime
import random
from Foundation import *
from AppKit import *
import objc
from helper.Utils import *
from Wakening import Runner
from helper.Player import *
from helper.Mplayer import *
import helper.Utility as Utility

def chooseRandom(ob,wts):
    def cumsum(x):
        s=[]
        y=0
        for i in x:
            y=y+i
            s.append(y)
        return(s)
    s=sum(wts)
    wts = [x/float(s) for x in wts]
    cwts = cumsum(wts)
    u = random.random()
    for i,w in enumerate(cwts):
        if u < w:
            o = ob[i]
            break
    return o

class Playable:
    def set(title, typeclz, how):
        if not typeclz:
            raise ValueError("Illegal value or type==%s" % str(type))
        if not typeclz.isValid(how):
            raise ValueError("Illegal 'how':%s for type:%s" %(str(how),str(typeclz)))
        self.title = str(title)
        self.play_claz = typeclz
        self.how = how
    def __str__(self):
        return "[playable] title:%s type:%s what:%s" % (str(title),str(typeclz),str(how))

class Configurator:
    def __init__(self,configfile):
        self.cfile =configfile
    def parseConfig(self):
        dd = { 'URL': iTunesURL, 'PLAYLIST':iTunesPlaylist, 'SMART': iTunesSmartPlaylist, 'MPlayer':Mplayer
               ,'play':self.addPlayable, 'wakeup':self.addWakeup,'run_appscript':Utility.runAppScriptCommand,'ENV':self.env
               }
        self.playables={}
        self.wakeups = []
        self.env = None
        exec(compile(open(self.cfile).read(), self.cfile, 'exec'), dd)
    def getWakeups(self):
        return self.wakeups
    def addPlayable(self, title, **kwargs):
        p = Playable()
        p.set(title, kwargs.get('type', None), kwargs.get('how',None))
        self.playables[title] = p
        NSLog("%s" % str(p))
    def addWakeup(self, title, start, play=None,days=range(7),weights=None,end=None, fadein={},
                  fadeout = {},**kwargs):
        current_time = datetime.datetime.today()
        t=filter(lambda r: r<0 or r>6,days)
        if(len(t)>0):
            raise ValueError("Illegal value for days in %s, got %s" %( str(days),str(t)))
        if current_time.weekday() not in days:
            return
        wake_time = current_time.replace(hour=start[0],minute=start[1],second=0)
        if(wake_time<current_time):
            return
        if play is None:
            play = self.playables.keys()
        if weights == None:
            weights = [1 for y_ in play]
        if(len(play)!=len(weights)):
            raise ValueError("Length of play must be equal to length of weights in %s" % title)
        which = chooseRandom( play, weights)
        if(which not in self.playables.keys()):
            raise ValueError("The playable %s was not found in the list of playables" % which)
        end_time = end
        if not end_time:
            if type(end) == int:
                end_time = wake_time+datetime.timedelta(seconds=abs(end))
            else type(list(end)) == list:
                end_time = current_time.replace(hour=end[0],minute=end[1],second=0)
                if end_time < wake_time:
                    raise ValueError("end_time:%s is less than start_time:%s" %(end_time, wake_time))
            else:
                raise ValueError("Illegal value for end time: %s" % end_time)

        runner = Runner.alloc().init()
        xtr = dict(self.env.items() + kwargs.items() )

        runner.create(title=title,play=self.playables[which]
                      ,start=wake_time,end=end_time
                      ,fadein=fadein,fadeout=fadeout,xtr)
        NSLog("%s" % runner)
        self.wakeups.append(runner)

                                
            


        
        
