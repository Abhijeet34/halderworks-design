import sys, runpy, re
root = sys.argv[1]
sys.argv = ["x"]
m = runpy.run_path(root + "/tests/components.py", run_name="not_main")
text = open(root + "/components/components.css").read()
envs = m["ramp_envs"](); rules_of = m["rules_of"]; check_fills = m["check_fills"]; fills_in = m["fills_in"]
contrast = m["contrast"]
base = set(check_fills(rules_of(text), envs)[0])
def run(label, css, replace=None, tiers=None):
    t = text.replace(*replace) if replace else text + "\n" + css
    if replace: assert replace[0] in text, replace[0]
    rs = rules_of(t)
    new = [f for f in check_fills(rs, envs)[0] if f not in base]
    measured = [x for x in fills_in(rs) if x not in fills_in(rules_of(text))]
    print(f"\n### {label}\ninput: {css or replace}\nmeasured as: {measured[:4]}")
    print(f"result: {'REFUSED' if new else 'PASSED (not refused)'} ({len(new)} new failures)")
    for f in new[:4]: print("   ", f)
    return new
def ratio(a, g, brand, tier):
    e = envs[brand][tier]; return min(contrast.ratio(contrast.resolve(a, e), contrast.resolve(g, e)))

print("== Attack 1: fill on a tinted ground inside a dark prefers-contrast block")
for b in envs:
    print(f"  {b} dark-more: --hw-accent on --hw-accent-fill {ratio('--hw-accent','--hw-accent-fill',b,'dark-more'):.2f}, "
          f"--hw-accent-edge on --hw-accent-fill {ratio('--hw-accent-edge','--hw-accent-fill',b,'dark-more'):.2f}, "
          f"--hw-danger-solid on --hw-danger-fill {ratio('--hw-danger-solid','--hw-danger-fill',b,'dark-more'):.2f}")
run("1a accent button on a selected row (tinted ground by nesting), dark under more",
    '@media (prefers-contrast: more) { [data-theme="dark"] .hw-row[aria-selected="true"] .hw-btn--accent { --_bg: var(--hw-accent); } }')
run("1b pin haloed in a tinted ground (its halo names the ground), dark under more",
    '@media (prefers-contrast: more) { [data-theme="dark"] .hw-pin { box-shadow: inset 0 0 0 var(--hw-border-w) var(--hw-accent-edge), 0 0 0 2px var(--hw-accent-fill); } }')
run("1c dark-more override that swaps the accent button edge for a tinted role",
    '@media (prefers-contrast: more) { [data-theme="dark"] .hw-btn--accent { --_bd: var(--hw-accent-fill); } }')
run("1d same override scoped to light only (media is ignored, so does it still measure dark-more?)",
    '@media (prefers-contrast: more) { [data-theme="light"] .hw-btn--accent { --_bd: var(--hw-accent-fill); } }')

print("\n== Attack 2: fill token that is an alias of another alias")
run("2a private alias chain: --_brand -> --_solid -> --hw-accent",
    ".hw-btn--brand { --_solid: var(--hw-accent); --_brand: var(--_solid); --_bg: var(--_brand); --_bd: var(--_brand); }")
run("2b direct, for comparison", ".hw-btn--brand { --_bg: var(--hw-accent); --_bd: var(--hw-accent); }")
run("2c role alias of alias: --hw-accent-hover (role -> step) painted as a meter bar",
    "", replace=("var(--_live, var(--hw-accent-edge))", "var(--_live, var(--hw-accent-hover))"))
run("2d fill named through a fallback chain var(--_x, var(--_y, var(--hw-accent)))",
    ".hw-btn--brand { --_bg: var(--_x, var(--_y, var(--hw-accent))); --_bd: var(--_x, var(--_y, var(--hw-accent))); }")

print("\n== Attack 3: a fill that passes on one ground and fails on another")
for b in envs:
  for t in ("light",):
    print(f"  {b} {t}: --hw-line-strong on " + ", ".join(f"{g} {ratio('--hw-line-strong',g,b,t):.2f}" for g in contrast.ROLE_GROUNDS))
run("3a accent button edged in --hw-line (a hairline) instead of the edge role",
    "", replace=("--_bd: var(--hw-accent-edge); --_bgh: var(--hw-accent-hover);", "--_bd: var(--hw-line); --_bgh: var(--hw-accent-hover);"))
run("3b toast's inner button: GROUND_OF ink; give it an accent solid there",
    ".hw-toast .hw-btn { --_bgh: var(--hw-accent); }")
