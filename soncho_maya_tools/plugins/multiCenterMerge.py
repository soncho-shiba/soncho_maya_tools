# -*- coding: utf-8 -*-
import sys
import maya.api.OpenMaya as om2
import maya.cmds as cmds
import maya.mel as mel

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

    def doIt(self, *args):
        selection_list = om2.MGlobal.getActiveSelectionList()
        if not self.is_selection_valid(selection_list):
            print("Invalid selection. Please select edges or faces")
            return

        vert_id_groups_per_comp = self.classify_vert_ids_by_comp(selection_list)
        vert_id_groups_by_adjacency = {
            key: self.classify_vert_ids_by_adjacency(value) for key, value in vert_id_groups_per_comp.items()
        }

        self.merge_vertices(vert_id_groups_by_adjacency)

        print(kPluginCmdName + "done")
        om2.MPxCommand.__init__(self)

    @staticmethod
    def is_selection_valid(selection_list):
        # type: (om2.MSelectionList) -> bool
        """
        現在の選択がエッジまたはフェースのみを含んでいる、もしくはエッジとフェース両方を選択しているマルチコンポーネント選択かをチェックする
        選択が空である、頂点を含んでいる、全選択されている、もしくはオブジェクトの選択を含んでいる場合はFalseを返す

        Args:
            selection_list (om2.MSelectionList): 現在の選択リスト

        Returns:
            bool: 選択がエッジまたはフェースのみを含んでいる場合はTrue、それ以外の場合はFalse
        """
        if selection_list.isEmpty():
            return False

        sel_iter = om2.MItSelectionList(selection_list, om2.MFn.kComponent)
        while not sel_iter.isDone():
            dag_path, comp = sel_iter.getComponent()
            if comp.isNull():
                return False

            api_type = comp.apiType()
            if api_type not in (om2.MFn.kMeshEdgeComponent, om2.MFn.kMeshPolygonComponent):
                return False

            mesh_fn = om2.MFnMesh(dag_path)
            if api_type == om2.MFn.kMeshEdgeComponent:
                total_edges = mesh_fn.numEdges
                sel_edges = om2.MFnSingleIndexedComponent(comp).elementCount
                if sel_edges == total_edges:
                    return False

            if api_type == om2.MFn.kMeshPolygonComponent:
                total_faces = mesh_fn.numPolygons
                sel_faces = om2.MFnSingleIndexedComponent(comp).elementCount
                if sel_faces == total_faces:
                    return False

            sel_iter.next()

        return True

    @staticmethod
    def classify_vert_ids_by_comp(selection_list):
        # type: (om2.MSelectionList) -> "dict[str, list[int]]"
        def convert_edges_to_vert_groups(edge_iter):
            # type: (om2.MItMeshEdge) -> "list[list[int]]"

            """
            Example:
                output: [[0, 1], [1, 2], [2, 3], [3, 0], ...]
            """
            vert_id_groups = []
            while not edge_iter.isDone():
                merge_vert_groups = [edge_iter.vertexId(0), edge_iter.vertexId(1)]
                vert_id_groups.append(merge_vert_groups)
                edge_iter.next()
            return vert_id_groups

        def convert_faces_to_vert_groups(poly_iter):
            # type: (om2.MItMeshPolygon) -> "list[list[int]]"
            """
            Example:
                output: [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], ...]
            """
            vert_id_groups = []
            while not poly_iter.isDone():
                merge_vert_groups = poly_iter.getVertices()
                vert_id_groups.append(merge_vert_groups)
                poly_iter.next()
            return vert_id_groups

        vert_id_groups_per_comp = {}

        sel_iter = om2.MItSelectionList(selection_list, om2.MFn.kComponent)
        while not sel_iter.isDone():
            dag_path, comp = sel_iter.getComponent()
            dag_path_str = dag_path.__str__()

            if comp.apiType() == om2.MFn.kMeshEdgeComponent:
                vert_groups = convert_edges_to_vert_groups(om2.MItMeshEdge(dag_path, comp))

            elif comp.apiType() == om2.MFn.kMeshPolygonComponent:
                vert_groups = convert_faces_to_vert_groups(om2.MItMeshPolygon(dag_path, comp))
            else:
                vert_groups = []

            if dag_path_str in vert_id_groups_per_comp.keys():
                if vert_groups not in vert_id_groups_per_comp[dag_path_str]:
                    vert_id_groups_per_comp[dag_path_str].append(vert_groups)
            else:
                vert_id_groups_per_comp[dag_path_str] = vert_groups

            sel_iter.next()

        return vert_id_groups_per_comp

    @staticmethod
    def classify_vert_ids_by_adjacency(vert_id_groups):
        # type: (list) -> "list[list[int]]"
        """
        Use Union-Find Algorithm

        Example:
            input -> [[1,2], [2,3], [4,5], [6,7,8], [9,10], [9,12], [12,13]]
            output -> [[1,2,3], [4,5], [6,7,8], [9,10,12,13]]
        """
        parent = {}

        def find(_vert):
            if parent[_vert] != _vert:
                parent[_vert] = find(parent[_vert])
            return parent[_vert]

        def union(_vert1, _vert2):
            root1 = find(_vert1)
            root2 = find(_vert2)
            if root1 != root2:
                parent[root2] = root1

        # 各頂点の初期親を自身に設定
        for group in vert_id_groups:
            for vert in group:
                if vert not in parent:
                    parent[vert] = vert

        # 各頂点グループ内の頂点を同じグループにマージ
        for group in vert_id_groups:
            first_vert = group[0]
            for vert in group[1:]:
                union(first_vert, vert)

        # マージされたグループを辞書で収集
        merged_groups = {}
        for vert in parent:
            root = find(vert)
            if root not in merged_groups:
                merged_groups[root] = []
            merged_groups[root].append(vert)

        # 辞書から頂点グループのリストを抽出して各グループをソート
        return [sorted(group) for group in merged_groups.values()]

    @staticmethod
    def create_vert_name_list(dag_path, vert_ids):
        # type: (om2.MDagPath, "list[int]") -> "list[str]"
        vert_names = ["{}.vtx[{}]".format(dag_path.__str__(), int(vert_id)) for vert_id in vert_ids]
        return vert_names

    @staticmethod
    def get_vert_group_center(dag_path, vert_ids):
        # type: (om2.MDagPath, "list[int]") -> "list[float]"
        selection_list = om2.MSelectionList()
        selection_list.add(dag_path)
        m_dag_path = selection_list.getDagPath(0)

        comp = om2.MObject()
        mesh_vertex_iter = om2.MItMeshVertex(m_dag_path, comp)

        x_total = 0.0
        y_total = 0.0
        z_total = 0.0
        for _id in vert_ids:
            mesh_vertex_iter.setIndex(_id)
            pos = mesh_vertex_iter.position(om2.MSpace.kWorld)
            x_total += pos.x
            y_total += pos.y
            z_total += pos.z

        x_center = x_total / len(vert_ids)
        y_center = y_total / len(vert_ids)
        z_center = z_total / len(vert_ids)

        return [x_center, y_center, z_center]

    def merge_vertices(self, vert_id_groups_by_adjacency):
        # type: ( "Dict[str, List[List[int]]]" ) -> None
        target_vert_name_list = []
        for day_path in vert_id_groups_by_adjacency.keys():
            vert_id_groups = vert_id_groups_by_adjacency[day_path]
            for vert_ids in vert_id_groups:
                vert_names = self.create_vert_name_list(day_path, vert_ids)
                if vert_names:
                    center = self.get_vert_group_center(day_path, vert_ids)
                    #  標準コマンドを呼んでいるのでUndo待ち行列に追加される
                    cmds.move(center[0], center[1], center[2], vert_names, absolute=True, worldSpace=True)
                    target_vert_name_list += vert_names

        cmds.select(target_vert_name_list, replace=True)
        # 標準コマンドを呼んでいるのでUndo待ち行列に追加される
        mel.eval("polyMergeVertex -d 0.000001 -ch true")


def cmdCreator():
    return multiCenterMerge()


def _get_plugin_instance(plugin_object, is_initializing=True):
    return om2.MFnPlugin(plugin_object, "soncho_shiba", "0.1", "Any") if is_initializing else om2.MFnPlugin(
        plugin_object)


def initializePlugin(obj):
    plugin = om2.MFnPlugin(obj, "soncho_shiba", "1.0", "Any")
    try:
        plugin.registerCommand(kPluginCmdName, cmdCreator)

    except Exception as e:
        raise Exception("Failed to register command:{}".format(kPluginCmdName))


def uninitializePlugin(obj):
    plugin = om2.MFnPlugin(obj)
    try:
        plugin.deregisterCommand(kPluginCmdName)

    except Exception as e:
        raise Exception("Failed to unregister command:{}".format(kPluginCmdName))


""" how to use
import maya.cmds as cmds
cmds.loadPlugin("multiCenterMerge.py")
cmds.multiCenterMerge()
"""
