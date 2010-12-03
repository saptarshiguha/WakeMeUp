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
import logging
from LogWindowController import *
from AppKit import *
import objc
objc.setVerbose(True)
from PyObjCTools import AppHelper
import time
import sys
import copy
VERSION_ID = 1.0
HOOKS={'ONAWAKE':"on_awake"
       ,"ONQUIT":"on_quit"
       ,"ONRELOAD":"on_reload"
       ,"ONPREPLAY":"pre_play"
       ,"ONPOSTSTOP":"post_stop"
       ,"ONFINISHLAUNCH":"on_launch"
       ,"ONSETVOLUME":"on_volume_set"
       ,"ONSNOOZE":"on_snooze"
       ,"SNOOZETIME":"snooze_time"
       ,"ACTION_CMD":"action_cmd"
       ,"ACTION_CMD_STOP":"action_cmd_stop"
       ,'NEW_DAY_RELOAD':'reload_new_day'
       }

def runAppScriptCommand(s):
        ap = NSAppleScript.alloc().initWithSource_(s)
        v=ap.executeAndReturnError_(None)
	return(v)

def getPasswordFromKeychain():
	import subprocess
	cmd0="security find-internet-password -gs %s 1>/dev/null" % "smtp.gmail.com"
	p = subprocess.Popen(cmd0, shell=True, bufsize=0, stderr=subprocess.PIPE,close_fds=True).stderr.readline()
	if p==None or len(p)==0 or not p.startswith("password"):
		return ''
	else:
		pw=p.split()[1]
		return pw.split("\"")[1]

def mailViaGmail(to, subject, text,attach=None,gmailuser=None, gmailpwd=None):
	try:
		import smtplib
		from email.MIMEMultipart import MIMEMultipart
		from email.MIMEBase import MIMEBase
		from email.MIMEText import MIMEText
		from email import Encoders
		import os,glob,sys
		if not gmailpwd:
			gmailpwd = getPasswordFromKeychain()
		msg = MIMEMultipart()
		msg['From'] = gmailuser
		msg['To'] = to
		msg['Subject'] = subject
		msg.attach(MIMEText(text))
		if attach:
			attach=('~/tmp/*.py','/tmp/togo')
			if isinstance(attach, str):
				attach = (attach,)
			v=[]
			for y in attach:
				v =v+ glob.glob(os.path.abspath(os.path.normpath(os.path.expanduser(y))))
			attach = v
			#remove duplicates
			v={}
			for x in attach:
				v[x]=1
			attach = v.keys()
			if len(attach)>0: sys.stderr.write("[gmail mailer] Attaching %d files\n" % len(attach))
			for x in attach:
				part = MIMEBase('application', 'octet-stream')
				part.set_payload(open(x, 'rb').read())
				Encoders.encode_base64(part)
				part.add_header('Content-Disposition',
						'attachment; filename="%s"' % os.path.basename(x))
				msg.attach(part)
		mailServer = smtplib.SMTP("smtp.gmail.com", 587)
		mailServer.ehlo()
		mailServer.starttls()
		mailServer.ehlo()
		mailServer.login(gmailuser, gmailpwd)
		mailServer.sendmail(gmailuser, to, msg.as_string())
		mailServer.close()
		return True
	except:
		import sys
		sys.stderr.write("GMAIL ERROR:\n")
		import traceback
		traceback.print_exc()
		return False

class AwakeLog(NSObject):
	logcontroller = None
	def initWithInfo_(self, info):
		self = super(AwakeLog, self).init()
		if self is None: return None
		self.filename=info.get('filename','NA')
		self.format=info.get('format',"%(asctime)s: %(message)s")
		logging.basicConfig(level=logging.INFO,format=self.format)
		sys.stdout = StdOut.alloc().init()
		sys.stderr = StdErr.alloc().init()
		self.infodict =  {
			NSFontAttributeName: NSFont.fontWithName_size_("Courier New Bold", 11),
			NSForegroundColorAttributeName:  NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0.0, 1.0)}
		self.infodictmessage =  {
			NSFontAttributeName: NSFont.fontWithName_size_("Courier New", 11),
			NSForegroundColorAttributeName:  NSColor.colorWithCalibratedRed_green_blue_alpha_(0.1, 0.1, 0.1, 1.0)}
		return self
	def initWithInfo_Logger(self, info,logger):
		self = self.initWithInfo_(info)
		if self is None: return None
		AwakeLog.logcontroller = logger
		AwakeLog.logcontroller.clear_(None)
		AwakeLog.logcontroller.switchOnScroll()
		self.performSelector_withObject_afterDelay_("checkForNewVersion",None,1)
		return self
	def checkForNewVersion(self):
		try:
			import urllib2
			# try:
			response = urllib2.urlopen('http://www.stat.purdue.edu/~sguha/dn/wakemeup.version')
			package = response.read()
			dd={}
			exec package in dd
			dd=dd['awake_news']
			if dd['version']> VERSION_ID:
				dwnurl = dd['download']
				AwakeLog.logcontroller.statusbarmessage = 'New Version: '+dwnurl + "\nInfo:"+dd.get('news')[:40]
		except :
			pass

	def info(self, message):
		self.log("info",str(message))
		
	def log(self, what,message):
		## see http://borkware.com/quickies/one?topic=NSTextView
		entry1 = u"[%s:%s:%s]"  % ( time.ctime(), str(what), str(self.filename))
		entry2 = u"%s\n" % str(message)
		tv = AwakeLog.logcontroller.getTextView().textStorage()

		arange = (tv.string().length(), 0)
		tv.replaceCharactersInRange_withString_(arange,entry1)
		arange = (arange[0], len(entry1))
		tv.setAttributes_range_(self.infodict, arange)

		arange = (tv.string().length(), 0)
		tv.replaceCharactersInRange_withString_(arange,entry2)
		arange = (arange[0], len(entry2))
		tv.setAttributes_range_(self.infodictmessage, arange)
		AwakeLog.logcontroller.gotoEnd()
		AwakeLog.logcontroller.refreshWindow()
		NSLog(str(message))

class StdParent(NSObject):
	def init(self):
		self = super(StdParent, self).init()
		if self is None: return None
		self.fmtdict =  {
		NSForegroundColorAttributeName : NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 1.0)}
		return self
	def write(self,text):
		entry = "%s" % text
		tv = AwakeLog.logcontroller.getTextView().textStorage()
		arange = (tv.string().length(), 0)
		tv.replaceCharactersInRange_withString_(arange,entry)
		arange = (arange[0], len(entry))
		tv.setAttributes_range_(self.fmtdict, arange)
		AwakeLog.logcontroller.gotoEnd()
		AwakeLog.logcontroller.refreshWindow()

class StdOut(StdParent):
	def init(self):
		self = super(StdOut, self).init()
		if self is None: return None
		self.fmtdict =  {
			NSForegroundColorAttributeName : NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 1.0)}
		return self
class StdErr(StdParent):
	def init(self):
		self = super(StdErr, self).init()
		if self is None: return None
		self.fmtdict =  {
			NSForegroundColorAttributeName : NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 0, 0, 1.0)}
		return self

