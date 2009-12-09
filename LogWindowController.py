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
from Utility import *
import objc
objc.setVerbose(True)

# awakelog = AwakeLog.alloc().initWithInfo_( {'filename':__name__})
class LogWindowController(NSObject):
    logmessages = objc.ivar(u"logmessages")
    logwindow = objc.ivar(u"logwindow")
    statusbarmessage = objc.ivar(u"statusbarmessage")
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
            
