import os
import sys
import maya.cmds as cmds
from maya.api import OpenMaya as om2

SONCHO_MAYA_TOOLS = 'soncho_maya_tools'

def pre_settings():
    om2.MGlobal.displayInfo("***{} Pre Settings***".format(SONCHO_MAYA_TOOLS))

def post_settings():
    om2.MGlobal.displayInfo("***{} Pre Settings***".format(SONCHO_MAYA_TOOLS))

def main():
    cmds.evalDeferred(pre_settings, lowPrrity=False)
    cmds.evalDeferred(post_settings, lowPrrity=True)

main()

