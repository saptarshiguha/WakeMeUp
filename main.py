#
#  main.py
#  Awake
#
#  Created by Saptarshi  Guha on 11/7/09.
#  Copyright __MyCompanyName__ 2009. All rights reserved.
#

#import modules required by application
import objc
objc.setVerbose(True)
import Foundation
import AppKit

from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib


import AwakeAppDelegate
import LogWindowController
# pass control to AppKit
AppHelper.runEventLoop()
