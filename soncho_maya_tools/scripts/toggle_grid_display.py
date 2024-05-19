# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel
from collections import namedtuple


__name__  = 'toggle_grid_display'


OptionVarValue = namedtuple('OptionVarValue', ['type', 'flag_name', 'value'])


"""
optionVar -fv gridSpacing 100 -fv gridDivisions 1 -fv gridSize 500 -intValue displayGridAxes 1 -intValue displayGridLines 1 -intValue displayDivisionLines 1 -intValue displayGridPerspLabels 0 -intValue displayGridOrthoLabels 0 -intValue displayGridAxesAccented 1 -stringValue displayGridPerspLabelPosition axis -stringValue displayGridOrthoLabelPosition edge;
"""


option_var_values = [OptionVarValue('fv', 'gridSpacing', 100.),
                     OptionVarValue('fv', 'gridDivisions', 1.),
                     OptionVarValue('fv', 'gridSize', 500.),
                     OptionVarValue('intValue', 'displayGridAxes', 1),
                     OptionVarValue('intValue', 'displayGridLines', 1),
                     OptionVarValue('intValue', 'displayDivisionLines', 1),
                     OptionVarValue('intValue', 'displayGridPerspLabels', 0),
                     OptionVarValue('intValue', 'displayGridOrthoLabels', 0),
                     OptionVarValue('intValue', 'displayGridAxesAccented', 1),
                     OptionVarValue('stringValue', 'displayGridPerspLabelPosition', 'axis'),
                     OptionVarValue('stringValue', 'displayGridOrthoLabelPosition', 'edge')
                     ]


def get_grid_option():
    #TODO: 2022と2019で設定オプションの違いがないか確かめる

    for option_var_value in option_var_values:
        if cmds.optionVar(exist = option_var_value.flag_name):
            print(cmds.optionVar(q='defaultTriangles'))


def set_grid_oprion():
    pass


def main():
    get_grid_option()


    '''
    saveShelf CurvesSurfaces "C:/Users/akane/Documents/maya/2019/prefs/shelves/shelf_CurvesSurfaces";
    // Result: 1 // 
    saveShelf XGen "C:/Users/akane/Documents/maya/2019/prefs/shelves/shelf_XGen";
    // Result: 1 // 
    saveShelf Omniverse "C:/Users/akane/Documents/maya/2019/prefs/shelves/shelf_Omniverse";
    // Result: 1 // 
    // Saving preferences to : C:/Users/akane/Documents/maya/2019/prefs/userPrefs.mel // 
    // Undo: gridCallback OptionBoxWindow|formLayout109|tabLayout4|formLayout111|tabLayout5|columnLayout3 1 
    '''
    """
    performTextureViewGridOptions.mel
    """