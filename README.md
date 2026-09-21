# Halderworks Instrument

A design system for instruments of record: software whose job is to be trusted about a number, a
state or a record rather than to be admired.

One token set, two themes, two densities, fifteen components, and **154 inventoried surfaces** each
marked covered, partial or excluded. Every value traces to a measurement, and the repository carries
the tools that prove it.

[SKILL.md](SKILL.md) is the entry point for a model, and
[Building a screen with it](#building-a-screen-with-it) below is the one for a developer.
[design/05-coverage.md](design/05-coverage.md) answers "does this system cover X", and
[AGENTS.md](AGENTS.md) is for changing the system itself.

## What it is for

**A reader should be able to tell, from a screen built with this, that somebody decided.**

That is the whole outcome, and it is the reason for the discipline rather than a slogan on top of
it. A screen assembled from defaults is legible as such: nothing on it was chosen, so nothing on it
carries conviction, and a reader feels that before they can name it. Every rule in this book exists
because a default existed and was refused - a neutral ground against a tinted one, one accent hue
measured to sit outside the crowded corridor, colour spent only where a state is reported, a
headline set tight because it is read once.

The corollary is the working rule, and it cuts both ways: **a rule with no reason attached is
itself a default**, and adding rules does not add conviction. That is how "master design system"
and "not bloat" are the same requirement rather than two competing ones.

## What makes it different from a palette with opinions

- **Nothing was chosen and then checked.** Each colour is solved to a contrast target against the
  worst surface it is permitted to sit on. That discipline caught five defects no eyeball found,
  including a dark-theme focus ring at **2.56:1** inside a dialog and a control outline shipping at
  1.45:1 against a 3:1 bar. [design/90-evidence.md](design/90-evidence.md) lists all five.
- **The build refuses to emit an unsolved set.** `tools/build.py` clamps chroma into sRGB,
  re-solves lightness where a floor stops holding, and exits non-zero rather than writing a token
  file whose numbers are not true.
- **Rhythm is a checked property, not a claim.** The spacing scale, the type ramp and the
  line-heights now have a stated relationship, and the build refuses an off-unit space or size
  value that is not declared with a reason - in both directions, so the exception list cannot rot.
  [design/32-rhythm.md](design/32-rhythm.md) names the unit, measures a screen against it, and says
  where it is deliberately broken.
- **It reports its own gaps.** A coverage inventory that only lists what a system has cannot report
  what it lacks. This one was audited against six external component and accessibility taxonomies,
  which returned 34 rows it had never named, and `tools/check-coverage.py` now fails when a refusal
  written anywhere in the rules does not name the row that carries it.
- **It records what it declined.** [design/85-considered-and-declined.md](design/85-considered-and-declined.md)
  carries what was screened and refused, the reason, and what would change the answer.
- **Permission is a table, not a convention.** Two tokens both existing does not make them a pair.
  [design/15-color-combinations.md](design/15-color-combinations.md) is the permission list.

## Building a screen with it

For a developer on a Halderworks product with a screen to build. Every step names the one file
that owns it.

1. **Load the tokens.** Copy [tokens/tokens.css](tokens/tokens.css) into the product and import it
   before the product's own stylesheet, with the font link in
   [design/95-extending.md](design/95-extending.md#loading-the-system-in-a-product). A Tailwind v4
   project takes [exports/theme.css](exports/theme.css) instead. Dark theme is
   `data-theme="dark"` on the root, compact density is `data-density="compact"` on any ancestor, and
   with neither set the page follows `prefers-color-scheme`.
2. **Find the surface's row** in [design/05-coverage.md](design/05-coverage.md): it lists 154 surfaces, each
   `covered` with the section to read, `partial` with what is missing, or `excluded` with the
   reason. No row at all is a gap to report, not permission to invent.
3. **Build from the component card**, not from a screenshot:
   [design/65-components.md](design/65-components.md) has fifteen, and
   [design/66-forms.md](design/66-forms.md) every form control. Every colour, size, radius,
   duration, breakpoint and z-index is a `var(--hw-*)`; a literal is off-system.
4. **Pair an ink with a ground only from the table** in
   [design/15-color-combinations.md](design/15-color-combinations.md), which carries each permitted
   pair with its measured ratio. Two tokens both existing does not make them a pair.
5. **Give every control its states and keys** from [design/60-states.md](design/60-states.md) and
   [design/72-keyboard.md](design/72-keyboard.md).
6. **Answer the thirty questions** at the end of
   [design/80-anti-patterns.md](design/80-anti-patterns.md) against the finished screen.
7. **Where a value is missing, use the nearest house value and say so** in the pull request, in the
   form [design/95-extending.md](design/95-extending.md#reporting-a-gap) shows. Product-specific
   tokens go in the product's own namespace, `--quoth-`, never by redefining an `hw-` token.

A product takes its identity from a brand seed, eleven bounded inputs, and only by regenerating:
`python3 tools/build.py --brand examples/papertrace/brand.seed.json` solves a full set in the
house's own token names and refuses to write if one pair fails
([design/12-brand.md](design/12-brand.md)). At accent hue 150 it refuses, because that hue's ink
sits 6.1 CIEDE2000 from `hw-success` against the 14
[design/10-color.md](design/10-color.md#the-three-bars-the-accent-is-held-to) requires.

## How a model loads it

There is nothing to install and no runtime. The whole system is files.

1. Clone or vendor this repository where the model can read it.
2. Point the model at [SKILL.md](SKILL.md). It fires on "about to write or restyle any UI" and
   routes to the file that answers the question in hand.
3. If context is tight, [exports/DESIGN.compact.md](exports/DESIGN.compact.md) is the whole value
   set in one file. `SKILL.md` says exactly when that is enough and when reading it alone will
   produce off-system work.

For a harness with a skills directory, `SKILL.md` and this tree drop in unchanged. For anything
else, the file is ordinary Markdown with a YAML header and reads correctly without any harness at
all - that is deliberate, because a design system that only one vendor's model can load is a design
system with a vendor lock in it.

Other forms of the same values, for a tool that wants one:

| file | what it is |
|---|---|
| [tokens/tokens.css](tokens/tokens.css) | the custom properties a browser loads. Copy-pasteable into any product |
| [tokens/tokens.json](tokens/tokens.json) | the machine-readable set, with a role, a lifecycle state and an introduced version on every token |
| [tokens/tokens.seed.json](tokens/tokens.seed.json) | the **source** the two above are generated from: a hue seed, per-token lightness and chroma anchors, and the contrast floor each token must hold |
| [exports/theme.css](exports/theme.css) | a Tailwind v4 `@theme` block, mapped to Tailwind's namespaces so utilities generate |
| [exports/variables.css](exports/variables.css) | plain CSS custom properties, both themes, compact density and reduced motion |
| [exports/design-tokens.json](exports/design-tokens.json) | W3C DTCG, with `$value`, `$type` and `$description` per token |
| [exports/DESIGN.md](exports/DESIGN.md) | the long brief: every token with its role, plus the rules |
| [exports/DESIGN.compact.md](exports/DESIGN.compact.md) | the short brief, for a small context window |

## Changing the system

[CONTRIBUTING.md](CONTRIBUTING.md) says how a change is proposed. [AGENTS.md](AGENTS.md) holds the
tools and the suite that checks them, the rules a change to a token or a rule is held to, what CI
requires before a merge,
and what the weekly maintenance job does and does not check. [docs/publication-record.md](docs/publication-record.md) records how the
first publication was scrubbed and verified.

## What is open

[design/05-coverage.md](design/05-coverage.md) is the full answer and it is checkable. Eight rows are
`partial`, each naming what is missing, and two decisions are recorded as open with the
measurement already done and a recommendation on each - they are in
[that file's open-decisions table](design/05-coverage.md#open-decisions), beside the ones since
settled and why. The two worth knowing before you read anything else:

- **A localised, mirrored build** has no decision. Right-to-left text inside a left-to-right
  product is specified; whether any product ever mirrors its whole interface is open, and the
  recommendation is no.
- **There is no logomark and no wordmark.** A mark is a commission rather than something an agent
  invents.

## Licence

Apache-2.0. See [LICENSE](LICENSE).

The typefaces this system names - Public Sans, Newsreader, IBM Plex Mono - the icon set it
chooses - Lucide, ISC - and the pictogram set - `@carbon/pictograms`, Apache-2.0 - are third-party and carry their own licences, which
[design/55-iconography.md](design/55-iconography.md) and
[design/90-evidence.md](design/90-evidence.md) record as fetched rather than recalled. Nothing from
any reference measured in the evidence file is reproduced here: every spec-sheet entry states what
principle was taken and what expression was deliberately left behind, and an entry that could not
fill the second line was declined rather than shipped.
