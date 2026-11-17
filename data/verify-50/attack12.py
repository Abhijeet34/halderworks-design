import sys, json, copy, pathlib, subprocess, tempfile
sys.path.insert(0, 'tools')
import ramps
house = json.loads(pathlib.Path('ramps/brands/house.json').read_text())
def run(label, accent):
    b = copy.deepcopy(house); b['hues']['accent'] = accent
    with tempfile.TemporaryDirectory() as t:
        p = pathlib.Path(t)/'atk.json'; p.write_text(json.dumps(b))
        r = subprocess.run([sys.executable,'tools/ramps.py',str(p),'--out',t],capture_output=True,text=True)
        print(f'## {label}: accent={accent}\nramps.py rc={r.returncode}')
        print('  ' + '\n  '.join((r.stdout+r.stderr).strip().splitlines()[-4:]))
        css = pathlib.Path(t)/'atk.tokens.css'
        if css.exists():
            c = subprocess.run([sys.executable,'tools/contrast.py',str(css)],capture_output=True,text=True)
            print(f'contrast.py rc={c.returncode}', (c.stdout+c.stderr).strip().splitlines()[-1][:200])
            for th, rs in ramps.parse(css.read_text()).items():
                print('  ', th, {s: rs['accent'][s][2] for s in (3,7,8,9,10,11,12)})
# attack 1: exactly on danger's hue (27) at several chromas
for c in (0.05, 0.10, 0.15, 0.19, 0.25): run(f'A1 hue = --hw-danger hue 27, chroma {c}', {'hue':27,'chroma':c})
run('A1 identical to red ramp + named solid', {'hue':27,'chroma':0.19,'solid':{'light':0.6,'dark':0.6}})
# attack 2: both sides fail all the way round
for c in (0.0, 0.001, 0.005, 0.02, 0.03, 0.04): run(f'A2 near-grey chroma {c}', {'hue':262,'chroma':c})
