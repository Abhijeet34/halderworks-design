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
4. **Its row in the verification.** A colour token joins `tokens/tokens.seed.json` with its `floors` - the bar it must clear and the grounds it may sit on - and the build must still pass. A layout or density token joins its family in the seed. Nothing joins `tokens/tokens.json` directly, because that file is generated.

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
