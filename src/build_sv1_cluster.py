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
pieces=[base]
# Recessed continuous core supports both nodes; rear/side grooves are decorative.
pieces.append(box(-69,-24.2,4.2,138,49.2,51.6))
for z in [4.2,31.2]:
    pieces.append(box(-71,-25,z,142,3.2,26))
    # ears and two left battery modules
    for x in [-74,71]: pieces.append(box(x,-25.5,z,3,4,26))
    for x in [-66,-46]:
        pieces.append(box(x,-27,z+2,18,3,22))
        pieces.append(box(x+2,-27.8,z+20,14,.9,1.4))
    # eight narrow hot-swap bays, with raised latch and lower indicators
    for i in range(8):
        x=-25+i*5.2
        pieces.append(box(x,-26.6,z+2,4.2,2,22))
        pieces.append(box(x+.7,-27.2,z+3,2.8,.8,3))
    # operator panel at right
    pieces.append(box(18,-26,z+2,49,1.4,22))
    # IBM mark sized to remain printable on a 0.4 mm nozzle (plain text)
    pieces.append(lettering('IBM',4.8,.65).rotate((90,0,0)).translate((53,-26,z+18)))
    # Front ears: simplified stripe and screw heads
    for x in [-73.5,71.5]:
        pieces.append(box(x,-26,z+6,2,.6,1))
    # Layered rear shell: 1.4-mm ribs on recessed core, 1.4-mm gaps
    for y in np.arange(-21,25,2.8):
        pieces.append(box(-71,float(y),z,142,1.4,26))

solid=union(pieces)
cuts=[]
for z in [4.2,31.2]:
    for x in [-66,-46]:
        # vent slots on battery covers, with >= 0.8-mm webs
        for j in range(8): cuts.append(box(x+1.2+j*2,-28,z+4,1,1.8,14))
    for i in range(8):
        x=-25+i*5.2
        cuts.append(box(x+1,-27,z+9,2.2,1,11))
    # vent pattern right panel, USB/management ports
    for x in np.arange(20,65,2.4):
        for zz in [4,7]: cuts.append(box(float(x),-26.8,z+zz,1.2,1.4,1.2))
    for x,w in [(37,4),(44,2),(49,4),(56,4)]: cuts.append(box(x,-26.8,z+14,w,1.4,1.5))
    # seam on each top / bottom edge remains shallow and supported
solid=solid-union(cuts)
label=lettering('IBM SVC SV1  /  2-NODE CLUSTER',5,.6)
lb=mesh(label).bounds
label=label.translate((-(lb[1,0]+lb[0,0])/2,-39,4.15))
solid=solid+label

result=mesh(solid)
assert result.is_watertight and result.is_winding_consistent and len(solid.decompose())==1
result.export(ROOT/'models/IBM_SVC_SV1_Cluster.stl')
core='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
ET.register_namespace('',core)
def node(parent,tag,attrs={}):return ET.SubElement(parent,'{'+core+'}'+tag,attrs)
main=ET.Element('{'+core+'}model',{'unit':'millimeter','{http://www.w3.org/XML/1998/namespace}lang':'en-US'})
node(main,'metadata',{'name':'Application'}).text='BambuStudio-02.08.02.61'
node(main,'metadata',{'name':'BambuStudio:3mfVersion'}).text='1'
node(main,'metadata',{'name':'Title'}).text='IBM SVC SV1 - 2 Node Cluster'
node(main,'metadata',{'name':'Designer'}).text='fabianbluemel'
node(main,'metadata',{'name':'LicenseTerms'}).text='Apache-2.0; see LICENSE and NOTICE'
obj=node(node(main,'resources'),'object',{'id':'1','type':'model','name':'IBM SVC SV1 - 2 Node Cluster'})
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
'Metadata/model_settings.config':b'<config><object id="1"><metadata key="name" value="IBM SVC SV1 - 2 Node Cluster"/><metadata key="extruder" value="1"/><part id="1" subtype="normal_part"><metadata key="name" value="IBM SVC SV1 - 2 Node Cluster"/></part></object><plate><metadata key="plater_id" value="1"/><metadata key="plater_name" value="IBM SVC SV1 - 2 Node Cluster"/><metadata key="locked" value="false"/><model_instance><metadata key="object_id" value="1"/><metadata key="instance_id" value="0"/><metadata key="identify_id" value="1"/></model_instance></plate></config>',
'Metadata/custom_gcode_per_layer.xml':b'<custom_gcodes_per_layer><plate><plate_info id="1"/><layer top_z="4.4" type="1" extruder="1" color="#FFFFFF" extra="Load white PLA / Weisses PLA laden" gcode="M400 U1"/><mode value="SingleExtruder"/></plate></custom_gcodes_per_layer>'}
preview=ROOT/'images/sv1_cluster.png'
if preview.exists():entries['Auxiliaries/.thumbnails/thumbnail_3mf.png']=preview.read_bytes()
with zipfile.ZipFile(ROOT/'models/IBM_SVC_SV1_Cluster_P1S.3mf','w',zipfile.ZIP_DEFLATED) as archive:
    for name,data in entries.items():archive.writestr(name,data)
report=dict(size_mm=result.extents.tolist(),watertight=bool(result.is_watertight),winding_consistent=bool(result.is_winding_consistent),connected_components=len(solid.decompose()),physical_test_measurements_available=False)
(ROOT/'models/sv1_cluster-geometry-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
