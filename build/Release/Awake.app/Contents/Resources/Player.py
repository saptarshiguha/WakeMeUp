## A class for players
from Foundation import *
from AppKit import *
import objc
from PyObjCTools import AppHelper
import traceback
import os
from Utility import *

        
class Player(NSObject):
    def start(self, args):
        pass
    def stop(self, args):
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

class iTunesBase(Player):
    vol=None
    def stop(self,args,xtras):
        os.system("osascript -e 'tell application \"iTunes\" to stop'")
    def volume_set(self, vol):
        self.vol=str(int(vol))
        runAppScriptCommand("tell application \"iTunes\" to set sound volume to %s" % self.vol)
    def volume(self,vol):
        if not self.vol:
            v=Popen(["osascript", "-e","'tell application \"iTunes\" to get sound volume'"], stdout=PIPE).communicate()[0]
            self.v=v.strip()
        return int(self.v)
    def __str__(self):
        return "iTunes"
    
class iTunesURL(iTunesBase):
    def start(self, args,xtras):
        player = args['player']
        v="""tell application "iTunes"
        open location "%s" 
        end tell""" % player
        runAppScriptCommand(v)
    def __str__(self):
        return "iTunesURL"

class iTunesPlaylist(iTunesBase):
    def start(self, args,xtras):
        player=args['player']
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
    def start(self, args,xtras):
        player = args['player']
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


