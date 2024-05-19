# -*- coding: utf-8 -*-
import maya.cmds as cmds

"""
reference: performGridOptions.mel    
"""
"""default values 
OptionVarValue = namedtuple('OptionVarValue', ['type', 'name', 'value']) 
default_option_vars = [ 
OptionVarValue('fv', 'gridSpacing', 5.),  # Length and width OptionVarValue('fv', 'gridDivisions', 5.),  
# Subdivision OptionVarValue('fv', 'gridSize', 12.),  # Grid Lines every OptionVarValue('intValue', 
'displayGridAxes', 1),  # Display > Axes OptionVarValue('intValue', 'displayGridLines', 1),  # Display > Grid lines 
OptionVarValue('intValue', 'displayDivisionLines', 1),  # Display > Subdivision lines OptionVarValue('intValue', 
'displayGridPerspLabels', 0),# Perpective grid numbers > 0: Hide/1: OnAxes/2: along edge OptionVarValue('intValue', 
'displayGridOrthoLabels', 0),# Orthographic grid numbers > 0: Hide/1: OnAxes/2: along edge OptionVarValue('intValue', 
'displayGridAxesAccented', 1),  # Display > Thicker line for axis OptionVarValue('stringValue', 
'displayGridPerspLabelPosition', 'axis'),# Perpective grid numbers > 0: Hide/1: OnAxes/2: along edge OptionVarValue(
'stringValue', 'displayGridOrthoLabelPosition', 'edge')# Orthographic grid numbers > 0: Hide/1: OnAxes/2: along edge 
]"""


class GridSettings:
    def __init__(self):
        self.grid_toggle = cmds.grid(toggle=True, q=True)
        self.space = cmds.grid(spacing=True, q=True)  # Length and width
        self.divisions = cmds.grid(divisions=True, q=True)  # Subdivision
        self.size = cmds.grid(size=True, q=True)  # Grid Lines every
        self.display_axes = cmds.grid(displayAxes=True, q=True)  # Display > Axes
        self.display_grid_lines = cmds.grid(displayGridLines=True, q=True)  # Display > Grid lines
        self.display_division_lines = cmds.grid(displayDivisionLines=True, q=True)  # Display > Subdivision lines
        self.display_perspective_labels = cmds.grid(displayPerspectiveLabels=True, q=True)  # Perspective grid numbers
        self.display_orthographic_labels = cmds.grid(displayOrthographicLabels=True, q=True) # Orthographic grid numbers
        self.display_axes_bold = cmds.grid(displayAxesBold=True, q=True)  # Display > Thicker line for axis
        self.perspective_label_position = cmds.grid(perspectiveLabelPosition=True, q=True)  # Perspective grid numbers
        self.orthographic_label_position = cmds.grid(orthographicLabelPosition=True, q=True) # Orthographic grid numbers
        self.grid_axis_color = cmds.displayColor("gridAxis", q=True)  # Color > Axes
        self.grid_highlight_color = cmds.displayColor("gridHighlight", q=True)  # Color > Gridlines&numbers
        self.grid_color = cmds.displayColor("grid", q=True)  # Color > Subdivision line

    def apply(self):
        cmds.grid(toggle=self.grid_toggle)
        cmds.grid(spacing=self.space)
        cmds.grid(divisions=self.divisions)
        cmds.grid(size=self.size)
        cmds.grid(displayAxes=self.display_axes)
        cmds.grid(displayGridLines=self.display_grid_lines)
        cmds.grid(displayDivisionLines=self.display_division_lines)
        cmds.grid(displayPerspectiveLabels=self.display_perspective_labels)
        cmds.grid(displayOrthographicLabels=self.display_orthographic_labels)
        cmds.grid(displayAxesBold=self.display_axes_bold)
        cmds.grid(perspectiveLabelPosition=self.perspective_label_position)
        cmds.grid(orthographicLabelPosition=self.orthographic_label_position)
        cmds.displayColor("gridAxis", self.grid_axis_color)
        cmds.displayColor("gridHighlight", self.grid_highlight_color)
        cmds.displayColor("grid", self.grid_color)


def get_current_option():
    return GridSettings()


def set_temporary_grid_settings():
    current_settings = get_current_option()

    # Temporary settings
    cmds.grid(spacing=100)
    cmds.grid(divisions=10)
    cmds.grid(size=500)
    cmds.grid(displayAxes=True)
    cmds.grid(displayGridLines=True)
    cmds.grid(displayDivisionLines=True)
    cmds.grid(displayPerspectiveLabels=0)
    cmds.grid(displayOrthographicLabels=0)
    cmds.grid(displayAxesBold=True)
    cmds.grid(perspectiveLabelPosition='axis')
    cmds.grid(orthographicLabelPosition='edge')
    cmds.displayColor("gridAxis", 2)  # default(gray)
    cmds.displayColor("gridHighlight", 14)  # green
    cmds.displayColor("grid", 2)  # default(gray

    return current_settings


def restore_grid_settings(settings):
    settings.apply()


def main():
    current_settings = set_temporary_grid_settings()
    restore_grid_settings(current_settings)
