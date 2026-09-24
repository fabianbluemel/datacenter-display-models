# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 fabianbluemel
"""Verify every new P1S slice and keep an auditable collection report."""
from pathlib import Path
import json,re,zipfile,hashlib
ROOT=Path(__file__).resolve().parents[1]
models=['IBM_SVC_SV1_Cluster','IBM_SVC_SV1_SingleNode','IBM_SVC_SV2_SingleNode','Dell_Compellent_SC8000']
report={'Brocade_X6-8':json.loads((ROOT/'models/slice-check.json').read_text())}
for name in models:
    folder=ROOT/'build'/('slice-'+name)
    r=json.loads((folder/'result.json').read_text())
    g=(folder/'plate_1.gcode').read_text()
    assert r['return_code']==0 and r['wall_loops']==2 and r['sparse_infill_density']==15
    assert len(re.findall(r'^M400 U1\s*$',g,re.M))==1
    p=g.index('\nM400 U1\n')
    assert re.search(r'22/\d+',g[p-300:p])
    assert '; printer_model = Bambu Lab P1S' in g
    plate=r['sliced_plates'][0]
    assert plate['filament_change_times']==0
    with zipfile.ZipFile(ROOT/'models'/(name+'_P1S.3mf')) as z:
        assert not any('Model Pictures' in n or n.startswith('3D/Objects/') for n in z.namelist())
    report[name]=dict(slicing_success=True,height_mm=plate['objects'][0]['bbox']['height'],manual_pauses=1,pause_before_layer=22,estimated_minutes=round(plate['total_predication']/60),estimated_grams=round(sum(f['total_used_g'] for f in plate['filaments']),1),stl_sha256=hashlib.sha256((ROOT/'models'/(name+'.stl')).read_bytes()).hexdigest())
report['photo_evidence']={'X6-8_and_SV1':'images/photos/datacenter-display-models.jpg','SV1_assembled_with_light':'images/photos/ibm-svc-sv1-illuminated-display.jpg','measured_fit_tolerances_documented':False}
(ROOT/'models/collection-check.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
