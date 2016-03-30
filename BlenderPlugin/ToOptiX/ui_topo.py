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

import bpy
from bpy.props import *
import bpy.ops

import os
import math

import mathutils
from . import topo

__bpydoc__ = """
Topologie optimization

"""


class OBJECT_OT_start_topo_optimization(bpy.types.Operator):
    """Starts the topology optimization"""
    bl_idname="object.start_topo_optimization"
    bl_label="Run the optimization"
    bl_options = {'REGISTER'}
    bl_category = "Topo Opt"
    objName = "lf_topoOpt"

    def execute(self, context):
        scene = context.scene
        volfrac = scene.topoOpt.vol_ratio
        penal = scene.topoOpt.penalty_value
        rmin = 0
        matSets = scene.topoOpt.mat_sets
        lastStepIter = scene.topoOpt.n_scale
        numbIterAfter = scene.topoOpt.n_const
        adaptChangeIteration = scene.topoOpt.n_change
        adapVolfrac = scene.topoOpt.vol_ratio_add
        NumberOfAdapChanges = scene.topoOpt.n_adapt_iter
        weightFactorStruc = scene.topoOpt.weight_factor
        ThermalIsActive = scene.topoOpt.thermal_topo
        StructIsActive = scene.topoOpt.structural_topo
        SensitivIsActive = scene.topoOpt.sens_topo
        AdaptionIsActive = scene.topoOpt.adapt_topo
        StartStrucAdap = scene.topoOpt.start_topo
        WeightAdapIsActive = scene.topoOpt.adaptweight_topo
        IterativeAdapIsActive = scene.topoOpt.adaptiter_topo
        midValueIsActive = scene.topoOpt.mid_topo
        simpIsActive = scene.topoOpt.simp_topo
        mExpoInpIsActive = scene.topoOpt.inp_topo
        mExpoStlIsActive = scene.topoOpt.stl_topo
        ccxPath = "ccx"
        abaPath = "testx"
        solverTypeisAba = False
        xSelec = scene.topoOpt.dens_selec_value
        noDesSpaceIsActive = scene.topoOpt.no_des_topo
        dispResultIsActive = scene.topoOpt.stl_topo_step
        filterIsActive = scene.topoOpt.fluid_topo
        topo.topo_start3d(volfrac, penal, rmin, matSets, lastStepIter, numbIterAfter,
                   adaptChangeIteration, adapVolfrac, NumberOfAdapChanges,
                   weightFactorStruc, ThermalIsActive,
                   StructIsActive, SensitivIsActive, AdaptionIsActive,
                   StartStrucAdap, WeightAdapIsActive, IterativeAdapIsActive,
                   midValueIsActive, simpIsActive, mExpoInpIsActive,
                   mExpoStlIsActive, ccxPath, abaPath, solverTypeisAba, xSelec,
                   noDesSpaceIsActive, dispResultIsActive, filterIsActive)
        #bpy.context.space_data.context = 'MODIFIER'
        bpy.ops.object.modifier_add(type='REMESH')
        bpy.context.object.modifiers["Remesh"].mode = 'SMOOTH'
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 4
        return {'FINISHED'}


class VIEW3D_OT_topo_opti_tools(bpy.types.Panel):
    '''This class draws the settings for ui'''
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Topo Opti"
    bl_label = "Topology Optimization"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        #-----
        # Checkboxes and values
        #-----
        # Settings for material law
        row = layout.row()
        row.label("Optimization iteration and system controll:")
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "n_const")
        rowsub.prop(scene.topoOpt, "n_scale")
        row = layout.row()
        rowsub = layout.row(align=True)
        row.prop(scene.topoOpt, "filter_topo")
        row.prop(scene.topoOpt, "no_des_topo")
        # Type of optimization
        row = layout.row()
        row.label("Type of optimization:")
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "single_topo")
        rowsub.prop(scene.topoOpt, "multi_topo")
        # Type of physic
        row = layout.row()
        row.label("Type of physic:")
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "thermal_topo")
        rowsub.prop(scene.topoOpt, "structural_topo")
        rowsub.prop(scene.topoOpt, "fluid_topo")
        # Type of material model
        row = layout.row()
        row.label("Type of material law:")
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "beso_topo")
        rowsub.prop(scene.topoOpt, "simp_topo")
        # Settings for material law
        row = layout.row()
        row.label("Settings for material law:")
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "vol_ratio")
        rowsub.prop(scene.topoOpt, "penalty_value")
        rowsub.prop(scene.topoOpt, "mat_sets")
        # Type of scaling physic
        row = layout.row()
        row.label("Type scaleing physic:")
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "median_topo")
        rowsub.prop(scene.topoOpt, "mid_topo")
        # Type of coupeling
        row = layout.row()
        row.label("Coupel methods:")
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "weight_topo")
        rowsub.prop(scene.topoOpt, "adapt_topo")
        # Weight settings
        row = layout.row()
        row.label("Additional weight factor:")
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "weight_factor")
        row = layout.row()
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "sens_topo")
        rowsub.prop(scene.topoOpt, "dens_topo")
        # Adaption parameters
        row = layout.row()
        row.label("Additional adaption:")
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "start_topo")
        rowsub.prop(scene.topoOpt, "adaptweight_topo")
        rowsub.prop(scene.topoOpt, "adaptiter_topo")
        # Adpation settings
        row = layout.row()
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "n_change")
        rowsub.prop(scene.topoOpt, "n_adapt_iter")
        rowsub.prop(scene.topoOpt, "vol_ratio_add")
        # Adaption parameters
        row = layout.row()
        row.label("Automatic export controll:")
        row = layout.row()
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "dens_selec_value")
        # Export settings
        row = layout.row()
        rowsub = layout.row(align=True)
        rowsub.prop(scene.topoOpt, "stl_topo")
        rowsub.prop(scene.topoOpt, "inp_topo")
        rowsub.prop(scene.topoOpt, "stl_topo_step")
        # Result change
        row = layout.row()
        rowsub.prop(scene.topoOpt, "auto_geo_blend")
        # create a basemesh
        col = layout.column()
        col.operator("object.start_topo_optimization", "Start optimization")


