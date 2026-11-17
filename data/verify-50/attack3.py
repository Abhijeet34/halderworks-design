import sys, json, copy, pathlib
sys.path.insert(0, 'tools')
import ramps
house = json.loads(pathlib.Path('ramps/brands/house.json').read_text())
rows=[]
for c in (0.10,0.15,0.19):
  for h in range(0,360,5):
    b = copy.deepcopy(house); b['hues']['accent'] = {'hue': h, 'chroma': c}
    try: built = ramps.build(b)
    except ramps.BrandError as e: print(h,c,'REFUSED',str(e)[:120]); continue
    fs=[s for s in built['shifts'] if s[0]=='focus']
    if not fs: continue
    d=built['dark']
    de=ramps.de2000(ramps.lab8(*d['accent'][11]), ramps.lab8(*d['green'][12]))
    de8=ramps.de2000(ramps.lab8(*d['accent'][8]), ramps.lab8(*d['green'][11]))
    rows.append((de,h,c,fs[0][2],de8))
rows.sort()
for r in rows[:8]: print('DE(dark acc11 vs green12)=%.2f brand %s c%.2f focus->%s  DE(dark acc8 vs green11)=%.2f'%r)
print(len(rows),'focus-shifted builds')
