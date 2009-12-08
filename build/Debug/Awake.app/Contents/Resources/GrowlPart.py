from Foundation import *
from AppKit import *
import objc,os
objc.setVerbose(True)
from PyObjCTools import AppHelper

class Growler(NSObject):
    singleinst = None
    def init(self):
        if Growler.singleinst:
            return Growler.singleinst
        self = super(Growler, self).init()
        if self is None: return None
        Growler.singleinst = self
        self.GrowlBundle=objc.loadBundle("GrowlApplicationBridge"
                                         ,globals()
                                         ,bundle_path=objc.pathForFramework(
                                             os.path.sep.join( (NSBundle.mainBundle().privateFrameworksPath(),"Growl.framework"))))
        return self
    def createGrowl(self,delegate):
        if self.GrowlBundle:
            GrowlApplicationBridge.setGrowlDelegate_(delegate)
            GrowlApplicationBridge.notifyWithTitle_description_notificationName_iconData_priority_isSticky_clickContext_( "Alert","Hello","Awake",None,0,False,NSDate.date())
        
