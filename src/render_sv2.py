# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 fabianbluemel
from pathlib import Path
import numpy as np
import trimesh
from matplotlib.font_manager import findfont, FontProperties
ROOT=Path(__file__).resolve().parents[1]
from PIL import Image, ImageDraw, ImageFont
m=trimesh.load_mesh(ROOT/'models/IBM_SVC_SV2_SingleNode.stl')
W,H=1600,1120
forward=np.array([.32,-1,.46]);forward/=np.linalg.norm(forward)
right=np.cross([0,0,1],forward);right/=np.linalg.norm(right)
up=np.cross(forward,right)
v=m.vertices@np.stack([right,up,forward],axis=1)
scale=min((W-120)/np.ptp(v[:,0]),(H-240)/np.ptp(v[:,1]))
v[:,:2]-=(v[:,:2].max(0)+v[:,:2].min(0))/2
v[:,0]=v[:,0]*scale+W/2;v[:,1]=-v[:,1]*scale+H/2+25
depth=np.full((H,W),-np.inf);rgb=np.full((H,W,3),[239,242,246],dtype=np.uint8)
light=np.array([-.5,-.7,1]);light/=np.linalg.norm(light)
for idx,(face,n) in enumerate(zip(m.faces,m.face_normals)):
    p=v[face];x0=max(0,int(np.floor(p[:,0].min())));x1=min(W-1,int(np.ceil(p[:,0].max())))
    y0=max(0,int(np.floor(p[:,1].min())));y1=min(H-1,int(np.ceil(p[:,1].max())))
    if x1<x0 or y1<y0:continue
    xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
    a,b,c=p;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
    if abs(den)<1e-8:continue
    u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
    t=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den
    w=1-u-t;z=u*a[2]+t*b[2]+w*c[2]
    mask=(u>=-1e-8)&(t>=-1e-8)&(w>=-1e-8)&(z>depth[y0:y1+1,x0:x1+1])
    depth[y0:y1+1,x0:x1+1][mask]=z[mask]
    color=np.array([238,239,240] if m.triangles_center[idx,2]>4.2001 else [37,39,43])*(.48+.52*max(0,float(n@light)))
    rgb[y0:y1+1,x0:x1+1][mask]=color.astype(np.uint8)
im=Image.fromarray(rgb);d=ImageDraw.Draw(im)
font=findfont(FontProperties(family='DejaVu Sans'));bold=findfont(FontProperties(family='DejaVu Sans',weight='bold'))
d.text((W/2,38),'IBM SVC SV2 - Single Node',font=ImageFont.truetype(bold,42),fill='#213343',anchor='mt')
d.text((W/2,98),'STL render - not a photo | One manual colour change',font=ImageFont.truetype(font,24),fill='#536575',anchor='mt')
d.text((W/2,H-58),'163.4 x 92.4 x 30.2 mm | Black base / white chassis',font=ImageFont.truetype(font,23),fill='#536575',anchor='mt')
im.save(ROOT/'images/sv2.png')
