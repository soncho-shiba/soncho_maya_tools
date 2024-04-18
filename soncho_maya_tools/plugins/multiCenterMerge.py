import math
import maya.api.OpenMaya as om2
import maya.cmds as cmds
from collections import deque
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

        # TODO:dagpathをkeyに取るdictにして、オブジェクト単位でmerge関数にvertex_idsを渡す
        vertex_ids = []

        sel_iter = om2.MItSelectionList(selection_list, om2.MFn.kComponent)
        while not sel_iter.isDone():
            dag_path, component = sel_iter.getComponent()

            if component.apiType() == om2.MFn.kMeshEdgeComponent:
                edge_iter = om2.MItMeshEdge(dag_path, component)
                vertex_ids.append(self.convert_edges_to_vertex_ids(edge_iter))

            elif component.apiType() == om2.MFn.kMeshPolygonComponent:
                poly_iter = om2.MItMeshEdge(dag_path, component)
                vertex_ids.append(self.convert_faces_to_vertex_ids(poly_iter))

            sel_iter.next()

        adjacent_vertex_id_groups = self.group_adjacent_verities(vertex_ids)
        self.merge_verities(adjacent_vertex_id_groups)

        print(kPluginCmdName + "_done")
        om2.MPxCommand.__init__(self)

    def get_dag_path_and_component(self, node_name):
        selectionList = om2.MSelectionList()
        selectionList.add(node_name)
        dagPath, component = selectionList.getComponent(0)
        return dagPath, component

    def is_selection_valid(self, selection_list: om2.MSelectionList) -> bool:
        """
        現在の選択がエッジまたはフェースのみを含んでいるかどうかをチェックする
        選択が空である、完全に選択されている、頂点を含んでいる、もしくはオブジェクトの選択を含んでいる場合はFalseを返す
        TODO: マルチ選択モードを除外するか決める

        Args:
            selection_list (om2.MSelectionList): 現在の選択リスト

        Returns:
            bool: 選択がエッジまたはフェースのみを含んでいる場合はTrue、それ以外の場合はFalse
        """
        if selection_list.isEmpty():
            return False

        sel_iter = om2.MItSelectionList(selection_list, om2.MFn.kComponent)
        while not sel_iter.isDone():
            _, component = sel_iter.getComponent()
            if component.isNull():
                return False

            api_type = component.apiType()
            if api_type not in (om2.MFn.kMeshEdgeComponent, om2.MFn.kMeshPolygonComponent):
                return False
            sel_iter.next()

        return True

    def convert_edges_to_vertex_ids(self, edge_iter: om2.MItMeshEdge) -> list:
        """
        Example:
            output: [[0, 1], [1, 2], [2, 3], [3, 0], ...]
        """
        vertex_id_groups = []
        while not edge_iter.isDone():
            vertex_ids = [edge_iter.vertexId(0), edge_iter.vertexId(1)]
            vertex_id_groups.append(vertex_ids)
            edge_iter.next()

        return vertex_id_groups

    def convert_faces_to_vertex_ids(self, poly_iter: om2.MItMeshPolygon) -> list:
        """
        Example:
            output: [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], ...]
        """
        vertex_id_groups = []
        while not poly_iter.isDone():
            vertex_ids = poly_iter.getVertices()
            vertex_id_groups.append(vertex_ids)
            poly_iter.next()

        return vertex_id_groups

    def group_adjacent__vertex_ids(self, vertex_index_groups):
        """
        Use Union-Find Algorithm

        Example:
            input -> [[1,2], [2,3], [4,5], [6,7,8], [9,10], [9,12], [12,13]]
            output -> [[1,2,3], [4,5], [6,7,8], [9,10,12,13]]
        """
        parent = {}

        def find(vertex):
            if parent[vertex] != vertex:
                parent[vertex] = find(parent[vertex])
            return parent[vertex]

        def union(vertex1, vertex2):
            root1 = find(vertex1)
            root2 = find(vertex2)
            if root1 != root2:
                parent[root2] = root1

        # 各頂点の初期親を自身に設定
        for group in vertex_index_groups:
            for vertex in group:
                if vertex not in parent:
                    parent[vertex] = vertex

        # 各頂点グループ内の頂点を同じグループにマージ
        for group in vertex_index_groups:
            first_vertex = group[0]
            for vertex in group[1:]:
                union(first_vertex, vertex)

        # マージされたグループを辞書で収集
        merged_groups = {}
        for vertex in parent:
            root = find(vertex)
            if root not in merged_groups:
                merged_groups[root] = []
            merged_groups[root].append(vertex)

        # 辞書から頂点グループのリストを抽出して各グループをソート
        return [sorted(group) for group in merged_groups.values()]

    def merge_verities(self):
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
