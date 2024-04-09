import os
import sys
from maya.api import OpenMaya as om2

import maya.cmds as cmds

TOOLS_NAMES = 'soncho_maya_tools'
SUPPORTED_MAYA_VERSIONS = [2024, 2025]
SUPPORTED_PYTHON_VERSION = '3'


def pre_settings():
    om2.MGlobal.displayInfo(f"***{TOOLS_NAMES} pre settings***")


def post_settings():
    om2.MGlobal.displayInfo(f"***{TOOLS_NAMES} post settings***")


def main():
    current_maya_version = int(cmds.about(version=True))
    current_python_version = sys.version.split(' ')[0]

    if current_python_version.startswith(SUPPORTED_PYTHON_VERSION) and current_maya_version in SUPPORTED_MAYA_VERSIONS:
        cmds.evalDeferred(pre_settings, lowPriority=False)
        cmds.evalDeferred(post_settings, lowPriority=True)
    else:
        om2.MGlobal.displayWarning(
            f"Unsupported version. {TOOLS_NAMES} supports Maya {SUPPORTED_MAYA_VERSIONS} and Python {SUPPORTED_PYTHON_VERSION}.")


if __name__ == "__main__":
    main()
