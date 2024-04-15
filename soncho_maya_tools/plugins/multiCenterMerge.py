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

    def get_dag_path_and_component(node_name):
        selectionList = om2.MSelectionList()
        selectionList.add(node_name)
        dagPath, component = selectionList.getComponent(0)
        return dagPath, component

    def group_components_by_adjacent_vertices(sel_iter):
        groups = {}

        while not sel_iter.isDone():
            dagPath, component = sel_iter.getComponent()

            if component.apiType() == om2.MFn.kMeshEdgeComponent:
                edge_iter = om2.MItMeshEdge(dagPath)
                while not edge_iter.isDone():
                    if edge_iter.index() in component:
                        vertices = [edge_iter.vertexId(0), edge_iter.vertexId(1)]
                        for vertex_id in vertices:
                            vertex_name = "{}.vtx[{}]".format(
                                dagPath.fullPathName(), vertex_id
                            )
                            if vertex_name not in groups:
                                groups[vertex_name] = []
                            groups[vertex_name].append(
                                "{}.e[{}]".format(
                                    dagPath.fullPathName(), edge_iter.index()
                                )
                            )
                    edge_iter.next()

            elif component.apiType() == om2.MFn.kMeshPolygonComponent:
                poly_iter = om2.MItMeshPolygon(dagPath)
                while not poly_iter.isDone():
                    if poly_iter.index() in component:
                        vertices = poly_iter.getVertices()
                        for vertex_id in vertices:
                            vertex_name = "{}.vtx[{}]".format(
                                dagPath.fullPathName(), vertex_id
                            )
                            if vertex_name not in groups:
                                groups[vertex_name] = []
                            groups[vertex_name].append(
                                "{}.f[{}]".format(
                                    dagPath.fullPathName(), poly_iter.index()
                                )
                            )
                    poly_iter.next()

            sel_iter.next()

        return groups


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
