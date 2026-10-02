---
name: halderworks-design
description: >-
  The house design system for Halderworks products. Load it BEFORE writing or restyling any user
  interface - a screen, a route, a component, a form, a table, a landing page, an email sign-in,
  a first-run setup screen, a settings page, a chart, an icon row, a piece of UI copy - and before
  proposing a colour, a size, a radius, a duration, a breakpoint or a z-index. It carries colour
  ramps with contrast floors, named roles, two themes, a five-step text size, two densities, a
  plain-CSS component layer with a generated sheet per component, and a rule that no value is
  invented: a value the system lacks is a gap to report, not a number to guess. Also load it when
  asked whether this system covers a surface at all, when a contrast ratio or an accessibility
  keyboard behaviour is in question, or when extending the system.
---

# Halderworks Instrument

You are about to build or change a user interface for a Halderworks product.
This system is what you build it from.

**It is plain files and plain Markdown by design.**
There is nothing to install and nothing to build, and no dependency on which model or tool is reading it.
Read the files.
The component layer is plain CSS, `components/components.css`, loaded after the variables.

## The four rules, which do not have exceptions

1. **Never write a literal colour, size, radius, duration, breakpoint or z-index.**
   Every one is a `var(--hw-*)` token.
   A value the system lacks is a gap to **report**, not a number to invent.
   `design/00-brand-book.md#the-rule-that-matters-most` shows the sentence to write.
2. **Never decide a contrast ratio by eye.**
   Every ink-on-ground pair this system permits is in the table in `design/10-color.md#which-ink-may-sit-on-which-ground`, which is exactly what `tools/contrast.py` certifies.
   A pairing not in that table is not a pairing you may reach for.
3. **Start from the component's sheet, not from a screenshot.**
   A button with the right colours and the wrong padding is still off-system.
4. **Answer the questions under "Before a screen ships" in `design/00-brand-book.md`** before you call the screen done.
   It is the last gate.

## Step 0, and skipping it is the most expensive mistake available

**Before you build a surface, check whether this system already answers it.**

`design/64-component-sheets.md` is the inventory: every component the house has, each with its purpose, anatomy, states, keys and tokens, generated from the same catalogue entry that draws it.
Searching it, and the table under "What the house has, and what it does not" in `design/00-brand-book.md`, returns one of four answers:

| what you find | what it means |
|---|---|
| a sheet | the house's component. Build from it |
| admitted, no sheet yet, or partial | the brand book names what exists and what is missing. Build the missing half from house components and report it |
| declined | this system decided not to have it, with the reason. Do not build it; say the decline exists |
| nothing at all | a genuine gap. Say so, build the nearest thing from house components, and report it |

## Which file answers your question

| you are about to | read |
|---|---|
| understand what these products are, the quiet page and the loud stage, and the marks | `design/00-brand-book.md` |
| build any component, or find out whether the house has one | `design/64-component-sheets.md`, and `components/components.css` for the CSS |
| pick a colour, or put an ink on a ground | `design/10-color.md`. **The pairing table is permission, not documentation** |
| build a screen for quoth, papertrace or pointback, or give a product its own identity | `design/12-brand.md`, then load `examples/<product>/exports/variables.css` in place of `exports/variables.css`. A brand changes values, never token names |
| set type, or support the reader's text size | `design/20-type.md`. The tabular-figures rule is the one most often missed |
| write the words in it | the Words section of `design/00-brand-book.md` |
| space, size, round, elevate or lay out anything, or add a compact mode | `design/30-space.md` |
| draw or choose an icon | the Icons sections of `design/00-brand-book.md` and `design/30-space.md` |
| animate anything | `design/40-motion.md` |
| give a control its focus, disabled, busy or selected behaviour, or its keys | the component's sheet, then `design/60-accessibility.md` |
| ship | the questions under "Before a screen ships" in `design/00-brand-book.md` |
| add something the system does not have | `design/00-brand-book.md#loading-it-in-a-product` for a product's own namespace, `design/12-brand.md#a-colour-of-the-products-own` for a colour, and `AGENTS.md` for a change to the house itself |

## If your context is tight, read this instead

**`exports/DESIGN.compact.md`** is every role and scale with its value and job in one file, generated from the same source as everything else.

**When the compact brief is enough:**

- You are styling something the system already specifies and you only need its values.
- You are converting an existing screen to house tokens.
- You are answering a question about what a token is or what it is for.

**When it is not enough, and reading it alone will produce off-system work:**

- **You are building a component or a surface for the first time.**
  The compact brief carries values, not anatomy.
  `design/64-component-sheets.md` is the anatomy, and a button with correct colours and wrong padding is the exact failure.
- **You are pairing an ink with a ground.**
  Permission lives in `design/10-color.md`.
  Two tokens both existing does not make them a pair.
- **You are making anything interactive.**
  Each sheet carries its states and keys, and `design/60-accessibility.md` what they share; neither is in the values.
- **You are asked whether the system covers something.**
  Only the sheets and the brand book's table can answer that, and a compact read that finds nothing will report a gap that is actually a decline.

Read `exports/DESIGN.compact.md` first and the specific file second.
Do not read the compact brief *instead of* the file that owns the thing you are building.

## Loading the tokens into a product

```css
@import "fonts/fonts.css";            /* the house faces, self-hosted from this repository's fonts/ */
@import "variables.css";              /* exports/variables.css, or examples/<brand>/exports/variables.css */
@import "components/components.css";  /* the component layer, after the variables */
@import "product.css";                /* the product's own namespace, loaded AFTER, never instead */
```

Fonts are self-hosted, never loaded from a font service: `fonts/` holds Archivo, Literata and IBM Plex Mono as WOFF2 with their OFL texts, and `design/00-brand-book.md#loading-it-in-a-product` says what a brand with system faces loads instead.

Every token is prefixed `hw-`, so it cannot collide with a framework's variables.
Dark theme is `[data-theme="dark"]`, and the system follows `prefers-color-scheme` when the page has made no explicit choice.
Compact density is `data-density="compact"` on any ancestor.

The exports are generated from `ramps/`: `exports/variables.css` is plain custom properties with every theme and media block, `exports/theme.css` is the same plus a Tailwind v4 `@theme inline` map, `exports/design-tokens.json` is W3C DTCG.
Type, space and control sizes are rem, and `data-text-size="s|m|l|xl|xxl"` on `html` sets the root to 13, 15, 17, 19 or 22px.

## What you may and may not change

**A product's identity is its brand file, and nothing else.**
`ramps/brands/<product>.json` names a neutral, five to eight hues by name - the accent, the mark, the three states and up to three of its own - and may name a shape register, an icon stroke and a face per family from `ramps/roster.json`, built into the house's own token names ([design/12-brand.md](design/12-brand.md#the-inputs)).
Take it by regenerating, never by hand-picking a colour:

```bash
python3 tools/ramps.py
python3 tools/contrast.py ramps/tokens/papertrace.tokens.css
python3 tools/export.py examples/papertrace
```

The build solves every text and boundary step against its contrast floor and **refuses to write** if one does not hold.
`contrast.py` then refuses an accent whose selected-row fill or focus ring sits too close to a state colour in CIEDE2000, so a product cannot take a green that competes with "passed".
The second line is not a formality and it is not a second opinion from the same head: `contrast.py` shares no arithmetic with the build and carries its own list of what must hold.
At every fifth accent hue, 45 of 72 clear it, and the 27 it refuses are 0 to 85 and 130 to 170 ([design/12-brand.md](design/12-brand.md#the-bars-every-brand-is-held-to)).

**Everything else goes in the product's own namespace**, `--quoth-`, `--gates-`, never by redefining an `hw-` token.
A colour the house has no token for is a named hue in the product's brand file, built into a ramp like every other and certified by `tools/contrast.py`, never hand-picked.

## Two things this system does that most do not, and why they matter to you

- **Every rule names the file that enforces it.**
  If you disagree with a value, read the tool that holds it and the source the book names beside it, and argue with the measurement rather than with a preference.
- **It says what it does not have.**
  The brand book lists what the house declines, with the reason, and what it admits but has not drawn yet.
  A question answered there does not need asking again.

Solve to the requirement.
Checking afterwards only tells you what you already shipped.
