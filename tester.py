import sys
import os
sys.path.append(os.getcwd())
from Player import *
import Configurator

e='play  [\'kcrw live\', fox,"file://bojuramjggt.kim/sdsd?fr",         1, "http://radio. paradise" "http://radio. paradise" wcpe .23,"file:/bojuramjggt.kim/sdsd?sfr"       ] on 22:10:21 am weekdays for 2hrs'
c=Configurator.Configurator("/tmp/foo",False)
c.addPlayable("kcrw live",type=Player,how="scirpt.sh")
c.addPlayable("fox",type=Player,how="scirpt.sh")
c.addPlayable("wcpe",type=Player,how="scirpt.sh")

c.naturalParse(e)
