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
/* quoth/tokens.css - loaded after the house tokens.css, never instead of it */
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

## The one thing a product may change

**The accent hue, and nothing else.**

The whole accent family is generated from one hue by the solver, so a product takes a different accent by regenerating, not by hand-picking:

```bash
python3 tools/build.py --accent-hue 318 --out ./my-tokens   # solve a full set at a new hue
python3 tools/contrast.py ./my-tokens/tokens.css            # verify it independently
```

**The build refuses to emit if the matrix does not hold.**
That refusal is the feature: it caught three defects in this system's own first pass, including a
dark focus ring at 2.56:1 on `--hw-surface-raised`.

What it does with a new hue, in order: every neutral, accent and chart hue follows the seed, while
the three semantics do not, because a green that means "passed" cannot follow a brand decision.
Chroma is clamped to the in-gamut maximum at each token's lightness and hue. Then any token whose
contrast floor no longer holds has its lightness re-solved by binary search, as close to its anchor
as the floor permits - which is not a formality, because rotating a hue at fixed lightness moves
WCAG luminance. Rebuilt at hue 318, five tokens re-solve and all 198 certified pairs still clear
their bar, on the float value and at 8-bit: worst 3.030:1 non-text and 4.532:1 text.

**A new hue must clear an oklab separation above 8 from every semantic**, which is the test recorded
in [10-color.md](10-color.md). A product cannot take hue 150 because it is close to `hw-success`,
and the build says so with the number rather than refusing on principle:

```text
FAIL  accent hue 150 sits 4.4 from hw-success in light theme, below the 8.0 this system
      requires (10-color.md#why-hue-198)
```

That is a measurement rather than a veto, and it is executable rather than merely written down.

**Do not hand-edit `tokens/tokens.css` or `tokens/tokens.json`.** Both are the build's output.
`tokens/tokens.seed.json` is the source, and it carries, per colour token, a lightness and chroma
anchor and the contrast floor that token must hold.

## A colour of the product's own

A product sometimes needs a colour for a concept the house has no opinion about, and quoth's open microphone is the case that exists.
A composition of `hw-` tokens is still the first answer.
When no house colour means the thing, the product declares its own colour and the house tools solve it, for the same reason the accent is regenerated rather than hand-picked.

The product owns a seed in its own namespace, with the per-token shape of `tokens/tokens.seed.json`: a hue, a lightness and chroma anchor per theme, the `floors` it must hold, and `apart`, the house colours it must never be mistaken for.
[examples/quoth.seed.json](../examples/quoth.seed.json) is the worked example, and the one CI builds on every change, so a house change that breaks a product colour fails here first.

```bash
python3 tools/build.py --extend ../quoth/quoth.seed.json      # solve it; writes quoth.tokens.css beside the seed
python3 tools/contrast.py --extend ../quoth/quoth.seed.json   # verify it with the second instrument
```

The build solves each token in all four blocks, light, dark and both `prefers-contrast: more` tiers, exactly as it solves a house token: chroma clamped into sRGB, lightness re-solved from the anchor when a floor fails, and every value re-measured on the string it writes, on the float value and at 8-bit.
It writes the product's file and nothing else, because the house `tokens.css` is loaded first and does not change.
A product that also regenerates the accent passes the same `--accent-hue` to both commands and verifies against that `tokens.css`.

What both tools refuse, whatever the product's seed says:

- **A name that is an `hw-` token, or outside the seed's namespace.** This path cannot redefine an `hw-` token, and `tools/contrast.py` refuses an `hw-` declaration in a product file on its own.
- **A token without a floor on each of the six surfaces**, or a floor at a bar that is neither 3:1 nor at least 4.5:1.
  A product colour is a mark drawn on a house surface, and nothing stops a component putting it on any of them.
- **An `apart` list without `hw-success`, `hw-warning`, `hw-danger` and `hw-accent`.**
  A seed can name more colours to stay clear of, never fewer.
- **A solved value closer than 8.0 in hue and chroma to anything in `apart`**, in any of the four blocks, with the number:

```text
FAIL  quoth-live at hue 150 sits 0.8 from hw-success in hue and chroma in light, below the 8.0
      this system requires (95-extending.md#a-colour-of-the-products-own)
```

`tools/contrast.py --extend` holds every product colour to 3:1 on the six surfaces and to 8.0 from the four state colours from its own declarations, and reads the seed only for what it adds, such as a text bar.
Weakening the seed and moving the value in one edit still fails.

Both tools also validate the seed's raw JSON before any of the above runs: a non-object top level, a namespace or token name that is not a string, an anchor `L` or `C` that is not a finite number, a hue that is neither a number nor `accent+N`, or a floor `bar` or `apart`/`on` entry of the wrong type or shape.
Every leaf a solver later reads is checked once at that boundary, so a bad leaf is one `FAIL` line and exit 1, never a traceback.
`tools/contrast.py --extend` also refuses to run against a seed whose built CSS is missing, naming the `tools/build.py --extend` command to run first, rather than measuring a file that is not there.

### Why the separation leaves lightness out

The accent's 8.0 is oklab distance with lightness in, measured at the semantics' own lightness, where the two readings agree: 8.9 and 8.2 from `hw-success` either way.
A product colour's anchors are its own, so a rule that counts lightness can be cleared by lightness alone.
Recording red is the case.
Hue 27 anchored at L 0.30 in light and 0.85 in dark solves to a maroon, `#5C0105`, and a salmon, `#FEBAB2`, which sit 23.9 and 20.9 from `hw-danger` counting lightness, and 14.0 and 9.8 under more contrast.
In hue and chroma they sit 0.9 and 3.1, which is what a reader sees: a red.
So a product colour is held to 8.0 in hue and chroma, which is never looser than the reading with lightness in.

### The worked example, quoth's live colour

The microphone-open state takes its own colour, decided by the system's owner on 2026-09-21.
The accent already marks selection, focus and the active tab, so a shared accent makes "the microphone is open" read as "this row is selected", and recording red sits on `hw-danger`.

| block | value | hex | worst contrast, six surfaces | closest in hue and chroma |
|---|---|---|---:|---|
| light | `oklch(0.515 0.13 297)` | `#7054A8` | 5.26:1 | 16.2 from `hw-accent` |
| dark | `oklch(0.6255 0.11 297)` | `#8F79C2` | 4.53:1 | 15.6 from `hw-danger` |
| light, more contrast | `oklch(0.4467 0.13 297)` | `#5D4192` | 7.07:1 | 15.5 from `hw-accent` |
| dark, more contrast | `oklch(0.7424 0.11 297)` | `#B39DE9` | 7.09:1 | 15.6 from `hw-danger` |

The derivation, one input at a time:

- **Hue 297** is the hue whose worst separation from the four state colours is largest, 15.5, in a one-degree sweep of the wheel. The 99 hues from 246 to 344 clear 8.0 with every floor held; no other hue does.
- **The anchors** are the accent's lightness, 0.515 and 0.619, and `hw-danger`'s chroma, 0.13 and 0.11, so recording is exactly as loud as an error and no louder.
- **The floor is the text bar, 4.5:1 on all six surfaces**, because the word is set in this colour; that subsumes the 3:1 a mark needs.
  It carries no pair on a quiet fill, because quoth has no live fill, so a live badge is the fill-less form [15-color-combinations.md](15-color-combinations.md) already gives a badge on a tinted row.

Colour is never the only carrier of the state: [15-color-combinations.md](15-color-combinations.md) puts a word beside every semantic colour and [55-iconography.md](55-iconography.md#colour) puts one beside every icon.
So the live state is always the word `Recording` and Lucide's `mic` icon at `--hw-icon-sm`, both in `--quoth-live`.
It does not pulse, because [40-motion.md](40-motion.md) lets only a determinate progress indicator loop, and the change is announced in a `role="status"` region, which quoth provides.
It is not certified on the menu-bar item, which sits on a ground the house does not own.

It sits 6.3 from `hw-chart-2` and 5.7 from `hw-chart-3` at its closest, and no hue clears 8.0 from all six chart colours and the four state colours at once: the best, hue 295, reaches 5.9.
A quoth screen that colours speakers from the chart ramp therefore keeps the live state out of the chart, and relies on the word and the icon beside it.

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
4. **Its row in the verification.** A colour token joins `tokens/tokens.seed.json` with its `floors` - the bar it must clear and the grounds it may sit on - and the build must still pass. A layout or density token joins its family in the seed. Nothing joins `tokens/tokens.json` directly, because that file is generated. A product's own colour takes the same four things in the product's seed, [above](#a-colour-of-the-products-own).

## Reporting a gap

A gap is a finding, not a blocker.
Ship the screen with the nearest house value, and say in the same breath what you needed:

> Used `--hw-space-24` for the pane divider; the pane wants about 28px and the scale has no step there.

That sentence is worth more than a correct-looking screen with `28px` written into it, because the next person hits the same gap and either finds the report or invents a second number.

## Loading the system in a product

```html
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Public+Sans:ital,wght@0,100..900;1,100..900&family=Newsreader:ital,opsz,wght@0,6..72,200..800;1,6..72,200..800&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&display=swap">
```

```css
@import "hw/tokens.css";      /* the house system */
@import "quoth/tokens.css";   /* the product's own namespace, after */
```

Nothing else is required.
There is no component library to install, no build step, and no runtime: the system is a token file, a set of rules, and the discipline to report a gap rather than invent a value. <!-- covered-by: A shipped component library -->

## For an agent building against this system

If you are a model that has never seen the conversation this system came out of, this is the whole contract:

1. Read [SKILL.md](../SKILL.md). Its table says which file answers the task in front of you.
2. Load `tokens/tokens.css` and use `var(--hw-*)` for every colour, size, radius, duration, breakpoint and z-index.
3. Check every ink-on-ground pair against [15-color-combinations.md](15-color-combinations.md) before you write it, and every control boundary against the 3:1 table in the same file.
4. Run the thirty-question checklist at the end of [80-anti-patterns.md](80-anti-patterns.md) against the screen before you call it done.
5. Where the system lacks a value, use the nearest one and say so. Do not invent one.

That is the difference between extending this system and forking it.
