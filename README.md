# Halderworks Instrument

A design system for instruments of record: software whose job is to be trusted about a number, a state or a record rather than to be admired.

Twelve-step colour ramps with a contrast floor on every step, named roles that point at steps, two themes and a high-contrast set, a rem type ramp under a five-step text-size setting, two densities, and a plain-CSS component layer.
Every value traces to a measurement, and the repository carries the tools that prove it.

[SKILL.md](SKILL.md) is the entry point for a model, and [Building a screen with it](#building-a-screen-with-it) below is the one for a developer.
[design/00-brand-book.md](design/00-brand-book.md) opens the book: the foundations, written once, and the component sheets, generated.
[AGENTS.md](AGENTS.md) is for changing the system itself.

## What it is for

**A reader should be able to tell, from a screen built with this, that somebody decided.**

That is the whole outcome, and it is the reason for the discipline rather than a slogan on top of it.
A screen assembled from defaults is legible as such: nothing on it was chosen, so nothing on it carries conviction, and a reader feels that before they can name it.
Every rule in this book exists because a default existed and was refused - a near-neutral ground against a tinted one, the primary action in ink rather than a hue, colour spent only where a state is reported, a headline set tight because it is read once.

The corollary is the working rule, and it cuts both ways: **a rule with no reason attached is itself a default**, and adding rules does not add conviction.
So the book states each foundation once and names the file that enforces it, and documents each component once, in a sheet generated from the catalogue that draws it.

## What makes it different from a palette with opinions

- **Nothing was chosen and then checked.**
  `tools/ramps.py` solves each ramp's text and boundary steps against every ramp they may sit on, measures the CSS it is about to write, and exits non-zero rather than writing a file whose numbers are not true.
- **Two instruments, not one.**
  `tools/contrast.py` certifies every step and every role again with arithmetic it shares with nothing, and carries its own list of what must hold, so a floor cannot be weakened in the same edit as the value it guards.
  `tools/painted.py` then measures the same pairs on the pixels a browser paints.
- **Permission is a table, not a convention.**
  Two roles both existing does not make them a pair: [design/10-color.md](design/10-color.md#which-ink-may-sit-on-which-ground) lists the pairs `tools/contrast.py` certifies, and `tests/components.py` refuses a component that paints any other pair without measuring it itself.
- **The text size is the reader's.**
  Type, space and controls are rem, five settings move the root from 13 to 22px, and `tests/exports.py` holds every export to its floors at each of them.
- **Rhythm is a checked property, not a claim.**
  `tests/exports.py` refuses an off-unit space or size value that is not declared with a reason - in both directions, so the exception list cannot rot.
  [design/30-space.md](design/30-space.md#the-unit) names the unit and the exceptions.

## Building a screen with it

For a developer on a Halderworks product with a screen to build.
Every step names the one file that owns it.

1. **Load the tokens and the components.**
   Copy [exports/variables.css](exports/variables.css), the `fonts/` directory with its [fonts.css](fonts/fonts.css), and [components/components.css](components/components.css) into the product and import them before the product's own stylesheet, as [design/00-brand-book.md](design/00-brand-book.md#loading-it-in-a-product) shows.
   A Tailwind v4 project takes [exports/theme.css](exports/theme.css) instead of the variables, and a product with its own brand takes the same files from `examples/<product>/exports/`.
   Dark theme is `data-theme="dark"` on the root, compact density is `data-density="compact"` on any ancestor, and with neither set the page follows `prefers-color-scheme`.
2. **Find the component's sheet** in [design/64-component-sheets.md](design/64-component-sheets.md), and build from it rather than from a screenshot.
   A surface with no sheet is either declined or admitted-but-undrawn in [the brand book's table](design/00-brand-book.md#what-the-house-has-and-what-it-does-not), or a gap to report.
3. **Pair an ink with a ground only from the table** in [design/10-color.md](design/10-color.md#which-ink-may-sit-on-which-ground).
   Every colour, size, radius, duration, breakpoint and z-index is a `var(--hw-*)`; a literal is off-system.
4. **Give every control its states and keys** from its sheet and from [design/60-accessibility.md](design/60-accessibility.md).
5. **Answer the questions** under [Before a screen ships](design/00-brand-book.md#before-a-screen-ships) against the finished screen.
6. **Where a value is missing, use the nearest house value and say so** in the pull request, in the form [the brand book](design/00-brand-book.md#the-rule-that-matters-most) shows.
   Product-specific tokens go in the product's own namespace, `--quoth-`, never by redefining an `hw-` token.

A product takes its identity from a brand file, `ramps/brands/<product>.json`: a neutral, five to eight named hues, and a shape register, an icon stroke and faces from the house roster ([design/12-brand.md](design/12-brand.md)).
`python3 tools/ramps.py` builds it in the house's own token names, and `tools/contrast.py` refuses it if one role fails.
At accent hue 150 it refuses, because the selected-row fill sits 0.4 CIEDE2000 from `--hw-success-fill` against the 5 [design/12-brand.md](design/12-brand.md#the-bars-every-brand-is-held-to) requires.

## How a model loads it

There is nothing to install and nothing to build.
The whole system is files, and the one script, `components/radiogroup.js`, gives a segmented control its arrow keys.

1. Clone or vendor this repository where the model can read it.
2. Point the model at [SKILL.md](SKILL.md).
   It fires on "about to write or restyle any UI" and routes to the file that answers the question in hand.
3. If context is tight, [exports/DESIGN.compact.md](exports/DESIGN.compact.md) is the whole value set in one file.
   `SKILL.md` says exactly when that is enough and when reading it alone will produce off-system work.

For a harness with a skills directory, `SKILL.md` and this tree drop in unchanged.
For anything else, the file is ordinary Markdown with a YAML header and reads correctly without any harness at all - that is deliberate, because a design system that only one vendor's model can load is a design system with a vendor lock in it.

Other forms of the same values, for a tool that wants one:

| file | what it is |
|---|---|
| [exports/variables.css](exports/variables.css) | the custom properties a browser loads, from `ramps/`: the brand's faces and shape, both themes, `prefers-contrast: more`, compact density, the 44px touch floor, reduced motion and `html[data-text-size]`. Copy-pasteable into any product |
| [exports/theme.css](exports/theme.css) | the same variables plus a Tailwind v4 `@theme inline` map, so every utility follows each block above |
| [exports/design-tokens.json](exports/design-tokens.json) | W3C DTCG, with `$value`, `$type` and `$description` per token |
| [exports/DESIGN.md](exports/DESIGN.md) | the long brief: every token with its role, plus the rules |
| [exports/DESIGN.compact.md](exports/DESIGN.compact.md) | the short brief, for a small context window |
| [fonts/fonts.css](fonts/fonts.css) | the house faces, Archivo, Literata and IBM Plex Mono, self-hosted as WOFF2 with each face's OFL text; no request leaves the product's origin |
| [ramps/brands/house.json](ramps/brands/house.json) | the **source** every file above is generated from: the neutral and the named hues, with [ramps/roles.css](ramps/roles.css) and [ramps/scales.css](ramps/scales.css) |

## Changing the system

[CONTRIBUTING.md](CONTRIBUTING.md) says how a change is proposed.
[AGENTS.md](AGENTS.md) holds the tools and the suite that checks them, the rules a change to a token or a rule is held to, what CI requires before a merge, and what the weekly maintenance job does and does not check.
[docs/publication-record.md](docs/publication-record.md) records how the first publication was scrubbed and verified.

## What is open

[The brand book's table](design/00-brand-book.md#what-the-house-has-and-what-it-does-not) is the full answer: two admitted surfaces with no sheet yet, three partly answered, and what the house declines with the reason for each.
The two worth knowing before you read anything else:

- **A localised, mirrored build** has no decision.
  Right-to-left text inside a left-to-right product is specified; whether any product ever mirrors its whole interface is open, and the recommendation is no.
- **There is no logomark and no wordmark.**
  A mark is a commission rather than something an agent invents.

## Licence

Apache-2.0.
See [LICENSE](LICENSE).

The typefaces this system ships - Archivo, Literata and IBM Plex Mono, all SIL OFL 1.1 - the icon set it chooses - Lucide, ISC - and the pictogram set - `@carbon/pictograms`, Apache-2.0 - are third-party and carry their own licences: each face's OFL text sits beside it in `fonts/`, and Lucide's sits beside the icons in `components/icons/`.
Every source the book relies on is named in the file that relies on it, with what was taken and what was left.
