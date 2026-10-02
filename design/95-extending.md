# Extending the system

A product will need something this system does not have.
That is expected, and there is one right way to do it and several wrong ones.

**The rule: extend in your own namespace, never edit `hw-`.**

## The decision, in order

Stop at the first one that applies.

| the situation | what to do |
|---|---|
| the value exists under another name | use it. `--hw-surface-sunken` is the skeleton fill, the code-block ground and the input rest fill; it does not need three aliases |
| you need a value *between* two steps | you do not. Pick one of the two. A 13px gap and a 14px gap are not perceptually different |
| you need a composition of existing tokens | build it in your product's CSS from `hw-` tokens. A `--quoth-toolbar-height: calc(var(--hw-control-h) + var(--hw-space-16))` is correct and needs no permission |
| you need a genuinely new *kind* of thing | add it in your namespace, per the recipe below, and report it |
| the system's value is wrong for everybody | report it. Do not fix it locally, because then two products disagree and neither knows |

## A product's own namespace

One prefix per product, derived from its name: `--quoth-`, `--gates-`, `--foliot-`.

```css
/* quoth/tokens.css - loaded after the house variables.css, never instead of it */
:root {
  /* A composition: no new value, and it stays correct when the house value changes. */
  --quoth-waveform-h: calc(var(--hw-row-h) * 3);

  /* A genuinely product-specific concept the house system has no opinion about. */
  --quoth-speaker-1: var(--hw-chart-1);
  --quoth-speaker-2: var(--hw-chart-2);
}
```

Two rules:

- **Never redefine an `hw-` token.**
  `--hw-radius-md: 8px` in a product stylesheet is a fork wearing the system's name, and every component that reads it now behaves differently in that product with nothing recording why.
- **Prefer a composition to a constant.**
  A token defined as `calc()` over house tokens tracks the system. A token defined as `24px` stops tracking it the day the scale moves.

## A brand file, and nothing else

A product's identity is a **brand file**, `ramps/brands/<product>.json`: a neutral, five to eight named hues, and optionally a shape register, an icon stroke and faces, built into the house's token names, never a stylesheet of overrides.
[12-brand.md](12-brand.md) owns the inputs, their bounds and the product brands.
papertrace is the worked example here:

```json
{
  "note": "papertrace's report is set as a document: ...",
  "shape": "crisp",
  "faces": {"sans": "system serif", "display": "system serif", "read": "system serif"},
  "neutral": {"hue": 250, "chroma": 0.005},
  "hues": {
    "accent": {"hue": 252, "chroma": 0.12},
    "mark": {"hue": 100, "chroma": 0.19, "solid": {"light": 0.9, "dark": 0.88}},
    "red": {"hue": 25, "chroma": 0.19},
    "amber": {"hue": 70, "chroma": 0.16},
    "green": {"hue": 150, "chroma": 0.14}
  }
}
```

```bash
python3 tools/ramps.py                                        # writes ramps/tokens/papertrace.tokens.css
python3 tools/contrast.py ramps/tokens/papertrace.tokens.css    # verify it independently
python3 tools/export.py examples/papertrace                     # the brand's exports/
```

**The build refuses to emit if a floor does not hold.**
That refusal is the feature: the solver it replaced caught three defects in this system's own first pass with it, including a dark focus ring at 2.56:1 on `--hw-surface-raised`.

What it does with a brand file, in order: every key is checked against its bound and the roster, and a key that is not an input, an `hw-` token included, is refused.
Every hue gets twelve steps per theme: 1 to 7 at fixed lightnesses, 8, 11 and 12 solved to their floors against every ramp's grounds, 9 the brightest solid that carries a white label unless the brand names its lightness, and 10 a hover step below it.
Every value is quantised to the form it is written in before it is measured, the written file is parsed back and measured again, and only then does it reach disk.

**What a brand paints must stand apart from the state drawn in the same form**: the selected-row fill from each state's fill, the primary from the danger solid, and the focus ring from the error text and from a control's own edge, each in CIEDE2000 on the 8-bit value, which [10-color.md](10-color.md#the-three-bars-the-accent-is-held-to) owns.
A product cannot take hue 150 for its accent, because its selected row would be a passed row, and `tools/contrast.py` says so with the number rather than refusing on principle:

```text
FAIL  h150: light: --hw-accent-fill sits 0.4 CIEDE2000 from --hw-success-fill at 8-bit, below 5: a brand fill that reads as a state
```

Its accent text is reported rather than refused: every state carries a glyph and a word.

That is a measurement rather than a veto, and it is executable rather than merely written down.

**Do not hand-edit a file in `ramps/tokens/` or `exports/`,** the house's or a brand's. Both are the build's output, and the brand file is the source.

## A colour of the product's own

A product sometimes needs a colour for a concept the house has no opinion about, and quoth's open microphone is the case that exists.
A composition of `hw-` tokens is still the first answer.
When no house colour means the thing, the product names a hue of its own in its brand file, and the build gives it twelve steps like every other hue, for the same reason the accent is built rather than hand-picked.
The product then names the step its concept uses in its own namespace, `--quoth-live: var(--hw-live-8)` for a mark at 3:1 on every ground, step 11 for text at 4.5:1.

```json
"live": {"hue": 48, "chroma": 0.19}
```

A product hue inherits the step floors by construction: step 8 clears 3:1 and step 11 4.5:1 against steps 1 to 5 of every ramp, in both themes, and `tools/contrast.py` certifies it with every other ramp.
A brand may name up to three hues of its own, because a brand carries at most eight and five of them are the house's roles.

### How a product colour is held apart

Decided by the system's owner on 2026-09-28, on the house-live-orange audit of that day: a product colour is a colour of its own when it sits **14 CIEDE2000** from each state on the 8-bit value a display receives, the accent's ink bar, calibrated where teal 172 at 10.5 read as a state and 186 at 14.3 as its own colour ([10-color.md](10-color.md#the-three-bars-the-accent-is-held-to)).
The retired solver also held a guard of 5.0 in hue and chroma with lightness left out, which caught a state moved only in lightness.

`tools/contrast.py` measures a brand's own hue at steps 8 and 11 against the same steps of the three state ramps, in both themes, and **reports** the closest; it does not refuse it.
The ramps put every hue at one lightness per step, so the guard that caught a state moved in lightness has nothing left to catch, and the CIEDE2000 distance is the one that remains.
It is reported rather than refused because quoth's live orange, decided by its own record, misses it against amber at every step, below; a refusal would block the product's decision rather than inform it, and the word beside the mark carries the state either way.

Colour-vision separation is reported and never refused on, as for the accent: the house's own states already collapse under deuteranopia and are told apart by their words ([10-color.md](10-color.md#the-three-bars-the-accent-is-held-to)).

### The worked example, quoth's live colour

The microphone-open state takes its own colour, decided by the system's owner on 2026-09-21.
The accent already marks selection, focus and the active tab, so a shared accent makes "the microphone is open" read as "this row is selected", and recording red sits on `--hw-danger`.
quoth's decision D-062 moved it from a violet to the orange of the open microphone, and D-059 took the word out of it, so it is a mark.

Built from `ramps/brands/quoth.json` as hue 48 at chroma 0.19, as `tools/contrast.py` measures it:

| step | light | dark | closest state, CIEDE2000, light / dark |
|---|---|---|---|
| 8, a mark at 3:1 | `#DC640C` | `#AD4C01` | amber 12.92 / 11.71 |
| 9, a solid | `#C25601` | `#C25601` | amber 12.31 / 12.31 |
| 11, text at 4.5:1 | `#A14600` | `#F36E01` | amber 11.01 / 13.41 |

Every step sits under the 14 from amber, by 3 at worst, and clears red by 15.02 or more and green by 49.41.
The solver held quoth's live colour 15.6 from `hw-warning` by solving its lightness away from amber's; a ramp step cannot, because every hue's step 11 sits at one lightness.
This is a finding, not a decision this file makes: either the orange moves off amber, which is quoth's to decide, or the bar is re-calibrated for ramps.

Colour is never the only carrier of the state: [15-color-combinations.md](15-color-combinations.md) puts a word beside every semantic colour and [55-iconography.md](55-iconography.md#colour) puts one beside every icon.
So the live state is always the word `Recording`, in a house text colour, beside the mark in `--quoth-live`.
It does not pulse, because [40-motion.md](40-motion.md) lets only a determinate progress indicator loop, and the change is announced in a `role="status"` region, which quoth provides.
It is not certified on the menu-bar item, which sits on a ground the house does not own.

## Adding a component

A component belongs in the house system when **two products need it**.
Before that it lives in the product that needs it, built from house tokens.

A house component card answers four things, in this order, and [65-components.md](65-components.md) is the shape to copy:

1. **What it is for, and what it is not.** "Use a data table when the columns are the point; use list rows when the row is."
2. **Anatomy**, in tokens. Not pixels, not a screenshot.
3. **Rules**, each one a thing that will otherwise go wrong.
4. **What the consumer provides.** The semantics, the keyboard handling, the state that only the product knows.

A component card that does not say what the consumer provides is a card that will be implemented four times with four different accessibility stories.

## Adding a token

A new token needs four things or it is not ready:

1. **A name in the `hw-` scale it belongs to**, matching the existing pattern.
2. **A usage note that says where it may be used and where it may not.**
3. **A number with a derivation.** Measured off something, solved to a target, or derived from another token. "It looked right" is the failure this whole system replaces.
4. **Its row in the verification.** A colour token is a role in `ramps/roles.css` naming a ramp step, whose floor it inherits, and `tools/contrast.py` must certify it: a role certified by nothing is refused. A size, space, layout or motion token joins its family in `ramps/scales.css` with its description as the comment beside it, and `tests/exports.py` holds a space or size to the 4px unit. Nothing joins `exports/` directly, because it is generated. A product's own colour is a hue in its brand file, [above](#a-colour-of-the-products-own).

## Reporting a gap

A gap is a finding, not a blocker.
Ship the screen with the nearest house value, and say in the same breath what you needed:

> Used `--hw-space-24` for the pane divider; the pane wants about 28px and the scale has no step there.

That sentence is worth more than a correct-looking screen with `28px` written into it, because the next person hits the same gap and either finds the report or invents a second number.

## Loading the system in a product

```css
@import "hw/fonts/fonts.css";   /* the house faces, vendored beside it with their OFL texts */
@import "hw/variables.css";     /* exports/variables.css, or a brand's examples/<brand>/exports/variables.css */
@import "quoth/tokens.css";     /* the product's own namespace, after */
```

Copy the whole `fonts/` directory, because `fonts.css` names its files by relative URL.
A brand whose faces are system stacks loads no `fonts.css`; a brand that names a self-hosted roster face the house does not vendor, such as quoth's Martian Mono, adds its own `@font-face` for the file the roster pins, the same way.

No font is loaded from a font service: three of the products this system serves make no network request or refuse one by policy, and a system that told them to load a stylesheet from a CDN was a system they could not follow.

Nothing else is required.
Nothing is installed and nothing is built. The component layer is two more files loaded the same way, [components/components.css](../components/components.css) after the variables and [components/radiogroup.js](../components/radiogroup.js) once, and [64-component-sheets.md](64-component-sheets.md#the-component-layer) shows the three lines.

## For an agent building against this system

If you are a model that has never seen the conversation this system came out of, this is the whole contract:

1. Read [SKILL.md](../SKILL.md). Its table says which file answers the task in front of you.
2. Load `fonts/fonts.css` and `exports/variables.css`, and use `var(--hw-*)` for every colour, size, radius, duration, breakpoint and z-index.
3. Check every ink-on-ground pair against [15-color-combinations.md](15-color-combinations.md) before you write it, and every control boundary against the 3:1 table in the same file.
4. Run the thirty-five-question checklist at the end of [80-anti-patterns.md](80-anti-patterns.md) against the screen before you call it done.
5. Where the system lacks a value, use the nearest one and say so. Do not invent one.

That is the difference between extending this system and forking it.
