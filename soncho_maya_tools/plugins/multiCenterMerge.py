import math
import maya.api.OpenMaya as om2
import maya.cmds as cmds
import maya.mel as mel
from collections import deque
import itertools

kPluginCmdName = "multiCenterMerge"


def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


class multiCenterMerge(om2.MPxCommand):

    def __init__(self):
        om2.MPxCommand.__init__(self)

    def doIt(self, args):
        # TODO:UNDO処理を書く
        selection_list = om2.MGlobal.getActiveSelectionList()
        if not self.is_selection_valid(selection_list):
            print("Please select edges or faces")
            return

        merge_vertex_groups = {}

        sel_iter = om2.MItSelectionList(selection_list, om2.MFn.kComponent)
        while not sel_iter.isDone():
            dag_path, component = sel_iter.getComponent()
            dag_path_str = dag_path.__str__()
            vertex_group = []
            if component.apiType() == om2.MFn.kMeshEdgeComponent:
                edge_iter = om2.MItMeshEdge(dag_path, component)
                vertex_groups = self.convert_edges_to_merge_vertex_groups(edge_iter)

            elif component.apiType() == om2.MFn.kMeshPolygonComponent:
                poly_iter = om2.MItMeshPolygon(dag_path, component)
                vertex_groups = self.convert_faces_to_merge_vertex_groups(poly_iter)

            if dag_path_str in merge_vertex_groups.keys():
                for vertex_group in vertex_groups:
                    if not vertex_group in merge_vertex_groups[dag_path_str]:
                        merge_vertex_groups[dag_path_str].append(vertex_group)
            else:
                merge_vertex_groups[dag_path_str] = vertex_groups

            sel_iter.next()

        adjacent_vertex_id_groups = {}
        for key, value in merge_vertex_groups.items():
            adjacent_vertex_id_groups[key] = self.group_adjacent_merge_vertex_groups(value)
        print("adjacent_vertex_id_groups : {}".format(adjacent_vertex_id_groups))
        self.merge_vertices(adjacent_vertex_id_groups)

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

    def convert_edges_to_merge_vertex_groups(self, edge_iter: om2.MItMeshEdge) -> list[list[int]]:
        """
        Example:
            output: [[0, 1], [1, 2], [2, 3], [3, 0], ...]
        """
        vertex_id_groups = []
        while not edge_iter.isDone():
            merge_vertex_groups = [edge_iter.vertexId(0), edge_iter.vertexId(1)]
            vertex_id_groups.append(merge_vertex_groups)
            edge_iter.next()

        return vertex_id_groups

    def convert_faces_to_merge_vertex_groups(self, poly_iter: om2.MItMeshPolygon) -> list[list[int]]:
        """
        Example:
            output: [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], ...]
        """
        vertex_id_groups = []
        while not poly_iter.isDone():
            merge_vertex_groups = poly_iter.getVertices()
            vertex_id_groups.append(merge_vertex_groups)
            poly_iter.next()

        return vertex_id_groups

    def group_adjacent_merge_vertex_groups(self, vertex_index_groups) -> list:
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

    def create_vertex_name_list(self, dag_path, vertex_ids):
        vertex_names = ["{}.vtx[{}]".format(dag_path.__str__(), int(vertex_id)) for vertex_id in vertex_ids]
        return vertex_names

    def get_vertex_group_center(self, vertex_ids):
        selection_list = om2.MSelectionList()
        for vertex_id in vertex_ids:
            selection_list.add(vertex_id)

        point_array = om2.MPointArray()
        for i in range(selection_list.length()):
            dag_path, component = selection_list.getComponent()
            iter = om2.MItMeshVertex(dag_path, component)
            while not iter.isDone():
                point_array.append(iter.position(om2.MSpace.kWorld))
                iter.next()

        center = om2.MPoint()
        for point in point_array:
            center += point
        center /= point_array.length()

        return [center.x, center.y, center.z]

    def merge_vertices_by_om2(self, adjacent_vertex_id_groups):
        cmds.selectType(vertex=True)

        for dag_path in adjacent_vertex_id_groups.keys():
            vertex_id_groups = adjacent_vertex_id_groups[dag_path]
            for vertex_ids in vertex_id_groups:
                cmds.select(clear=True)
                center = self.get_vertex_group_center(vertex_ids)
                vertex_names = self.create_vertex_name_list(dag_path, vertex_ids)
                if vertex_names:
                    om2.MGlobal.executeCommand(
                        f"move -a {center[0]} {center[1]} {center[2]} {' '.join(vertex_names)}"
                    )
                    om2.MGlobal.executeCommand(
                        "polyMergeVertex -d 0.000001 -ch true"
                    )  # TODO:melを使用する方法と計算速度の比較をする

    def merge_vertices(self, adjacent_vertex_id_groups):
        #TODO: グループごとに順番にマージすると頂点番号がかわってしまう　→　頂点番号を維持する方法、もしくはIDではなく位置ベースにする、もしくは
        cmds.selectType(vertex=True)

        for dag_path in adjacent_vertex_id_groups.keys():
            vertex_id_groups = adjacent_vertex_id_groups[dag_path]
            for vertex_ids in vertex_id_groups:
                cmds.select(clear=True)
                vertex_names = self.create_vertex_name_list(dag_path, vertex_ids)
                print(vertex_names)
                if vertex_names:
                    cmds.select(vertex_names, replace=True)
                    mel.eval("polyMergeToCenter")  # TODO:ＡＰＩ2.0を使用する方法と計算速度の比較をする


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
