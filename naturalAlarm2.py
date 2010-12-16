import parsedatetime as pdt
import parsedatetime_consts as pdc
import string
from time import localtime,asctime
from datetime import datetime,timedelta
import re

pdc_p = pdt.Calendar(pdc.Constants())


def readToken(word):
    token=[]
    pos = 1
    space = re.compile("[\],\s]")
    word=word+" "
    l = len(word)
    lastw=False
    while True:
        if pos == l:
            break
        if space.match(word[pos]) != None:
            if lastw:
                x = ''.join(token)
                token = []
                lastw=False
                p=x
                try:
                    p=float(x)
                except ValueError:
                    pass
                yield p
        else:
            lastw=True
            token.append(word[pos])
        pos = pos+1
    return


def cleanword(word,punct=False,all=False):
    # logging.info("cleanword: %s" % word)
    word=word.lower()
    word=word.strip()
    word=re.sub("\s+" , " ", word)
    puncs='!#$%&\()*+-;<=>?@\\^_`{|}~'
    if all:
        puncs=re.compile('[:]').sub("",string.punctuation)
    regex = re.compile('[%s]' % re.escape(puncs)) 
    if punct:
        word=regex.sub("" ,word)
    return word





class NaturalAlarm:
    def find_regularity(self,word):
        import sys
        word = word.lower()
        sys.stdout.write( "reg(%s):"%word)
        h={}
        def check(exp):
            if h.get(exp,None):
                m=h[exp]
            else:
                m=re.compile(exp)
                h[exp] = m
            if m.search(word):
                return True
            else:
                return False
        def _inline():
            if check("daily|(every day)|(everyday)") or check("weekdays") or check("(every weekday)") or check ("(every week day)"):
                return [True,True,True,True,True,True,True]
            f=[False,False,False,False,False,False,False]
            if (check("every") and check("(mon|monday)")) or check("mondays"): f[0]=True
            if (check("every") and check("(tue|teusday|tuesday)")) or check("tuesdays"): f[1]=True
            if (check("every") and check("(wed|wednesday|wensday)")) or check("wednesdays|wensdays"): f[2]=True
            if (check("every") and check("(thu|thursday)")) or check("thursdays"): f[3]=True
            if (check("every") and check("(fri|friday)")) or check("fridays"): f[4]=True
            if (check("every") and check("(sat|saturday)")) or check("saturdays"): f[5]=True
            if (check("every") and check("(sun|sunday)")) or check("sundays"): f[6]=True
            if check("mwf"): f=[True,False,True,False,True,False,False]
            if check("tth"): f=[False,True,False,True,False,False,False]
            if check("weekends") or check("every weekend"): f=[False,False,False,False,False,True,True]
            if check("weekday"): f=[True,True,True,True,True,False,False]
            return f
        if word=="":
            self.regularity = [True,True,True,True,True,True,True]
        else:
            self.regularity = _inline()
        sys.stdout.write("%s\n" % str(self.regularity))
    def find_start(self, s):
        t = pdc_p.parse(s)
        if t[1] == 0:
            raise ValueError("Invalid start time (%s) for %s" % (s,self.oldword))
        t=datetime( *t[0][:6])
        print "start(%s):%s"%(s,str(t))
        self.start_time = t+timedelta(seconds=3)
    def find_end(self,s):
        t = pdc_p.parse(s, self.start_time)
        if t[1] == 0:
            print "end:"
            return
        ## parsedatetime will sometimes (e.g. for 2hrs) compute time from now
        ## so get the difference and add it to start_time
        ending = datetime( *t[0][:6])
        # start_time = self.start_time
        # print "End time:%s" % str(ending)
        # ending1 = start_time.replace(day=ending.day,hour  =ending.hour, minute = ending.minute,second=ending.second) - start_time
        # ending2 = ending -  datetime.today()
        # delta = min(ending1,ending2)
        delta = ending - self.start_time
        deltasecs = delta.days*86400+delta.seconds
        if deltasecs <0 :
            deltasecs = delta.days*86400+delta.seconds
        if (deltasecs > 86400 or deltasecs<0):
            raise ValueError("Cannot play for longer than 24hrs or negative (passed=%s,orgi=%s,end_time=%s,start=%s" % (s,self.oldword,ending,str(start_time)))
        self.end_time=ending
        print "end(%s):%s"%(s,str(self.end_time))
        
    def findMax(self, rex, s, deflt):
        mymax=-1
        p=rex.search(s)
        if p:
            # print p.group()
            return p.start()
        else:
            return deflt
        # for x in rex.finditer(s):
        #     print x.group()
        #     if x.start() >= mymax:
        #         mymax = x.start()
        # if mymax<0:
        #     mymax = deflt
        # print "DOE"
        # return mymax
    def drive(self):
        ## make this regex work on word boundaries!
		## see http://www.comanswer.com/question/does-python-re-module-support-word-boundaries-%255Cb
		## for information on word boundaries
        startsyno = re.compile(r"\b(in|at|awake|wakeupto|wakeup|wake|awaketo|awake|cometo|come|arouse|rouse|play|listen|play|from|form|beginning|begining|starting|since)\b",flags=re.IGNORECASE)
        endsynon =  re.compile(r"\b(to|for|till|until|untill|stop|(stop\s+at)|(stop\s+in)|(stop\s+after)|(not more)|most|kill)\b",flags=re.IGNORECASE)
        regularity =  re.compile(r"\b(daily|every|weekends|weekend|weekdays|weekday|mwf|tth|mondays|monays|tuesdays|wednesdays|wensdays|thursdays|thrusdays|thersdays|fridays|saturdays|sats|sundays|suns)\b",flags=re.IGNORECASE)
        startpos = self.findMax(startsyno,self.word,len(self.word))
        durationpos = self.findMax(endsynon,self.word,len(self.word))
        regularitypos = self.findMax(regularity,self.word,len(self.word))
        if startpos == None:
            raise ValueError("No starting identifier found in expression: %s" % self.oldword)
        y= sorted(zip( (startpos,durationpos,regularitypos) , ("find_start","find_end","find_regularity")),reverse=False)
        # print "Foo="+str(y)
        t={}
        print("%s == %s" %(y[0][1],self.word[ y[0][0]:(y[1][0]) ]))
        print("%s == %s" %(y[1][1],self.word[ y[1][0]:(y[2][0]) ]))
        print("%s == %s" %(y[2][1],self.word[ y[2][0]:(len(self.word)) ]))
        t[y[0][1]]= ( self.word[ y[0][0]:(y[1][0]) ] )
        t[y[1][1]]= ( self.word[ y[1][0]:(y[2][0]) ] )
        t[y[2][1]]= ( self.word[ y[2][0]:(len(self.word)) ] )
        self.funcs['find_start'](t['find_start'])
        self.funcs['find_end'](t['find_end'])
        self.funcs['find_regularity'](t['find_regularity'])
    def __str__(self):
        x = "NaturalAlarm:%s\nstart time:%s end time:%s regularity: %s" % (self.oldword, self.start_time, self.end_time, self.regularity)
        return x
    def __init__(self, word):
        self.oldword = word
        self.urlhash={}
        self.oldsubject=None
        self.word=re.sub("'","\"",self.oldword)
        self.start_time = None
        self.end_time  = None
        self.regularity = [True,True,True,True,True,True,True]
        self.funcs={ 'find_start':self.find_start, 'find_end':self.find_end, 'find_regularity':self.find_regularity}
        def repme1(mo):
            import uuid
            k = re.sub("-","",str(uuid.uuid4()))
            v=mo.group(0)
            self.urlhash[k] = v
            return(k)
        def repme2(mo):
            import uuid
            self.oldsubject = mo.group(0)
            return ""
        self.word = re.sub('["]([^"]*)["]',repme1,self.word) #raplace things in quote, protects stange characters
        self.word = re.sub('[\[]([^\[]*)[\]]',repme2,self.word) # replace the subject
        #by this time we have play X at Time every blah untill blah where X=[...]
        self.driven = self.drive()
    def getsubject(self):
        return self.oldsubject

# p=NaturalAlarm("play ['foo'] for 2 hrs from 9:30 am every friday")
p=NaturalAlarm("play ['foo'] at 2:34 pm")
print p
