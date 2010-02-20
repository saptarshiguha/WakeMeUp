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
from PyObjCTools import AppHelper
import traceback
import os
from Utility import *
import types

        
class Player(NSObject):
    cdesc = 'Player'
    def initWithValue_(self,value):
        self = super(Player, self).init()
        if self is None: return None
        if value:
            self.info = value
        else:
            self.info = {}
        return self
    def start(self, args=None,xtrs=None):
        pass
    def stop(self, args=None,xtras=None):
        pass
    def volume_set(self, vol):
        pass
    def volume(self,vol):
        pass
    @classmethod
    def isValid(Player,args):
        if args:
            return True
        else:
            return False
    @classmethod
    def isMusical(Player):
        return True
    
class Action(Player):
    cdesc = 'Action'
    vol=None
    def action(self, args, xtras=None):
        self.v= NSTask.alloc().init()
        if type(args)==types.FunctionType:
            self.v = args(args,xtras)
            return self.v
        else:
            if type(args)==str:
                args = args.split(" ")
            self.v.setLaunchPath_(args[0])
            self.v.setArguments_(args[1:])
        # v.setStandardOutput_(NSFileHandle.fileHandleWithNullDevice())
        # v.setStandardError_(NSFileHandle.fileHandleWithNullDevice())
            self.v.launch()
            return self.v
    def stop(self,args=None,xtras=None):
        if self.v:
            if isinstance(self.v,NSTask):
                if self.info.get("action_woe",True):
                    self.v.waitUntilExit()
                else:
                    self.v.terminate()
            else:
                if self.info.get("action_cmd_stop",None):
                    self.info["action_cmd_stop"](self.v)
        self.v = None
    def start(self,args,xtras=None):
        self.v = self.info.get("action_cmd",self.action)(args,xtras)
    def __str__(self):
        return "Action"
    @classmethod
    def isMusical(Player):
        return False

    
class iTunesBase(Player):
    cdesc = 'iTunesBase'
    vol=None
    def stop(self,args=None,xtras=None):
        os.system("osascript -e 'tell application \"iTunes\" to stop'")
    def volume_set(self, vol):
        print("VOLUME SET=="+str(vol))
        self.vol=str(int(vol))
        runAppScriptCommand("tell application \"iTunes\" to set sound volume to %s" % self.vol)
    def volume(self,vol):
        if not self.vol:
            v=Popen(["osascript", "-e","'tell application \"iTunes\" to get sound volume'"], stdout=PIPE).communicate()[0]
            self.v=v.strip()
        return int(self.v)
    def __str__(self):
        return "iTunes"
# http://pyobjc.sourceforge.net/documentation/pyobjc-core/intro.html
class iTunesURL(iTunesBase):
    cdesc = 'iTunesURL'
    def start(self, args,xtras=None):
        player = args
        v="""tell application "iTunes"
        open location "%s" 
        end tell""" % player
        runAppScriptCommand(v)
    def __str__(self):
        return "iTunesURL"

class iTunesPlaylist(iTunesBase):
    cdesc = 'iTunesPlayList'
    def start(self, args,xtras=None):
        player=args
        v1="""
        tell application "iTunes"
        play playlist "%s"  
        end tell""" % player
        runAppScriptCommand(v1)
        NSThread.sleepForTimeInterval_(4)
        os.system("osascript -e 'tell application \"iTunes\" to play'")
    def __str__(self):
        return "iTunesPlayList"

class iTunesSmartPlaylist(iTunesBase):
    cdesc = 'iTunesSmartPlayList'
    def start(self, args=None,xtras=None):
        player = args
        v1 = """
        set playlist_list to "%s"
        tell application "iTunes"
        delete (tracks in (first playlist whose name is playlist_list))
        end tell""" % player
        runAppScriptCommand(v1)
        NSThread.sleepForTimeInterval_(4)
        v1 = """
        set playlist_list to "%s"
        tell application "iTunes"
        set theTrack to (tracks of (first playlist whose name is playlist_list))
        play first item of theTrack
        end tell""" % player
        runAppScriptCommand(v1)
        NSThread.sleepForTimeInterval_(4)
        os.system("osascript -e 'tell application \"iTunes\" to play'")
    def __str__(self):
        return "iTunesSmartPlayList"


