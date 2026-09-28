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

## A brand seed, and nothing else

A product's identity is a **brand seed**: twenty-two bounded inputs the build solves into a full token set with the house's names, never a stylesheet of overrides.
[12-brand.md](12-brand.md) owns the inputs, their bounds and the three product brands.
papertrace is the worked example here, because it is the warm one:

```json
{
  "name": "papertrace",
  "accentHue": 250, "accentChroma": 1.27, "accentLightness": {"light": 0.42, "dark": 0.78},
  "quietChroma": 0.6, "neutralHue": 85, "neutralChroma": 3.0,
  "shape": "crisp", "iconStroke": "1.5px", "display": "system serif", "text": "system serif"
}
```

```bash
python3 tools/build.py --brand examples/papertrace/brand.seed.json   # writes examples/papertrace/tokens/
python3 tools/contrast.py examples/papertrace/tokens/tokens.css        # verify it independently
```

**The build refuses to emit if the matrix does not hold.**
That refusal is the feature: it caught three defects in this system's own first pass, including a
dark focus ring at 2.56:1 on `--hw-surface-raised`.

What it does with a brand seed, in order: every input is checked against its bound, and a key that is not an input, an `hw-` token included, is refused.
The inputs are applied to a copy of the house seed: the sixteen neutrals follow the neutral hue and chroma together, the accent family follows the accent hue, chroma and lightness, and the chart ramp rotates with the accent, while the three semantics do not move, because a green that means "passed" cannot follow a brand decision.
Then the copy is solved exactly as the house is: chroma clamped to the in-gamut maximum, and any token whose contrast floor no longer holds re-solved by binary search, as close to its anchor as the floor permits - which is not a formality, because rotating a hue at fixed lightness moves WCAG luminance.
Built from papertrace's seed, three tokens re-solve and all 198 certified pairs clear their bar, on the float value and at 8-bit: worst 3.031:1 non-text and 4.594:1 text.

**What a brand paints must stand apart from the state drawn in the same form**: the primary fill from `hw-danger`, the selected-row fill from each state's quiet fill, and the focus ring from `hw-danger`, each in CIEDE2000 on the 8-bit value, which [10-color.md](10-color.md#the-three-bars-the-accent-is-held-to) owns.
A product cannot take hue 150 with an accent selection, because its selected row is a passed row, and the build says so with the number rather than refusing on principle:

```text
FAIL  the fill, hw-accent-quiet at hue 150, sits 0.3 from hw-success-quiet in light, below the 5
      CIEDE2000 this system requires (10-color.md#the-three-bars-the-accent-is-held-to)
```

Its ink, 6.1 from `hw-success`, is reported rather than refused since the vivid tier: every state carries a glyph and a word.
With `selection: neutral`, in a brand that opens the vivid tier, the same hue builds and certifies, because a neutral row is not a hue.

That is a measurement rather than a veto, and it is executable rather than merely written down.

`--accent-hue` stays as the one-input form: `python3 tools/build.py --accent-hue 318 --out ./my-tokens` is a brand whose only input is its hue, and at 318 five tokens re-solve and all 198 certified pairs still clear their bar.

**Do not hand-edit a `tokens.css` or a `tokens.json`,** the house's or a brand's. Both are the build's output.
`tokens/tokens.seed.json` is the source, and it carries, per colour token, a lightness and chroma
anchor and the contrast floor that token must hold; a brand's `brand.seed.json` carries only its inputs.

## A colour of the product's own

A product sometimes needs a colour for a concept the house has no opinion about, and quoth's open microphone is the case that exists.
A composition of `hw-` tokens is still the first answer.
When no house colour means the thing, the product declares its own colour and the house tools solve it, for the same reason the accent is regenerated rather than hand-picked.

The product owns a seed in its own namespace, with the per-token shape of `tokens/tokens.seed.json`: a hue, a lightness and chroma anchor per theme, the `floors` it must hold, and `apart`, the house colours it must never be mistaken for.
[examples/quoth/quoth.seed.json](../examples/quoth/quoth.seed.json) is the worked example, and the one CI builds on every change, so a house change that breaks a product colour fails here first.

A product colour is solved against its own brand's set, because the surfaces it lands on and the accent it must stay clear of are its brand's, not the house's:

```bash
python3 tools/build.py --brand quoth/brand.seed.json --extend quoth/quoth.seed.json   # writes quoth.tokens.css beside the seed
python3 tools/contrast.py quoth/tokens/tokens.css --extend quoth/quoth.seed.json     # verify it with the second instrument
```

The build solves each token in all four blocks, light, dark and both `prefers-contrast: more` tiers, exactly as it solves a house token: chroma clamped into sRGB, lightness re-solved from the anchor when a floor fails, and every value re-measured on the string it writes, on the float value and at 8-bit.
It writes the product's file and nothing else, because the brand's `tokens.css` is loaded first and does not change.
A product with no brand seed solves against the house set by leaving `--brand` out and verifying against `tokens/tokens.css`.

What both tools refuse, whatever the product's seed says:

- **A name that is an `hw-` token, or outside the seed's namespace.** This path cannot redefine an `hw-` token, and `tools/contrast.py` refuses an `hw-` declaration in a product file on its own.
- **A token without a floor on each of the six surfaces**, or a floor at a bar that is neither 3:1 nor at least 4.5:1.
  A product colour is a mark drawn on a house surface, and nothing stops a component putting it on any of them.
- **An `apart` list without `hw-success`, `hw-warning`, `hw-danger` and `hw-accent`.**
  A seed can name more colours to stay clear of, never fewer.
- **A solved value under either product bar**, in any of the four blocks, with the number: under 14 CIEDE2000 at 8-bit from `hw-success`, `hw-warning` or `hw-danger`, or under 5.0 in hue and chroma from anything in `apart`. [The next section](#how-a-product-colour-is-held-apart) says why there are two.

```text
FAIL  quoth-live at hue 150 sits 2.9 from hw-success in hue and chroma in light, below the 5.0
      this system requires (95-extending.md#a-colour-of-the-products-own)
FAIL  quoth-live at hue 150 sits 5.4 CIEDE2000 from hw-success at 8-bit in light, below the 14
      this system requires (95-extending.md#a-colour-of-the-products-own)
```

`tools/contrast.py --extend` holds every product colour to 3:1 on the six surfaces, 14 CIEDE2000 from the three states and 5.0 in hue and chroma from the states and the accent from its own declarations, and reads the seed only for what it adds, such as a text bar.
Weakening the seed and moving the value in one edit still fails.

Both tools also validate the seed's raw JSON before any of the above runs: a non-object top level, a namespace or token name that is not a string, an anchor `L` or `C` that is not a finite number, a hue that is neither a whole number of degrees nor `accent+N`, or a floor `bar` or `apart`/`on` entry of the wrong type or shape.
Every leaf a solver later reads is checked once at that boundary, so a bad leaf is one `FAIL` line and exit 1, never a traceback.
`tools/contrast.py --extend` also refuses to run against a seed whose built CSS is missing, naming the `tools/build.py --extend` command to run first, rather than measuring a file that is not there.

### How a product colour is held apart

Decided by the system's owner on 2026-09-28, on the house-live-orange audit of that day.
It replaces 8.0 in hue and chroma, which was the accent's retired 8.0 carried into the product rule without calibration, and which refused five of the six inks the constraint audit's renders judged to be colours of their own: 186, 116, 350, the umber and the moss sit 5.4 to 6.7.

Against `hw-success`, `hw-warning` and `hw-danger`, in all four blocks, a product colour clears two bars:

| bar | measured | calibrated on |
|---|---|---|
| 14 | CIEDE2000 on the 8-bit value a display receives | the accent's ink bar: teal 172 at 10.5 read as a state and 186 at 14.3 as its own colour ([10-color.md](10-color.md#the-three-bars-the-accent-is-held-to)) |
| 5.0 | oklab distance times 100 with lightness left out, "in hue and chroma" | the same judged inks: hue 52 at 4.58 sat with Failed and Retried, the umber at 5.36 read as dark brown |

Each bar refuses a colour the other passes, and the mutation suite watches both fail:

- **The guard catches a state moved in lightness.** Recording red kept at hue 27 and anchored at L 0.30 and 0.85 solves to a maroon, `#5C0105`, 21.6 CIEDE2000 from `hw-danger`, past the 14, and 0.9 from it in hue and chroma, which is what a reader sees: a red. An oxblood at hue 36, `#812101`, clears 14 in light at 15.7 and sits 2.2 in hue and chroma.
- **CIEDE2000 catches a state moved in chroma.** Recording red at hue 30 at a 3:1 floor, `#D41101` and `#FE6653`, clears the guard at 7.9 because its chroma is higher than `hw-danger`'s, and sits 10.4 CIEDE2000 from it in dark.
  That keeps quoth's recording red excluded mechanically.

Against `hw-accent`, and any further colour a seed names, the guard alone.
The ink bar was calibrated on chromatic inks against the states, and quoth's violet of 2026-09-21, approved on render, sits 12.0 CIEDE2000 from quoth's near-neutral slate accent and 8.8 clear of it in hue and chroma.

Colour-vision separation is reported and never refused on, as for the accent.
Both tools print, in each block, the closest a product colour comes to a state under protanopia, deuteranopia and tritanopia, simulated with Machado, Oliveira and Fernandes 2009 at full severity ([90-evidence.md](90-evidence.md#the-painted-separation-bars)).
The house's own states already collapse under deuteranopia and are told apart by their words ([10-color.md](10-color.md#the-three-bars-the-accent-is-held-to)), so refusing a product colour on it would hold the product to a bar the house fails; the product's word or shape carries the state instead.

The floor is set by use: 3:1 on the six surfaces for a mark, per WCAG 2.2 SC 1.4.11, and 4.5:1 only when text is set in the colour.
The seed's `floors` declare which, and `tools/contrast.py` never certifies less than 3:1 whatever they say.

A third reading was measured and declined: CIEDE2000 with its lightness term dropped.
No bar in it reproduces the judged inks, because it puts the umber, judged distinct, at 10.6 and hue 52, judged a state, at 12.0, and at 8.0 it admits teal 172 and hue 52 as product colours, both rejected on render.

### The worked example, quoth's live colour

The microphone-open state takes its own colour, decided by the system's owner on 2026-09-21.
The accent already marks selection, focus and the active tab, so a shared accent makes "the microphone is open" read as "this row is selected", and recording red sits on `hw-danger`.
quoth's decision D-062 moved it from a violet to the orange of the open microphone, and D-059 took the word out of it, so it is a mark.

Solved against quoth's brand set, [examples/quoth/quoth.tokens.css](../examples/quoth/quoth.tokens.css), as `tools/contrast.py` measures it:

| block | value | hex | worst contrast, six surfaces | closest CIEDE2000 to a state | closest in hue and chroma | a dichromat, reported |
|---|---|---|---:|---|---|---|
| light | `oklch(0.55 0.1492 48)` | `#B45001` | 4.54:1 | 15.6 from `hw-warning` | 5.43 from `hw-danger` | protan 1.8 from `hw-warning` |
| dark | `oklch(0.74 0.1687 48)` | `#FE853E` | 6.88:1 | 18.7 from `hw-danger` | 7.69 from `hw-danger` | protan 6.7 from `hw-warning` |
| light, more contrast | `oklch(0.55 0.1492 48)` | `#B45001` | 4.54:1 | 19.4 from `hw-danger` | 5.43 from `hw-danger` | protan 8.2 from `hw-warning` |
| dark, more contrast | `oklch(0.74 0.1687 48)` | `#FE853E` | 6.88:1 | 16.4 from `hw-danger` | 7.69 from `hw-danger` | deutan 3.9 from `hw-warning` |

The contrast figures are the 8-bit ones.
Neither anchor re-solves: the floor rises to 4.5:1 under more contrast, and the light value already holds 4.54:1.
`tools/build.py` reads the light block's CIEDE2000 as 15.2, because it also measures the rounding a display may take the other way on a channel near a boundary.

The derivation, one input at a time:

- **Hue 48 at L 0.55 and 0.74** is quoth's D-062. It passes by 0.43 in hue and chroma, and the choice among the oranges that pass was a render judgement, not a number.
- **The chroma** is asked at 0.30 and clamped by the build to the sRGB edge, 0.1492 and 0.1687, so the orange is as vivid as a display paints it at that lightness.
- **The floor is 3:1 on all six surfaces**, because it is a mark: the lit segments of the level meter.
  It carries no pair on a quiet fill, because quoth has no live fill.

Colour is never the only carrier of the state: [15-color-combinations.md](15-color-combinations.md) puts a word beside every semantic colour and [55-iconography.md](55-iconography.md#colour) puts one beside every icon.
So the live state is always the word `Recording`, in a house text colour, beside the mark in `--quoth-live`.
Under protanopia the light value comes within 1.8 of `hw-warning`, which is that word's job, not the colour's.
It does not pulse, because [40-motion.md](40-motion.md) lets only a determinate progress indicator loop, and the change is announced in a `role="status"` region, which quoth provides.
It is not certified on the menu-bar item, which sits on a ground the house does not own.

It sits 6.2 in hue and chroma and 17.5 CIEDE2000 from quoth's `hw-chart-3` at its closest.
The chart ramp is not in its `apart` list, so a quoth screen that colours speakers from the chart ramp keeps the live state out of the chart, and relies on the word beside it.

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

```css
@import "hw/tokens.css";      /* the house set, or a brand's own tokens/tokens.css */
@import "quoth/tokens.css";   /* the product's own namespace, after */

/* The faces, self-hosted: each file is the upstream one 20-type.md cites. A brand whose faces are
   system stacks loads none of these; a self-hosted brand face is added the same way. */
@font-face { font-family: "Public Sans"; src: url("fonts/PublicSans[wght].ttf") format("truetype");
             font-weight: 100 900; font-display: swap; }
@font-face { font-family: "Public Sans"; src: url("fonts/PublicSans-Italic[wght].ttf") format("truetype");
             font-weight: 100 900; font-style: italic; font-display: swap; }
@font-face { font-family: "Newsreader"; src: url("fonts/Newsreader[opsz,wght].ttf") format("truetype");
             font-weight: 200 800; font-display: swap; }
@font-face { font-family: "IBM Plex Mono"; src: url("fonts/IBMPlexMono-Regular.ttf") format("truetype");
             font-weight: 400; font-display: swap; }
```

No font is loaded from a font service: three of the products this system serves make no network request or refuse one by policy, and a system that told them to load a stylesheet from a CDN was a system they could not follow.

Nothing else is required.
There is no component library to install, no build step, and no runtime: the system is a token file, a set of rules, and the discipline to report a gap rather than invent a value. <!-- covered-by: A shipped component library -->

## For an agent building against this system

If you are a model that has never seen the conversation this system came out of, this is the whole contract:

1. Read [SKILL.md](../SKILL.md). Its table says which file answers the task in front of you.
2. Load `tokens/tokens.css` and use `var(--hw-*)` for every colour, size, radius, duration, breakpoint and z-index.
3. Check every ink-on-ground pair against [15-color-combinations.md](15-color-combinations.md) before you write it, and every control boundary against the 3:1 table in the same file.
4. Run the thirty-five-question checklist at the end of [80-anti-patterns.md](80-anti-patterns.md) against the screen before you call it done.
5. Where the system lacks a value, use the nearest one and say so. Do not invent one.

That is the difference between extending this system and forking it.
