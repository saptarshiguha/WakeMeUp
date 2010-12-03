#
#  main.py
#  Awake
#
#  Created by Saptarshi  Guha on 11/7/09.
#  Copyright __MyCompanyName__ 2009. All rights reserved.
#

#import modules required by application
from objc import *
setVerbose(True)
from Foundation import *
from AppKit import *
from PyObjCTools import *
import sys

NSLog(u"SYS.PATH follows for %s" % sys.version)
NSLog(' '.join(sys.path))
from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib


import AwakeAppDelegate
import LogWindowController
# pass control to AppKit
AppHelper.runEventLoop()
