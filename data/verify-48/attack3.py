import sys, runpy
exec(open(sys.argv[2]).read().split('print("== Attack 1')[0])
for g in ("--hw-accent-fill","--hw-danger-fill","--hw-success-fill"):
  print(f"  --hw-accent-edge on {g}: " + ", ".join(f"{b}/{t} {ratio('--hw-accent-edge',g,b,t):.2f}" for b in envs for t in ("light","dark","light-more","dark-more")))
run("1h accent button with its edge, nested in a selected row on --hw-accent-fill",
    '@media (prefers-contrast: more) { [data-theme="dark"] .hw-row[aria-selected="true"] .hw-btn--accent { --_bg: var(--hw-accent); --_bd: var(--hw-accent-edge); } }')
