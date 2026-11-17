import sys, runpy
exec(open(sys.argv[2]).read().split('print("== Attack 1')[0].replace("root = sys.argv[1]", "root = sys.argv[1]"))
for g in ("--hw-danger-fill","--hw-accent-fill","--hw-warning-fill"):
  for s in ("--hw-danger-solid","--hw-accent","--hw-ink"):
    print(f"  {s} on {g}: " + ", ".join(f"{b}/{t} {ratio(s,g,b,t):.2f}" for b in envs for t in ("light","dark","light-more","dark-more")))
run("1e danger-solid button inside a danger callout (tinted ground), dark under more",
    '@media (prefers-contrast: more) { [data-theme="dark"] .hw-callout--danger .hw-btn--danger-solid { --_bg: var(--hw-danger-solid); --_bd: var(--hw-danger-solid); } }')
run("1f same, no media, every tier", '.hw-callout--danger .hw-btn--danger-solid { --_bg: var(--hw-danger-solid); --_bd: var(--hw-danger-solid); }')
run("1g same, but the rule names the tinted ground as a halo", '.hw-callout--danger .hw-btn--danger-solid { --_bg: var(--hw-danger-solid); --_bd: var(--hw-danger-solid); box-shadow: 0 0 0 2px var(--hw-danger-fill); }')
