# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

'''The following program uses any fem-program with an
inputdeck for topology optimisation

There are several classes which are needed for the initializing of
the nodes and elements. If you want to add a fem-program which does
not exist, just implement an ascci-file. And change the output ascci.
The whole optimisation process works with several dictonarys in
which are nodes and elements are saved.

Source code:
             Name: Denk, Martin
             Date: 02.2016
             Accronym: DMST
'''



bl_info = {
    "name": "Topologie Optimization",
    "author": "Martin Denk",
    "description": "Optimization by solving finet element problems",
    "version": (0, 3, 0),
    "blender": (2, 64, 0),
    "location": "View3D > Tool Shelf > Topo Opti",
    "url": "None",
    "wiki_url": "None",
    "category": "Mesh"
}


if "bpy" in locals():
    import importlib
    importlib.reload(ui_topo)
else:
    from . import ui_topo


import bpy
from bpy.props import *


# global properties for the script, mainly for UI
class TopoOptimizationPropertyGroup(bpy.types.PropertyGroup):
    # -----
    # Values for the optimization
    # -----
    # Volumina ratio
    vol_ratio = FloatProperty(
            name="Volumina Ratio",
            default=0.3,
            min=0.0,
            # 172 degrees
            max=1.0,
            precision=2,
            description="Ratio between the design space and solution space")
    # Sectionpart for the penalty factor
    penalty_value = FloatProperty(
            name="Penalty Factor",
            default=3.0,
            min=1.5,
            max = 15.0,
            precision=3,
            description="Exponent for the penalty function")
    # Materialsets
    mat_sets = IntProperty(
            name="Number of material sets",
            default=20,
            min=1,
            description="Number of sets for the step-material law")
    # Scaling value const
    n_const = IntProperty(
            name="Iteration const",
            default=2,
            min=1,
            description="Iterations after decreased volumina ratio")
    # Scaling value linear
    n_scale = IntProperty(
            name="Iteration scale",
            default=1,
            min=1,
            description="Design ratio will decreased over given iterations")
    # Change iteration
    n_change = IntProperty(
            name="Change system iteration",
            default=10,
            min=1,
            description="Value on which iteration the system is changing")
    # Number of adaptions
    n_adapt_iter = IntProperty(
            name="Adap. Numbers",
            default=5,
            min=1,
            description="Number of adpation by using iteration adaption")
    # Addition of volumina ratio
    vol_ratio_add = FloatProperty(
            name="Add volumina ratio",
            default=0.1,
            min=0.0,
            # 172 degrees
            max=1.0,
            precision=2,
            description="Adaption of volumina ratio")
    # Weight factor
    weight_factor = FloatProperty(
            name="Weight factor",
            default=0.5,
            min=0.0,
            # 172 degrees
            max=1.0,
            precision=2,
            description="Weighting different systems")
    # Density export
    dens_selec_value = FloatProperty(
            name="Density selection (export)",
            default=0.8,
            min=0.0,
            # 172 degrees
            max=1.0,
            precision=2,
            description="All elements with densitys above this value will be exported")
    # -----
    # Checkboxes controlling the solution type
    # -----
    # Sensitivity weight
    sens_topo = BoolProperty(
            name="Use density",
            default=False,
            description="Using an filter for avoiding numerical problems")
    # Density weight
    dens_topo = BoolProperty(
            name="Use sensitivity",
            default=False,
            description="Using an filter for avoiding numerical problems")
    # Controll of optimization
    filter_topo = BoolProperty(
            name="Filter",
            default=True,
            description="Using an filter for avoiding numerical problems")
    # Controll of optimization
    no_des_topo = BoolProperty(
            name="No design space",
            default=False,
            description="There are area which should not taken into account")
    # Optimization type
    single_topo = BoolProperty(
            name="Single physic",
            default=False,
            description="Selection of single physic optimization")
    multi_topo = BoolProperty(
            name="Multi physic",
            default=True,
            description="Selection of multi physic optimization")
    # Physic in optimization
    thermal_topo = BoolProperty(
            name="Thermal",
            default=True,
            description="Thermal physic is selected")
    structural_topo = BoolProperty(
            name="Structural",
            default=True,
            description="Structural physic is selected")
    fluid_topo = BoolProperty(
            name="Fluid",
            default=False,
            description="Fluid physic is selected -> laminar")
    # Material law
    beso_topo = BoolProperty(
            name="BESO",
            default=False,
            description="BESO-Law is selected")
    simp_topo = BoolProperty(
            name="SIMP",
            default=True,
            description="SIMP-Law is selected")
    # Scaling method
    median_topo = BoolProperty(
            name="Median",
            default=True,
            description="Using median for scaleing different physic systems")
    mid_topo = BoolProperty(
            name="Average",
            default=False,
            description="Using average value for scaleing different physical systems")
    # Coupel type
    weight_topo = BoolProperty(
            name="Weight Factor",
            default=True,
            description="Weight the different physical systems")
    adapt_topo = BoolProperty(
            name="Adaption",
            default=False,
            description="Adaption of an old solution")
    # Additional parameter for adaption
    start_topo = BoolProperty(
            name="Start Struc",
            default=False,
            description="Start system can be struc or thermal")
    adaptweight_topo = BoolProperty(
            name="Adaption with weight",
            default=False,
            description="Adaption of an weight solution")
    adaptiter_topo = BoolProperty(
            name="Iteration Adaption",
            default=False,
            description="Adaption of an weight solution")
    # Export control
    inp_topo = BoolProperty(
            name="Output fe-mesh (inp)",
            default=False,
            description="Export of an fe mesh in abaqus style")
    stl_topo = BoolProperty(
            name="Import Last Result",
            default=True,
            description="Stl output")
    stl_topo_step = BoolProperty(
            name="Import each step",
            default=True,
            description="Import")
    auto_geo_blend = BoolProperty(
            name="Auto geo improve",
            default=True,
            description="Using blender function for smoothing the result")




def register():
    # register properties
    bpy.utils.register_class(TopoOptimizationPropertyGroup)
    bpy.types.Scene.topoOpt = bpy.props.PointerProperty(type=TopoOptimizationPropertyGroup)
    bpy.utils.register_module(__name__)


def unregister():
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
