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
from Runner import WakeItem
from Player import *
from MPlayer import *
from Utility import *
import naturalAlarm2

def getName():
    i=0
    while True:
        i = i+1
        yield "Wakeup-%d" % i

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
        self.env={}

    def __str__(self):
        return """[playable] title:%s type:%s what:%s""" % (str(self.title),str(self.play_claz.cdesc),str(self.how))

class Configurator:
    def __init__(self,configfile,uselog=True):
        self.cfile =configfile
        self.uselog = uselog
        if self.uselog:
            self.awakelog = AwakeLog.alloc().initWithInfo_( {'filename':__name__})
        self.createDataStructures()
    def createDataStructures(self):
        self.playables={}
        self.wakeups = []
        self.wktmp=[]
        self.env={}
        self.getAName = getName()
        
    def parseConfig(self):
        self.createDataStructures()
        dd = { 'URL': iTunesURL, 'PLAYLIST':iTunesPlaylist, 'SMART': iTunesSmartPlaylist, 'MPlayer':MPlayer,'ACTION':Action
               ,'play':self.addPlayable, 'wakeup':self.addWakeup,'run_appscript':runAppScriptCommand,'ENV':self.env
               ,'mail_gmail':mailViaGmail,'N':self.naturalParse,'groupname':self.getAName
               }
        execfile(self.cfile,dd)
        for k in dd.keys():
            if k in HOOKS.values():
                self.env[k]=dd[k]
        for i in self.wktmp:
            wakeitem = WakeItem.alloc().init()
            xtra=dict(self.env.items() + i['xtr'].items() )
            wakeitem.create( title=i['title'], play=i['play']
                           ,wake_time=i['wake_time'],end_time=i['end_time']
                           ,fadein=i['fadein'],fadeout=i['fadeout']
                           ,xtr=xtra)
            self.awakelog.info("%s" % wakeitem)
            self.wakeups.append(wakeitem)
    
    def getEnv(self):
        return self.env
    def getWakeups(self):
        return self.wakeups
    def naturalParse(self,x,fadein={},fadeout={},**kwargs):
        if self.uselog:
            self.awakelog.info("Parsing natural alarm: %s" % str(x))
        c= naturalAlarm2.NaturalAlarm(x)
        if self.uselog:
            self.awakelog.info("Parsing natural alarm results: %s" % str(c))
        else:
            print ("Parsing natural alarm results: %s" % str(c))
        x=self.constructWakeUp(c)
        x['fadein']=fadein
        x['fadeout']=fadeout
        if self.uselog and x:
            self.awakelog.info("Natural alarm constructed: %s" % str(x))
        if x:
            self.addWakeup(title=self.getAName.next(),start = x['time'],play = x['play'],days=x['days'],weights=x['weights'],end=x['end'],fadein=fadein,fadeout=fadeout,**kwargs)
        else:
            raise Exception("Bad Parsing: %s" % x)
        # print self.wktmp
    def convertIntoPlay(self,pl):
        import re
        ## remove quotations
        if pl[0]=="'" or pl[0]=="\"":
            pl = pl[1:-1]
        import urlparse
        haveit = self.playables.get(pl,None)
        if not haveit  == None:
            if self.uselog:
                self.awakelog.info("Returning cached playable for %s" % pl)
            else:
                print("Returning cached playable for %s" % pl)
            return pl
        pl=re.sub("\"","",pl)
        scheme = pl.split(":",1)
        try:
            what = scheme[1]
        except IndexError:
            raise Exception("This is not defined, how to play? %s" % pl)
        x=scheme[0]
        
        if x == "file":
            self.addPlayable(title=pl, type=MPlayer,how = what)
        elif scheme[0] == "http":
            self.addPlayable(title=pl, type=iTunesURL,how = pl)
        elif x == "playlist":
            self.addPlayable(title=pl, type=iTunesPlaylist,how = what)
        elif x == "smart":
            self.addPlayable(title=pl, type=iTunesSmartPlaylist,how = what)
        elif x == "url":
            self.addPlayable(title=pl, type=iTunesURL,how = what)
        elif x == "action":
            self.addPlayable(title=pl, type=Action,how = what)
        elif x == "mplayer":
            self.addPlayable(title=pl, type=MPlayer,how = what)
        else:
            raise Exception("Not present and cannot infer url:%s" % pl)
        return pl

    def constructWakeUp(self,obj):
        ##compulsory: starttime
        container={'time':None,'play':None,'days':range(7), 'weights':None,'end':None,'fadein':{},'fadeout':{}}
        starttime = obj.start_time
        if starttime is None:
            raise ValueError("I received a naturally parsed expression without a start time?: %s" % str(obj))
        year,month,day,hour,minute,sec = starttime.year,starttime.month,starttime.day,starttime.hour, starttime.minute,starttime.second
        container['time']={'yr':year, 'mon':month, 'day':day, 'hr':hour, 'min':minute,'sec':sec}
                    #optional: end time
        if obj.end_time:
            container['end'] = (obj.end_time - obj.start_time).seconds
                #not compulsory: dow
        dow = obj.regularity
        days = []
        arr = ("mon","tue","wed","thur","fri","sat","sun")
        for i in range(7):
            if dow[i]:
                days.append(arr[i])
        container['days'] = days
        #compulsory: what to play
        actual = obj.getsubject()
        if actual is None:
            return None
        play=[]
        weights=[]
        whatwaslast = None
        for w in naturalAlarm2.readToken(actual):
            if type(w)==float:
                weights.append(w)
                whatwaslast = "notlabel"
            else:
                actually = obj.urlhash.get(w,w)
                if whatwaslast == "alabel":
                    weights.append(1.0)
                play.append(self.convertIntoPlay(actually))
                whatwaslast="alabel"
        if whatwaslast == "alabel":
            weights.append(1.0)
        container['weights'] = weights
        container['play'] = play
        return container
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
        if self.uselog:
            self.awakelog.info("Added %s" % str(p))
    def addWakeup(self, title, start, play=None,days=range(7),weights=None,end=None, fadein={},
                  fadeout = {},**kwargs):
        current_time = datetime.datetime.today()
        if not (type(days) == tuple or type(days)==list):
            days = [days,]
        if type(days)==int:
            days=[days,]
        elif type(days)==str and days.upper()=="TODAY":
            days = [current_time.weekday(),]
        elif type(days)==tuple or type(days) == list:
            pass
        else:
            raise ValueError("Invalid type for days for wakeup:%s" % title)
        days_new = []
        for x in days:
            if type(x) == int:
                days_new.append(x)
            elif type(x) == str:
                p = x.lower()
                if p == "today":
                    days_new.append(current_time.weekday())
                elif p.startswith("m"):
                    days_new.append(0)
                elif p.startswith("tu"):
                    days_new.append(1)
                elif p.startswith("w"):
                    days_new.append(2)
                elif p.startswith("th"):
                    days_new.append(3)
                elif p.startswith("f"):
                    days_new.append(4)
                elif p.startswith("sa"):
                    days_new.append(5)
                elif p.startswith("su"):
                    days_new.append(6)
        days = days_new
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
            second = start.get('sec',0)
            wake_time = current_time.replace(year=year,month=month,day=day,hour=hr,minute=minute,second=second)
        else:
            raise ValueError("Strangest Start time: %s" % str(start))
        
        if(wake_time<current_time or wake_time > (current_time+datetime.timedelta(seconds=86400))):
            return
		#confirm within 24hrs
        if play is None:
            play = self.playables.keys()
        elif type(play)==str:
            play=[play,]
        if weights == None:
            weights = [1 for y_ in play]
        elif type(weights)==int or type(weights)==float:
            weights = [weights for y_ in play]
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
        xtr = dict(self.playables[which].extras.items()+xtr.items())
        self.wktmp.append( {'title':title,'play':self.playables[which]
                      ,'wake_time':wake_time,'end_time':end_time
                      ,'fadein':fadein,'fadeout':fadeout,'xtr':xtr})
                           

                                
            
        


