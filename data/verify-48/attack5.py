import sys, runpy
exec(open(sys.argv[2]).read().split('print("== Attack 1')[0])
new = run("3d a solid on gray step 9: in light-more it holds 4.5 on surface (4.54) but not on fill (3.90)",
    ".hw-btn--brand { --_bg: var(--hw-gray-9); --_bd: var(--hw-gray-9); }")
hl = [f for f in new if f.startswith("house light-more")]
print("house light-more lines:"); [print("   ", f) for f in hl]
new = run("3e same solid with a halo in --hw-surface (the one ground it holds on): must pass, sitting on its halo",
    ".hw-btn--brand { --_bg: var(--hw-gray-9); --_bd: var(--hw-gray-9); box-shadow: 0 0 0 2px var(--hw-surface); }")
print("tiers refused:", sorted({f.split(':')[0] for f in new}))
