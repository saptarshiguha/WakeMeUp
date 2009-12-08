from Foundation import *
from AppKit import *
import objc
from PyObjCTools import AppHelper

def runAppScriptCommand(s):
        ap = NSAppleScript.alloc().initWithSource_(s)
        ap.executeAndReturnError_(None)
