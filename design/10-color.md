# Colour

Every colour a screen paints is a role, and every role names one step of a twelve-step ramp.
The step carries a contrast floor that was solved, written, read back and measured again before the file reached disk, so no colour here was chosen and then checked.
A screen never names a ramp step itself: a role carries its step's floor, and a step chosen by eye carries none.
The component layer names a step in two places, each with its reason beside it in `components/components.css`: the status dot is the step-9 solid of green, amber or red, a mark beside a word that carries the meaning and is certified by nothing, and the dark highlight is a block in mark step 7, which `tests/components.py` measures under `--hw-text` itself.

## Ramps, steps and floors

A brand names a neutral and five to eight hues ([12-brand.md](12-brand.md#the-inputs)), and `tools/ramps.py` gives each one the same twelve steps in each theme:

| step | what it is | its floor |
|---|---|---|
| 1 to 7 | grounds, fills and borders, at fixed lightnesses | none: they are what the floors are measured against |
| 8 | a control boundary, a focus ring, a chart mark | 3:1 against steps 1 to 3 of every ramp |
| 9 | the solid: a button, a selected switch, a stage | the brightest solid whose label, `<ramp>-on-solid`, clears 4.5:1, white unless the brand names the solid's lightness, as the yellow mark and pointback's pencil do with an ink label |
| 10 | the solid under the pointer | step 9 moved 0.04 darker, its label still at 4.5:1 |
| 11 | secondary text, state text, links | 4.5:1 against steps 1 to 5 of every ramp |
| 12 | primary text, and every text under `prefers-contrast: more` | 13:1 against steps 1 to 5 on the gray, 7:1 on a hue so a status word keeps its hue |

"Of every ramp" rather than its own, so accent text holds on a gray fill and muted gray text on an accent fill by construction.
Every floor is measured twice, on the value as solved and on the 8-bit value a display receives, because a pair that clears 3:1 as a float and reads 2.999 in hex is a pair no other checker will agree about.

Three tools hold the floors, and they are three on purpose:

- `tools/ramps.py` solves every step and refuses to write a ramps file in which one floor misses.
- `tools/contrast.py` re-derives every floor and every role with a converter that shares no arithmetic with the build, the CSS Color 4 reference path a browser implements, and carries its own list of what must hold, so a floor cannot be weakened in the same edit as the value it guards.
- `tools/painted.py` renders every pair `tools/contrast.py` certifies in a headless browser and measures the screenshot's pixels; it needs a browser, so it is a local and release check rather than a CI one.

## Roles

`ramps/roles.css` is the whole list, identical for every brand, and the comment beside each role is the description every export carries.
In groups:

| group | roles | job |
|---|---|---|
| neutral | `--hw-bg`, `--hw-bg-subtle`, `--hw-surface`, `--hw-surface-raised`, `--hw-fill`, `--hw-fill-hover`, `--hw-fill-active`, `--hw-line`, `--hw-line-strong`, `--hw-text`, `--hw-text-muted`, `--hw-text-disabled`, `--hw-ink`, `--hw-ink-hover`, `--hw-on-ink` | the page, its surfaces, its lines, its text and the primary action |
| the product's own colour | `--hw-accent`, `--hw-accent-hover`, `--hw-on-accent`, `--hw-accent-text`, `--hw-accent-fill`, `--hw-accent-line`, `--hw-focus` | links, a selection's tint, the focus ring, and one accent solid |
| marks, the house signature | `--hw-mark`, `--hw-on-mark`, `--hw-mark-quiet`, `--hw-insert`, `--hw-insert-fill`, `--hw-delete`, `--hw-delete-fill` | the highlighter and proof marks |
| states | `--hw-success`, `--hw-warning`, `--hw-danger`, each with `-fill` and `-line`; `--hw-danger-solid`, `--hw-danger-hover`, `--hw-on-danger` | a state beside its word, and a destructive action's button |
| chart series | `--hw-chart-1` to `--hw-chart-6` | the series of one chart, in a fixed order |
| scrim | `--hw-scrim` | behind a modal dialog or sheet, never read on |

`--hw-surface` stays white in light whatever the brand's neutral, so data never sits on the tint.
The house neutral is hue 90 at chroma 0.004, a graphite near grey, because a tinted ground biases every reading placed on it; a brand may warm or cool its own.

A new colour role is a choice of step in `ramps/roles.css`, never a new solve, and `tools/contrast.py` refuses a role that it neither certifies on a ground nor exempts with a reason.

## Which ink may sit on which ground

Two roles both existing does not make them a pair.
The permitted pairs are exactly the ones `tools/contrast.py` certifies, in light, dark and both under `prefers-contrast: more`:

| foreground | on | bar |
|---|---|---|
| `--hw-text` | every ground, fill and tint below | 13:1 |
| `--hw-text-muted`, `--hw-accent-text`, `--hw-success`, `--hw-warning`, `--hw-danger`, `--hw-insert`, `--hw-delete` | grounds `--hw-bg`, `--hw-bg-subtle`, `--hw-surface`, `--hw-surface-raised`, `--hw-fill`; fills `--hw-fill-hover`, `--hw-fill-active`; tints `--hw-accent-fill`, the three state fills, `--hw-insert-fill`, `--hw-delete-fill`, `--hw-mark-quiet` | 4.5:1 |
| `--hw-line-strong`, `--hw-focus`, `--hw-ink`, as an edge | the five grounds | 3:1 |
| `--hw-chart-1` to `--hw-chart-6`, as a mark | the five grounds | 3:1 |
| `--hw-text-disabled` | the five grounds | 3:1; WCAG exempts disabled text, and this is what keeps disabled from being invisible |
| `--hw-on-ink`, `--hw-on-accent`, `--hw-on-danger`, `--hw-on-mark` | their own solid, and its hover where it has one | 4.5:1 |

Under `prefers-contrast: more` a text bar under 7:1 rises to 7:1, and a 3:1 bar to 4.5:1; disabled text stays at 3:1.
`--hw-line`, `--hw-accent-line`, the state `-line` roles and `--hw-scrim` are certified as nothing and exempt by name in `tools/contrast.py`: a divider is never a control boundary, a tint's edge sits beside a word, and a scrim is never read on.
A pair not in this table is not a pair you may reach for, and `tests/components.py` refuses a rule in the component layer that sets a text colour and a background outside it.
It allows one exception and measures it itself: `--hw-text` on the dark highlight block, `--hw-mark-7`, held to 4.5:1 in both tiers, so under `prefers-contrast: more` it is the one text pair the layer paints below 7:1.

## How colour is spent

**The primary action is `--hw-ink`**, near-black in light and near-white in dark, with no hue, in every brand; no brand input moves it.
There is one per view.

**The accent does four jobs and no others**: link and accent text (`--hw-accent-text`); a selection's tint (`--hw-accent-fill`, behind a selected table row or an accent badge, with `--hw-accent-line` at a tint's edge); the focus ring (`--hw-focus`); and one accent solid (`--hw-accent`) for the brand moment a product names, such as a download button or a stage.
Where a whole page is one accent, the accent stops meaning anything.

**The states are green, amber and red, and each always sits beside its word.**
A state colour is never decoration, never a brand colour and never progress: a step being finished is a count in words in a neutral colour, `--hw-success` is a check that passed, and `--hw-warning` is a real problem named in words.

**The mark is yellow and covers a few words** ([00-brand-book.md](00-brand-book.md#the-house-signature-marks-on-paper)).

**The scrim dims the page behind a modal dialog or sheet and nothing else**: not a loading state, not a menu.
A scrim claims the rest of the interface is unavailable, which is true exactly when something modal is open.

A brand's accent is held apart from the states by painted distance, so a selected row never reads as a passed one; [12-brand.md](12-brand.md#the-bars-every-brand-is-held-to) has the bars and what each brand clears them by.

## Under `prefers-contrast: more`

`ramps/roles.css` re-points roles rather than defining a second palette: muted text, the focus ring, the solids and the state text move to step 12, which clears 7:1, and the lines darken, `--hw-line` to step 8 and `--hw-line-strong` to step 11.
In dark the ring moves to accent 11, and the danger solid to red 7 under a light label, off the ink.
Chart series 1, 3 and 5 move to step 11, which clears 4.5:1.
`tests/exports.py` holds the cascade, muted text on step 12 included, in every export.

## Chart series

Six series ramps, teal, blue, violet, pink, olive and sky, are the house's in every brand and are not brand inputs, so a chart reads the same series order in every product.
Odd series take step 8 and even series step 11, so neighbours differ in lightness as well as hue.
`tools/contrast.py` holds every series 14 CIEDE2000 from every other series and from each state, and reports what a dichromat sees of the closest pair.
A seventh series is "Other" or another chart, and every series carries a direct label rather than relying on a legend's colour alone.

## Sources

| source | taken | left |
|---|---|---|
| [Radix Colors, understanding the scale](https://www.radix-ui.com/colors/docs/palette-composition/understanding-the-scale) | twelve steps with a job per step, and step 9 as the solid | its hand-tuned values; these are solved to floors |
| [Primer primitives](https://github.com/primer/primitives) | accessibility themes as overrides on a base; the `diffBlob` and `highlight` component tokens | the `-2px` inset focus offset as the default; the ring here sits outside at 2px, and insets only where a box would clip it ([60-accessibility.md](60-accessibility.md#focus)) |
| [Linear, how we redesigned the Linear UI](https://linear.app/now/how-we-redesigned-the-linear-ui) | three inputs per theme | LCH; the ramps are OKLCH |
| [WCAG 2.2, non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html) | 1.4.11's 3:1 for a control boundary and a focus ring | nothing |
| [CSS Color 4 conversions](https://github.com/w3c/csswg-drafts/blob/main/css-color-4/conversions.js) | the reference conversion `tools/contrast.py` implements | nothing |

The measurements this system was first solved against, the 44-site capture, the constraint audit of 2026-09-21 and the five defects the solver caught, are recorded in [the evidence file as it stood on 2026-10-02](https://github.com/Abhijeet34/halderworks-design/blob/a95ed0fed0c544fc12483031a2066f3eecc6b535/design/90-evidence.md), before the ramps replaced the solver.
