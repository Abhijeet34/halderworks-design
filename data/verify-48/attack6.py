import sys, runpy
exec(open(sys.argv[2]).read().split('print("== Attack 1')[0])
run("B4 alias cycle (--_a -> --_b -> --_a) must not hang or crash", ".hw-btn--brand { --_a: var(--_b); --_b: var(--_a); --_bg: var(--_a); }")
run("B5 alias declared in the component base rule, read by a variant", ".hw-chip { --_solid: var(--hw-accent); }\n.hw-chip--brand { --_bg: var(--_solid); }")
run("B6 alias declared, fallback is the solid: browser uses the alias (non-solid) -> no refusal expected", ".hw-btn--brand { --_x: var(--hw-surface); --_bg: var(--_x, var(--hw-accent)); }")
run("B7 alias undeclared, fallback the solid -> refused expected", ".hw-btn--brand { --_bg: var(--_nowhere, var(--hw-accent)); }")
run("B8 alias set by an ancestor rule (custom properties inherit): .hw-callout { --_s: accent } .hw-callout .hw-btn--x { --_bg: var(--_s) }", ".hw-callout { --_s: var(--hw-accent); }\n.hw-callout .hw-btn--x { --_bg: var(--_s); }")
run("B9 later state rule drops the edge through an alias: .hw-pin:hover { --_r: var(--hw-surface); box-shadow: 0 0 0 2px var(--_r) }", ".hw-pin:hover { --_r: var(--hw-surface); box-shadow: 0 0 0 2px var(--_r); }")
run("B10 three-deep alias in the edge: accent button --_bd through --_e1->--_e2->--_e3 = --hw-line", "", replace=("--_bd: var(--hw-accent-edge); --_bgh: var(--hw-accent-hover);", "--_e3: var(--hw-line); --_e2: var(--_e3); --_e1: var(--_e2); --_bd: var(--_e1); --_bgh: var(--hw-accent-hover);"))
