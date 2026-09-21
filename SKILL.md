---
name: halderworks-design
description: >-
  The house design system for Halderworks products. Load it BEFORE writing or restyling any user
  interface - a screen, a route, a component, a form, a table, a landing page, an email sign-in,
  a settings page, a chart, an icon row, a piece of UI copy - and before proposing a colour, a
  size, a radius, a duration, a breakpoint or a z-index. It carries one token set, two themes, two
  densities, 149 inventoried surfaces, and a rule that no value is invented: a value the system
  lacks is a gap to report, not a number to guess. Also load it when asked whether this system
  covers a surface at all, when a contrast ratio or an accessibility keyboard behaviour is in
  question, or when extending the system.
---

# Halderworks Instrument

You are about to build or change a user interface for a Halderworks product.
This system is what you build it from.

**It is plain files and plain Markdown by design.** There is nothing to install, no runtime, no
component library, and no dependency on which model or tool is reading it. Read the files.

## The four rules, which do not have exceptions

1. **Never write a literal colour, size, radius, duration, breakpoint or z-index.**
   Every one is a `var(--hw-*)` token. A value the system lacks is a gap to **report**, not a
   number to invent. `design/95-extending.md#reporting-a-gap` shows the sentence to write.
2. **Never decide a contrast ratio by eye.**
   Every ink-on-ground pair this system permits is in `design/15-color-combinations.md`, with its
   measured ratio. A pairing not in a table there is not a pairing you may reach for.
3. **Start from the component rule, not from a screenshot.**
   A button with the right colours and the wrong padding is still off-system.
4. **Run the closing checklist in `design/80-anti-patterns.md` before you call the screen done.**
   Thirty yes-or-no questions. It is the last gate.

## Step 0, and skipping it is the most expensive mistake available

**Before you build a surface, check whether this system already answers it.**

`design/05-coverage.md` lists **149 surfaces**, each marked `covered`, `partial` or `excluded`, and
it was audited against six external component and accessibility taxonomies so that it can report
what it does not have. Searching it takes one read and returns one of four answers:

| what you find | what it means |
|---|---|
| `covered` | the file and section that answers it. Go there |
| `partial` | it is half answered, and the row names exactly what is missing. Build the named half yourself and report it |
| `excluded` | this system decided not to have it, with the reason. Do not build it; say the row exists |
| nothing at all | a genuine gap. Say so, build the nearest thing from house tokens, and report it |

A surface the inventory never considered used to return silence, which reads as permission to
invent. That is why the inventory exists and why it is checked by a script.

## Which file answers your question

| you are about to | read, in this order |
|---|---|
| find out whether this system covers a thing at all | `design/05-coverage.md` |
| understand what these products are and why the system looks like this | `design/00-brand-book.md` |
| build or restyle any screen | `design/00-brand-book.md`, `design/35-layout.md`, then the component's section in `design/65-components.md` |
| pick a colour | `design/10-color.md` for the token, `design/15-color-combinations.md` for what it may sit on. **The pairing table is permission, not documentation** |
| set type | `design/20-type.md`. The tabular-figures rule is the one most often missed |
| write the words in it | `design/25-content.md` |
| space, round or elevate anything | `design/30-space-radius-elevation.md` |
| understand how the spacing scale and the type ramp relate, or check a screen's vertical rhythm | `design/32-rhythm.md` |
| lay out a page, pick a breakpoint, set a container width | `design/35-layout.md` |
| build for a shape other than a desktop window | `design/36-form-factors.md` |
| build a rail, a header, a footer, a toolbar or a table of contents | `design/37-navigation.md` |
| animate anything | `design/40-motion.md` |
| make a gesture dismiss something, or stack toasts | `design/74-interaction-constants.md` |
| build a dense screen, or add a compact mode | `design/45-density.md` |
| decide how a surface separates from the one behind it | `design/50-surface-texture.md` |
| draw or choose an icon | `design/55-iconography.md` |
| give a control its hover, focus, disabled or loading behaviour | `design/60-states.md` |
| build any of fifteen components | `design/65-components.md` |
| build a form, or any single control in one | `design/66-forms.md`, then `design/67-validation.md` |
| build a sign-in page or a settings page | `design/68-page-patterns.md` |
| make anything reachable by keyboard | `design/72-keyboard.md` |
| build a table, a list, an empty state or a chart | `design/70-data-display.md` |
| pick a theme overlay, a surface style, a format, a type treatment or a colour scheme | `design/75-spec-sheet.md` |
| ship | `design/80-anti-patterns.md`, checked against the screen |
| find out why a source, a tool or a technique was not adopted | `design/85-considered-and-declined.md` |
| argue with a value | `design/90-evidence.md`, which says where every number came from |
| add something the system does not have | `design/95-extending.md` |

## If your context is tight, read this instead

**`exports/DESIGN.compact.md`** is the whole system's values in one file, generated from the same
source as everything else, and it is about a tenth of the size of the book.

**When the compact brief is enough:**

- You are styling something the system already specifies and you only need its values.
- You are converting an existing screen to house tokens.
- You are answering a question about what a token is or what it is for.

**When it is not enough, and reading it alone will produce off-system work:**

- **You are building a component or a surface for the first time.** The compact brief carries
  values, not anatomy. `design/65-components.md` and `design/66-forms.md` are the anatomy, and a
  button with correct colours and wrong padding is the exact failure.
- **You are pairing an ink with a ground.** Permission lives in `design/15-color-combinations.md`
  and nowhere else. Two tokens both existing does not make them a pair.
- **You are making anything interactive.** `design/60-states.md` has nine states and
  `design/72-keyboard.md` has the key bindings, and neither is in the values.
- **You are asked whether the system covers something.** Only `design/05-coverage.md` can answer
  that, and a compact read that finds nothing will report a gap that is actually an exclusion.

Read `exports/DESIGN.compact.md` first and the specific file second. Do not read the compact brief
*instead of* the file that owns the thing you are building.

## Loading the tokens into a product

```html
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Public+Sans:ital,wght@0,100..900;1,100..900&family=Newsreader:ital,opsz,wght@0,6..72,200..800;1,6..72,200..800&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&display=swap">
```

```css
@import "tokens.css";          /* the house system: tokens/tokens.css in this repository */
@import "quoth/tokens.css";    /* the product's own namespace, loaded AFTER, never instead */
```

Every token is prefixed `hw-`, so it cannot collide with a framework's variables.
Dark theme is `[data-theme="dark"]`, and the system follows `prefers-color-scheme` when the page
has made no explicit choice. Compact density is `data-density="compact"` on any ancestor.

Other forms of the same system, for a tool that wants one: `exports/theme.css` is a Tailwind v4
`@theme` block, `exports/variables.css` is plain custom properties, `exports/design-tokens.json` is
W3C DTCG with a `$description` on every token.

## What you may and may not change

**One thing is a product's to change: the accent hue.**
Take it by regenerating, never by hand-picking a colour:

```bash
python3 tools/build.py --accent-hue 318 --out ./my-tokens
python3 tools/contrast.py ./my-tokens/tokens.css
```

The build re-solves every affected token against its contrast floor and **refuses to write** if one
does not hold. It also refuses a hue that sits closer than 8 in oklab distance to a semantic
colour, so a product cannot take a green that competes with "passed".
The second line is not a formality and it is not a second opinion from the same head: `contrast.py` shares no arithmetic with the build and carries its own list of what must hold.
Of the 360 integer hues, 147 build, and `contrast.py` accepts all 147.

**Everything else goes in the product's own namespace**, `--quoth-`, `--gates-`, never by
redefining an `hw-` token. `design/95-extending.md` is the whole procedure.

## Three things this system does that most do not, and why they matter to you

- **Every number traces to a measurement.** `design/90-evidence.md` names the sites, the packages,
  the commands and the counts behind each one. If you disagree with a value, argue with the
  measurement rather than with a preference.
- **It reports its own gaps.** `tools/check-coverage.py` fails when a refusal stated anywhere in
  the rules does not name the inventory row that carries it. That check exists because one refusal
  escaped for three rounds, and nothing else would have found it.
- **It says what it declined.** `design/85-considered-and-declined.md` records what was screened
  and refused, with the reason and what would change the answer. A question answered there does not
  need asking again.

Solve to the requirement. Checking afterwards only tells you what you already shipped.
