import math
import maya.api.OpenMaya as om2
import maya.cmds as cmds


kPluginCmdName = "multiCenterMerge"


def maya_useNewAPI():
    pass


class multiCenterMerge(om2.MPxCommand):

    def __init__(self):
        om2.MPxCommand.__init__(self)


    def doIt(self, args):
        self.sel = om2.MGlobal.getActiveSelectionList()
        if not self.is_selection_valid(self.sel):
            raise RuntimeError("please edges or faces")

        print(kPluginCmdName + "done")

    def is_selection_valid(self,sel_list):
        """現在の選択がエッジかフェースのみであるかをチェックします。
        無選択、全選択、頂点、オブジェクト選択時にはFalseを返します。

        Args:
            sel_list (om2.MSelectionList): 現在の選択リスト

        Returns:
            bool: 選択がエッジまたはフェースのみの場合はTrue、それ以外はFalse
        """
        if sel_list.isEmpty():
            return False

        sel_iter = om2.MItSelectionList(sel_list, om2.MFn.kComponent)
        while not sel_iter.isDone():
            _, component = sel_iter.getComponent()
            if component.isNull():
                return False

            api_type = component.apiType()
            if api_type not in (om2.MFn.kMeshEdgeComponent, om2.MFn.kMeshPolygonComponent):
                return False
            sel_iter.next()

        return True

    def grouping_comps():
        pass

    def get_center():
        pass

    def merge():
        pass

def cmdCreator():
    return multiCenterMerge()


def initializePlugin(obj):
    plugin = om2.MFnPlugin(obj, "soncho_shiba", "0.1", "Any")
    try:
        plugin.registerCommand(kPluginCmdName, cmdCreator)
    except:
        raise Exception("Failed to register command:{}".format(kPluginCmdName))


def uninitializePlugin(obj):
    plugin = om2.MFnPlugin(obj)
    try:
        plugin.deregisterCommand(kPluginCmdName)

    except:
        raise Exception("Failed to unregister command:{}".format(kPluginCmdName))


""" how to use
import maya.cmds as cmds
cmds.loadPlugin("multiCenterMerge.py")
cmds.multiCenterMerge()
"""
