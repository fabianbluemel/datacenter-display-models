# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 fabianbluemel
from pathlib import Path
import json, zipfile
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
import manifold3d as md
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
ROOT=Path(__file__).resolve().parents[1]
(ROOT/'models').mkdir(exist_ok=True)
def box(x,y,z,dx,dy,dz):
    return md.Manifold.cube((dx,dy,dz)).translate((x,y,z))
def union(items): return md.Manifold.batch_boolean(items,md.OpType.Add)
def rounded(w,d,r,h):
    pts=[]
    for cx,cy,start in [(w/2-r,d/2-r,0),(-w/2+r,d/2-r,90),(-w/2+r,-d/2+r,180),(w/2-r,-d/2+r,270)]:
        for a in np.linspace(start,start+90,13): pts.append((cx+r*np.cos(np.deg2rad(a)),cy+r*np.sin(np.deg2rad(a))))
    return md.CrossSection([pts]).extrude(h)
def lettering(text,size,depth):
    p=TextPath((0,0),text,size=size,prop=FontProperties(family='DejaVu Sans',weight='bold'))
    polygons=p.to_polygons()
    return md.CrossSection(polygons,md.FillRule.EvenOdd).extrude(depth)
def mesh(m):
    a=m.to_mesh();return trimesh.Trimesh(np.array(a.vert_properties)[:,:3],np.array(a.tri_verts),process=True)

# The original standard bottom has a 160 x 89 mm through opening,
# R2.5 corners, and a 164 x 93 mm upper rebate, 2.5 mm deep.
# 0.3 mm lateral clearance; flange rests on original ledge.
base=rounded(159.4,88.4,2.5,1.8)+box(-81.7,-46.2,1.8,163.4,92.4,2.4)
# Front proportions ~437.4 : 612.3; shortened depth for display stand.
z=4.2
pieces=[box(-50,-22,z,100,48,140)]
cuts=[]
# Outer rack ears, top ventilated plenum and lower branding rail.
for x in [-53,50]:
    pieces.append(box(x,-24,z,3,4,140))
    for h in [5,44,92,134]:cuts.append(box(x+.8,-24.1,z+h,1.4,1,2.4))
pieces.extend([box(-50,-24,z+116,100,3,24),box(-50,-25,z,100,4,9)])
for row in range(6):
    for col in range(31):cuts.append(box(-47+col*3,-24.1,z+119+row*3,1.8,1.1,1.7))
# Two half-height CP modules at far left, ten full-height blades beside them.
for h in [11,63]:
    pieces.append(box(-48,-24,z+h,8,3,51))
    for hh in [9,17,25]:cuts.append(box(-46.8,-24.1,z+h+hh,4.6,1.1,3))
    pieces.append(box(-46,-25,z+h+3,3,2,3))
    for hh in range(33,46,3):cuts.append(box(-46.8,-24.1,z+h+hh,4.6,1.1,1.2))
for slot in range(10):
    x=-39+slot*8.7
    pieces.append(box(x,-24,z+11,7.7,3,103))
    for h in [13,108]:pieces.append(box(x+1.5,-25,z+h,4.5,2,3.5))
    if slot in [4,5]:
        # CR32-8: sixteen larger ICL sockets per blade.
        for row in range(8):
            for col in range(2):cuts.append(box(x+.9+col*3.2,-24.1,z+26+row*8.6,2.1,1.1,4))
    else:
        # FC32-48: 2 columns x 24 recessed sockets.
        for row in range(24):
            for col in range(2):cuts.append(box(x+.9+col*3.2,-24.1,z+22+row*3.45,2.1,1.1,1.8))
# Supported cable comb along the bottom; shallow side/rear ventilation.
for x in np.arange(-46,48,5):pieces.append(box(float(x),-27,z+8.5,2,4,3))
for y in np.arange(-17,23,3.5):
    cuts.append(box(49.1,float(y),z+12,1,1.5,116))
    cuts.append(box(-50.1,float(y),z+12,1,1.5,116))
for x in np.arange(-44,46,4):cuts.append(box(float(x),25.1,z+14,2,1,110))
solid=union(pieces)-union(cuts)
brand=lettering('BROCADE X6-8',4.5,.6).rotate((90,0,0))
bb=mesh(brand).bounds
solid=solid+brand.translate((-(bb[0,0]+bb[1,0])/2,-24.9,z+2))
# Uniform chassis scaling about its bottom; preserve the mating base and label.
chassis_scale=(100.0-z)/140.0
solid=solid.translate((0,0,-z)).scale((chassis_scale,)*3).translate((0,0,z))
solid=solid.rotate((0,0,-10)).translate((-28,5,0))
solid=base+solid
# A compact, left-aligned typographic block on the right balances the chassis.
for text,size,y in [('BROCADE',6.8,12),('X6-8',12,-2),('SAN DIRECTOR',3.8,-12)]:
    label=lettering(text,size,.85)
    bb=mesh(label).bounds
    solid=solid+label.translate((23-bb[0,0],y,4.15))
solid=solid+box(23,-17,4.15,43,.9,.85)
result=mesh(solid)
assert result.is_watertight and result.is_winding_consistent and len(solid.decompose())==1
assert result.bounds[1,2]<=100.00001 and abs(result.extents[2]-100)<.00001

result.export(ROOT/'models/Brocade_X6-8_100mm.stl')
core='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',core)
def node(parent,tag,attrs={}):return ET.SubElement(parent,'{'+core+'}'+tag,attrs)
main=ET.Element('{'+core+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
node(main,'metadata',{'name':'Application'}).text='BambuStudio-02.08.02.61'
node(main,'metadata',{'name':'BambuStudio:3mfVersion'}).text='1'
node(main,'metadata',{'name':'Title'}).text='Brocade X6-8 display - 100 mm'
node(main,'metadata',{'name':'Designer'}).text='fabianbluemel'
node(main,'metadata',{'name':'LicenseTerms'}).text='Apache-2.0; see LICENSE and NOTICE'
obj=node(node(main,'resources'),'object',{'id':'1','type':'model','name':'Brocade X6-8 display'})
me=node(obj,'mesh');vs=node(me,'vertices');fs=node(me,'triangles')
for v in result.vertices:node(vs,'vertex',dict(zip('xyz',[f'{c:.6f}' for c in v])))
for f in result.faces:node(fs,'triangle',dict(zip(['v1','v2','v3'],map(str,f))))
node(node(main,'build'),'item',{'objectid':'1','transform':'1 0 0 0 1 0 0 0 1 128 128 0'})
settings=json.loads((ROOT/'third_party/bambu/p1s-settings.json').read_text(encoding='utf-8'))
entries={
'[Content_Types].xml':b'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>',
'_rels/.rels':b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>',
'3D/3dmodel.model':ET.tostring(main,encoding='utf-8',xml_declaration=True),
'Metadata/project_settings.config':json.dumps(settings,indent=2).encode(),
'Metadata/model_settings.config':b'<config><object id="1"><metadata key="name" value="Brocade X6-8 display"/><metadata key="extruder" value="1"/><part id="1" subtype="normal_part"><metadata key="name" value="Brocade X6-8 display"/></part></object><plate><metadata key="plater_id" value="1"/><metadata key="plater_name" value="X6-8 100 mm"/><metadata key="locked" value="false"/><model_instance><metadata key="object_id" value="1"/><metadata key="instance_id" value="0"/><metadata key="identify_id" value="1"/></model_instance></plate></config>',
'Metadata/custom_gcode_per_layer.xml':b'<custom_gcodes_per_layer><plate><plate_info id="1"/><layer top_z="4.4" type="1" extruder="1" color="#FFFFFF" extra="Load white PLA / Weisses PLA laden" gcode="M400 U1"/><mode value="SingleExtruder"/></plate></custom_gcodes_per_layer>'}
preview=ROOT/'images/preview.png'
if preview.exists():entries['Auxiliaries/.thumbnails/thumbnail_3mf.png']=preview.read_bytes()
with zipfile.ZipFile(ROOT/'models/Brocade_X6-8_P1S.3mf','w',zipfile.ZIP_DEFLATED) as archive:
    for name,data in entries.items():archive.writestr(name,data)
report=dict(size_mm=result.extents.tolist(),watertight=bool(result.is_watertight),winding_consistent=bool(result.is_winding_consistent),connected_components=len(solid.decompose()),physical_print_tested=False)
(ROOT/'models/geometry-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
