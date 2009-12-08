import os,sys
import glob,shutil
from optparse import OptionParser
import datetime
import random
import logging,copy
from heapq import heappush, heappop
from Foundation import *
from AppKit import *
import objc


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

def volchanger(min,max, t):
    return min+(max-min)*t

class WP:

    def __init__(self, title,when, play,sound):
        self.title = title
        self.when = when
        self.play = play
        self.sound = sound
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        dt = self.when.ctime()
        return "WAKE[ title:%s play:%s when:%s volume:{min:%s end:%s dur:%s fader:%s} ]" % (self.title, self.play, dt, self.sound['start'],self.sound['end'],self.sound['duration'],self.sound['fade'].func_name)

class WakeUp:
    URL=0
    ITUNES_PLAYLIST=1
    ITUNES_SMART_PLAYLIST=2
    ITUNES_URL=3
    def __init__(self,filename):
        self.format =  "%(asctime)s: %(message)s"
        logging.basicConfig(level=logging.INFO,format=self.format)
        self.wakeups=[]
        self.setConfig(filename)

    def setConfig(self,filename):
        self.config =  os.path.abspath(os.path.expanduser(os.path.normpath(filename)))
    def parseConfig(self):
        self.playables={}
        self.di = { 'URL':WakeUp.URL,'ITUNES_URL':WakeUp.ITUNES_URL,'ITUNES_SMART_PLAYLIST':WakeUp.ITUNES_SMART_PLAYLIST,'ITUNES_PLAYLIST':WakeUp.ITUNES_PLAYLIST,'playable':self.addPlayable,'wakeup':self.addWakeup}
        self.wakeups=[]
        execfile(self.config,self.di)
    def log(self,s):
#         logging.info(s)
        NSLog(s)
                   
    def getWakeups(self):
        x=[]
        t=copy.deepcopy(self.wakeups)
        while t:
            x.append(heappop(t)[1])
        return(x)

    def addPlayable(self,title,type,player):
        self.log("Registered title: %s player: %s type:%d" %( title,str(player),type))
        self.playables[title] = {'type':type,'player':player}
    
    def addWakeup(self,title=None,days=range(0,7),play=None,weights=None,volume={},start=None):
        if(title is None  or start is None):
            raise ValueError("You have to at least give a title and start time (hr,min)")

        v = datetime.datetime.today()

        a={}
        t=filter(lambda r: r<0 or r>6,days)
        if(len(t)>0):
            raise ValueError("Illegal value for days in %s, got %s" %( str(days),str(t)))
        if v.weekday() not in days:
            return
        x = v.replace(hour=start[0],minute=start[1],second=0)
        if(x<v):
            return
        ##The wakeup is today and after current time
        ##Are we going to play it? Based on 
        if(play is None): play = self.playables.keys()
        if weights == None:
            weights = [1 for y_ in play]
        if(len(play)!=len(weights)):
            raise ValueError("Length of play must be equal to length of weights in %s" % title)
        which = chooseRandom( play, weights)
        if(which not in self.playables.keys()):
            raise ValueError("The playable %s was not found in the list of playables" % which)
        so={ 'start': volume.get('start',0.0), 'duration':volume.get('duration',60),
            'end': volume.get('end',100), 'fade':volume.get('fade', volchanger)}
        if so['end'] < so['start']:
            raise ValueError("For wakeup=%s, end volume(%d) must be greater than start volume(%d) " %( title,so['end'], so['start']))
        a = WP(title=title,when=x, play=which,sound=so)
        NSLog("Scheduled to play: %s" % a)
        heappush(self.wakeups, ((x-v).seconds, a))


if __name__=="__main__":
    fish=WakeUp(sys.argv[1])
    fish.parseConfig()
    print fish.getWakeups()[0]
    print fish.playables[fish.getWakeups()[0].play]['player']

