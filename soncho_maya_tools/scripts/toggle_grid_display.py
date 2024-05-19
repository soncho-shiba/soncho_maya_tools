# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel
from collections import namedtuple

__name__ = 'toggle_grid_display'

OptionVarValue = namedtuple('OptionVarValue', ['type', 'name', 'value'])

"""
optionVar -fv gridSpacing 5 -fv gridDivisions 5 -fv gridSize 12 -intValue displayGridAxes 1 -intValue displayGridLines 1 -intValue displayDivisionLines 1 -intValue displayGridPerspLabels 0 -intValue displayGridOrthoLabels 0 -intValue displayGridAxesAccented 1 -stringValue displayGridPerspLabelPosition axis -stringValue displayGridOrthoLabelPosition edge;
"""
user_option_vars = []
default_option_vars = [
    OptionVarValue('fv', 'gridSpacing', 5.),  # Length and width
    OptionVarValue('fv', 'gridDivisions', 5.),  # Subdivision
    OptionVarValue('fv', 'gridSize', 12.),  # Grid Lines every
    OptionVarValue('intValue', 'displayGridAxes', 1),  # Display > Axes
    OptionVarValue('intValue', 'displayGridLines', 1),  # Display > Grid lines
    OptionVarValue('intValue', 'displayDivisionLines', 1),  # Display > Subdivision lines
    OptionVarValue('intValue', 'displayGridPerspLabels', 0),
    # Perpective grid numbers > 0: Hide/1: OnAxes/2: along edge
    OptionVarValue('intValue', 'displayGridOrthoLabels', 0),
    # Orthographic grid numbers > 0: Hide/1: OnAxes/2: along edge
    OptionVarValue('intValue', 'displayGridAxesAccented', 1),  # Display > Thicker line for axis
    OptionVarValue('stringValue', 'displayGridPerspLabelPosition', 'axis'),
    # Perpective grid numbers > 0: Hide/1: OnAxes/2: along edge
    OptionVarValue('stringValue', 'displayGridOrthoLabelPosition', 'edge')
    # Orthographic grid numbers > 0: Hide/1: OnAxes/2: along edge
]

custum_option_vars = [
    OptionVarValue('fv', 'gridSpacing', 100.),  # Length and width
    OptionVarValue('fv', 'gridDivisions', 1.),  # Subdivision
    OptionVarValue('fv', 'gridSize', 500.),  # Grid Lines every
    OptionVarValue('intValue', 'displayGridAxes', 1),  # Display > Axes
    OptionVarValue('intValue', 'displayGridLines', 1),  # Display > Grid lines
    OptionVarValue('intValue', 'displayDivisionLines', 1),  # Display > Subdivision lines
    OptionVarValue('intValue', 'displayGridPerspLabels', 0),
    # Perpective grid numbers > 0: Hide/1: OnAxes/2: along edge
    OptionVarValue('intValue', 'displayGridOrthoLabels', 0),
    # Orthographic grid numbers > 0: Hide/1: OnAxes/2: along edge
    OptionVarValue('intValue', 'displayGridAxesAccented', 1),  # Display > Thicker line for axis
    OptionVarValue('stringValue', 'displayGridPerspLabelPosition', 'axis'),
    # Perpective grid numbers > 0: Hide/1: OnAxes/2: along edge
    OptionVarValue('stringValue', 'displayGridOrthoLabelPosition', 'edge')
    # Orthographic grid numbers > 0: Hide/1: OnAxes/2: along edge
]


#TODO:2023以降では処理を分岐してcatを設定する必要があることに注意
def get_user_option():
    #type: () -> bool

    for option_var in default_option_vars:
        if cmds.optionVar(exists=option_var.name):
            user_option_var = OptionVarValue(option_var.type, option_var.name, option_var.value)
            user_option_vars.append(user_option_var)

    if len(user_option_vars) <= 0:
        return False
    else:
        return True

def set_user_options():
    for option_var in user_option_vars:
        if cmds.optionVar(exists=option_var.name):
            if option_var.type == "fv":
                cmds.optionVar(fv=(option_var.name, option_var.value))

            if option_var.type == "intValue":
                cmds.optionVar(intValue=(option_var.name, option_var.value))

            if option_var.type == "stringValue":
                cmds.optionVar(stringValue=(option_var.name, option_var.value))


def set_custom_options():
    for option_var in custum_option_vars:
        if cmds.optionVar(exists=option_var.name):
            if option_var.type == "fv":
                cmds.optionVar(fv=(option_var.name, option_var.value))

            if option_var.type == "intValue":
                cmds.optionVar(intValue=(option_var.name, option_var.value))

            if option_var.type == "stringValue":
                cmds.optionVar(stringValue=(option_var.name, option_var.value))


def set_default_options():
    for option_var in default_option_vars:
        if cmds.optionVar(exists=option_var.name):
            if option_var.type == "fv":
                cmds.optionVar(fv=(option_var.name, option_var.value))

            if option_var.type == "intValue":
                cmds.optionVar(intValue=(option_var.name, option_var.value))

            if option_var.type == "stringValue":
                cmds.optionVar(stringValue=(option_var.name, option_var.value))


def main():

    #set_default_options()

    set_custom_options()
    mel.eval("gridCallback  1")
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
