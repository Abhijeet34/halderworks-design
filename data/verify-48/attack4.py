import sys, runpy
exec(open(sys.argv[2]).read().split('print("== Attack 1')[0])
G = contrast.ROLE_GROUNDS
found = None
for b in envs:
  for t in envs[b]:
    bar = contrast.raised(contrast.NON_TEXT) if t.endswith("-more") else contrast.NON_TEXT
    for r in sorted(k for k in envs[b][t] if k.startswith("--hw-")):
        try: vals = {g: ratio(r, g, b, t) for g in G}
        except Exception: continue
        if max(vals.values()) >= bar > min(vals.values()):
            print(" ", b, t, r, {g: round(x,2) for g,x in vals.items()}); found = found or (b,t,r)
print("first:", found)
b,t,r = ("house","light-more","--hw-gray-9")
run(f"3c accent button whose edge is {r}: holds {b} {t} on some grounds, not on others",
    "", replace=("--_bd: var(--hw-accent-edge); --_bgh: var(--hw-accent-hover);", f"--_bd: var({r}); --_bgh: var(--hw-accent-hover);"))
