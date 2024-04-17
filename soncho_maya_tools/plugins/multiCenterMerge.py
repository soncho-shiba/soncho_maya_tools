import math
import maya.api.OpenMaya as om2
import maya.api.OpenMayaUI as omui
import maya.cmds as cmds

import itertools

kPluginCmdName = "multiCenterMerge"

def maya_useNewAPI():
    pass

class multiCenterMerge(om2.MPxCommand):

    def __init__(self):
        om2.MPxCommand.__init__(self)

    def doIt(self, args):
        selection_list = om2.MGlobal.getActiveSelectionList()
        if not self.is_selection_valid(selection_list):
            raise RuntimeError("Please select edges or faces")

        vertex_groups = []
        sel_iter = om2.MItSelectionList(selection_list, om2.MFn.kComponent)
        while not sel_iter.isDone():
            dagPath, component = sel_iter.getComponent()

            if component.apiType() == om2.MFn.kMeshEdgeComponent:
                vertex_groups = self.group_edges_and_convert_to_vertex_lists()

            elif component.apiType() == om2.MFn.kMeshPolygonComponent:
                pass
                # vertex_groups = self.group_faces_and_convert_to_vertex_lists(selection_list)

            sel_iter.next()
        print("Vertex groups for merging:", vertex_groups)

        print(kPluginCmdName + "_done")
        om2.MPxCommand.__init__(self)

    def get_dag_path_and_component(self, node_name):
        selectionList = om2.MSelectionList()
        selectionList.add(node_name)
        dagPath, component = selectionList.getComponent(0)
        return dagPath, component

    def is_selection_valid(self, selection_list: om2.MSelectionList) -> bool:
        """現在の選択がエッジかフェースのみであるかをチェックします。
        無選択、全選択、頂点、オブジェクト選択時にはFalseを返します。
        TODO:マルチ選択モードを対象外にする
        Args:
            selection_list (om2.MSelectionList): 現在の選択リスト

        Returns:
            bool: 選択がエッジまたはフェースのみの場合はTrue、それ以外はFalse
        """
        if selection_list.isEmpty():
            return False

        sel_iter = om2.MItSelectionList(selection_list, om2.MFn.kComponent)
        while not sel_iter.isDone():
            _, component = sel_iter.getComponent()
            if component.isNull():
                return False

            api_type = component.apiType()
            if api_type not in (
                om2.MFn.kMeshEdgeComponent,
                om2.MFn.kMeshPolygonComponent,
            ):
                return False
            sel_iter.next()

        return True

    def group_edges_and_convert_to_vertex_lists(self):
        selection_list = om2.MGlobal.getActiveSelectionList()
        edge_groups = {}
        vertex_groups = []

        for i in range(selection_list.length()):
            dag_path, component = selection_list.getComponent(i)
            if not component.isNull() and component.apiType() == om2.MFn.kMeshEdgeComponent:
                edge_fn = om2.MFnSingleIndexedComponent(component)
                edge_ids = edge_fn.getElements()

                edge_iter = om2.MItMeshEdge(dag_path)
                while not edge_iter.isDone():
                    if edge_iter.index() in edge_ids:
                        # MIntArrayをPythonのリストに変換
                        connected_edges = list(edge_iter.getConnectedEdges())
                        # Pythonのリスト同士を連結
                        key = frozenset([edge_iter.index()] + connected_edges)
                        if key not in edge_groups:
                            edge_groups[key] = set()
                        edge_groups[key].update([edge_iter.vertexId(0), edge_iter.vertexId(1)])
                    edge_iter.next()

        for vertices in edge_groups.values():
            vertex_list = list(vertices)
            if vertex_list not in vertex_groups:
                vertex_groups.append(vertex_list)

        return vertex_groups


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
