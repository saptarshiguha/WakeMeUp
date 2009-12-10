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

import os,sys
import datetime
import random
from Foundation import *
from AppKit import *
import objc
objc.setVerbose(True)
from Wakening import Runner
from Player import *
from MPlayer import *
from Utility import *


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
    def set(self,title, typeclz, how,xtrastuff):
        try:
            typeclz.alloc().init()
        except:
            raise ValueError("Do not instantiate the class:%s" % str(typeclz))
        if not typeclz:
            raise ValueError("Illegal value or type==%s" % str(type))
        if not typeclz.isValid(how):
            raise ValueError("Illegal 'how':%s for type:%s" %(str(how),str(typeclz)))
        self.title = str(title)
        self.play_claz = typeclz
        self.how = how
        self.extras = xtrastuff
  
    def __str__(self):
        return """[playable] title:%s type:%s what:%s""" % (str(self.title),str(self.play_claz.cdesc),str(self.how))

class Configurator:
    def __init__(self,configfile):
        self.cfile =configfile
        self.awakelog = AwakeLog.alloc().initWithInfo_( {'filename':__name__})
    def parseConfig(self):
        self.env={}
        dd = { 'URL': iTunesURL, 'PLAYLIST':iTunesPlaylist, 'SMART': iTunesSmartPlaylist, 'MPlayer':MPlayer,'ACTION':Action
               ,'play':self.addPlayable, 'wakeup':self.addWakeup,'run_appscript':runAppScriptCommand,'ENV':self.env
               ,'mail_gmail':mailViaGmail
               }
        self.playables={}
        self.wakeups = []
        self.wktmp=[]
        # exec(compile(open(self.cfile).read(), self.cfile, 'exec'), globals=dd)
        execfile(self.cfile,dd)
        for k in dd.keys():
            if k in HOOKS.values():
                self.env[k]=dd[k]
        for i in self.wktmp:
            runner = Runner.alloc().init()
            xtra=dict(self.env.items() + i['xtr'].items() )
            runner.create( title=i['title'], play=i['play']
                           ,wake_time=i['wake_time'],end_time=i['end_time']
                           ,fadein=i['fadein'],fadeout=i['fadeout']
                           ,xtr=xtra)
            self.awakelog.info("%s" % runner)
            self.wakeups.append(runner)
    
    def getEnv(self):
        return self.env
    def getWakeups(self):
        return self.wakeups
    def addPlayable(self, title, **kwargs):
        import copy
        p = Playable()
        g=copy.deepcopy(kwargs)
        if g.get('type',None):
            del(g['type'])
        if g.get('how',None):
            del(g['how'])
        p.set(title, kwargs.get('type', None), kwargs.get('how',None),g)
        self.playables[title] = p
        self.awakelog.info("%s" % str(p))
    def addWakeup(self, title, start, play=None,days=range(7),weights=None,end=None, fadein={},
                  fadeout = {},**kwargs):
        current_time = datetime.datetime.today()
        if type(days)==int:
            days=[days,]
        t=filter(lambda r: r<0 or r>6,days)
        if(len(t)>0):
            raise ValueError("Illegal value for days in %s, got %s" %( str(days),str(t)))
        if current_time.weekday() not in days:
            return
        if type(start)==int or type(start)==float:
            wake_time = current_time+datetime.timedelta(seconds=abs(int(start)))
        elif type(start)==list or type(start)==tuple:
            if len(start)==2:
                wake_time = current_time.replace(hour=start[0],minute=start[1],second=0)
            elif len(start)==3:
                wake_time = current_time.replace(day=start[0],hour=start[1],minute=start[2],second=0)
            elif len(start)==4:
                wake_time = current_time.replace(month=start[0],day=start[1],hour=start[2],minute=start[3],second=0)
            elif len(start)==5:
                wake_time = current_time.replace(year=start[0],month=start[1],day=start[2],hour=start[3],minute=start[4],second=0)
            else:
                raise ValueError("Start time is too long %s" % str(start))
        elif type(start)==dict:
            second=0
            minute = start.get('min',current_time.minute)
            hr = start.get('hr',current_time.hour)
            day = start.get('day',current_time.day)
            month = start.get('mon',current_time.month)
            year = start.get('yr',current_time.year)
            wake_time = current_time.replace(year=year,month=month,day=day,hour=hr,minute=minute,second=0)
        else:
            raise ValueError("Strangest Start time: %s" % str(start))
        
        if(wake_time<current_time):
            return
        if play is None:
            play = self.playables.keys()
        elif type(play)==str:
            play=[play,]
        if weights == None:
            weights = [1 for y_ in play]
        elif type(weights)==int or type(weights)==float:
            weights = [weights,]
        if(len(play)!=len(weights)):
            raise ValueError("Length of play must be equal to length of weights in %s" % title)
        which = chooseRandom( play, weights)
        if(which not in self.playables.keys()):
            raise ValueError("The playable %s was not found in the list of playables" % which)
        end_time = end
        if end_time:
            if type(end) == int:
                end_time = wake_time+datetime.timedelta(seconds=abs(end))
            elif type(list(end)) == list:
                end_time = current_time.replace(hour=end[0],minute=end[1],second=0)
                if end_time < wake_time:
                    raise ValueError("end_time:%s is less than start_time:%s" %(end_time, wake_time))
            else:
                raise ValueError("Illegal value for end time: %s" % end_time)
       
        xtr = dict(self.env.items() + kwargs.items() )
        xtr = dict(xtr.items() + self.playables[which].extras.items())
        self.wktmp.append( {'title':title,'play':self.playables[which]
                      ,'wake_time':wake_time,'end_time':end_time
                      ,'fadein':fadein,'fadeout':fadeout,'xtr':xtr})
                           

                                
            


        
        
