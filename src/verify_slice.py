# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 fabianbluemel
"""Verify a local Bambu Studio CLI slice under build/slice before release."""
from pathlib import Path
import json,re,zipfile,hashlib
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'build/slice/result.json').read_text())
g=(ROOT/'build/slice/plate_1.gcode').read_text()
assert r['return_code']==0 and r['wall_loops']==2 and r['sparse_infill_density']==15
assert len(re.findall(r'^M400 U1\s*$',g,re.M))==1
p=g.index('\nM400 U1\n')
assert re.search(r'22/\d+',g[p-300:p])
assert '; printer_model = Bambu Lab P1S' in g
assert r['sliced_plates'][0]['filament_change_times']==0
assert abs(r['sliced_plates'][0]['objects'][0]['bbox']['height']-100)<.001
with zipfile.ZipFile(ROOT/'models/Brocade_X6-8_P1S.3mf') as z:
    assert not any('Model Pictures' in n or n.startswith('3D/Objects/') for n in z.namelist())
    for n in ['3D/3dmodel.model','Metadata/project_settings.config']:
        content=z.read(n).decode()
        assert 'C:\\' not in content and 'C:/' not in content and 'IMG_09' not in content
plate=r['sliced_plates'][0]
report=dict(slicing_success=True,printer='Bambu Lab P1S 0.4 mm',height_mm=100,layer_height_mm=.2,wall_loops=2,infill_percent=15,manual_pauses=1,pause_before_layer=22,automatic_filament_changes=0,estimated_seconds=plate['total_predication'],estimated_grams=sum(f['total_used_g'] for f in plate['filaments']),physical_print_tested=False,stl_sha256=hashlib.sha256((ROOT/'models/Brocade_X6-8_100mm.stl').read_bytes()).hexdigest())
(ROOT/'models/slice-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
