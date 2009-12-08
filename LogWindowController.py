#
#  LogWindowCollector.py
#  Awake
#
#  Created by Saptarshi  Guha on 11/7/09.
#  Copyright __MyCompanyName__ 2009. All rights reserved.
#

from Foundation import *
from AppKit import *
from Utility import *
import objc
objc.setVerbose(True)

# awakelog = AwakeLog.alloc().initWithInfo_( {'filename':__name__})
class LogWindowController(NSObject):
    logmessages = objc.ivar(u"logmessages")
    logwindow = objc.ivar(u"logwindow")
    inst = None
    @classmethod
    def Instance(LogWindowController):
        return LogWindowController.inst
    def init(self):
        if LogWindowController.inst is None:
            self = super(LogWindowController, self).init()
            LogWindowController.inst = self
        if self is None: return None
        return(LogWindowController.inst)

    def clear_(self,sender):
        self.logmessages.setString_(u"")
        self.logmessages.setNeedsDisplay_(True)
        
    def showwindow_(self,sender):
        self.logwindow.makeKeyAndOrderFront_(self)

    def windowShouldClose_(self,sender):
        return True

    def getTextView(self):
        return self.logmessages

    def refreshWindow(self):
        self.logmessages.setNeedsDisplay_(True)

    def gotoEnd(self):
        # see http://borkware.com/quickies/one?topic=NSTextView
        arange = (self.logmessages.string().length(),0)
        self.logmessages.scrollRangeToVisible_(arange)

    def switchOnScroll(self):
        pass
        # self.logmessages.enclosingScrollView().setHasHorizontalScroller_(True)
        # self.logmessages.setHorizontallyResizable_(True)
        # self.logmessages.setAutoresizingMask_(NSViewWidthSizable | NSViewHeightSizable)
        # self.logmessages.textContainer().setContainerSize_( (100,100))
        # self.logmessages.textContainer().setWidthTracksTextView_(True)
            
