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
        self.selections = om2.MGlobal.getActiveSelectionList()
        if not self.is_selection_valid(self.selections):
            raise RuntimeError("Please select edges or faces")

        sel_iter = om2.MItSelectionList(self.selections, om2.MFn.kComponent)
        vertex_group_dict = self.group_components_by_adjacent_vertices(sel_iter)
        print(vertex_group_dict)
        print(kPluginCmdName + "_done")
        om2.MPxCommand.__init__(self)

    def get_dag_path_and_component(self, node_name):
        selectionList = om2.MSelectionList()
        selectionList.add(node_name)
        dagPath, component = selectionList.getComponent(0)
        return dagPath, component

    def is_selection_valid(self, selections: om2.MSelectionList) -> bool:
        """現在の選択がエッジかフェースのみであるかをチェックします。
        無選択、全選択、頂点、オブジェクト選択時にはFalseを返します。

        Args:
            selections (om2.MSelectionList): 現在の選択リスト

        Returns:
            bool: 選択がエッジまたはフェースのみの場合はTrue、それ以外はFalse
        """
        if selections.isEmpty():
            return False

        sel_iter = om2.MItSelectionList(selections, om2.MFn.kComponent)
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

    def format_edge_name(self, dagPath, edge_iter):
        return "{}.e[{}]".format(dagPath.fullPathName(), int(edge_iter.index()))

    def group_components_by_adjacent_vertices(
        self, sel_iter: om2.MItSelectionList
    ) -> dict:
        groups = {}

        while not sel_iter.isDone():
            dagPath, component = sel_iter.getComponent()

            if component.apiType() == om2.MFn.kMeshEdgeComponent:
                edge_iter = om2.MItMeshEdge(dagPath, component)

                sel_vertex_indices = []
                while not edge_iter.isDone():
                    sel_vertex_indices.append(edge_iter.vertexId(0))
                    sel_vertex_indices.append(edge_iter.vertexId(1))
                    edge_iter.next()
                print(sel_vertex_indices)
                
                obj_edge_iter = om2.MItMeshEdge(dagPath)
                while not edge_iter.isDone():

                    edge_name = self.format_edge_name(dagpath, edge_iter)
                    groups[edge_name].append(edge_iter.vertexId(0))
                    groups[edge_name].append(edge_iter.vertexId(1))

                    for i in edge_iter.getConnectedEdges():
                        connected_edge = obj_edge_iter.setIndex(i)
                        connected_edge_vertices = [
                            connected_edge.vertexId(0),
                            connected_edge.vertexId(1),
                        ]
                        for vertex_id in connected_edge_vertices:
                            if vertex_id in sel_vertex_indices:
                                groups[edge_name].append(edge_iter.index())
                    edge_iter.next()

            elif component.apiType() == om2.MFn.kMeshPolygonComponent:
                poly_iter = om2.MItMeshPolygon(dagPath)
                pass

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
