# Surface and texture

How a surface is distinguished from the one behind it, and what is allowed to carry that distinction.

## There is no texture, and that is a decision
<!-- covered-by: Texture, grain, gradient, glass -->

**No noise, no grain, no paper, no gradient, no glass behind text.**
The system has no token for any of them and will not be given one.

**One exception, added in the fourth pass and scoped by a measurement rather than by taste.**
The reason below is that a contrast ratio is computed against one background colour, so a texture makes every certified number an approximation.
That is exactly true of grain, photography and glass, whose luminance at a given pixel is unknown.
It is **not** true of a deterministic two-colour pattern, whose worst pixel is a named token: certify the ink against the darker of the two and the number is as real as any other here.
So a ground may carry a pattern only where every pixel of it is a solved token and every ink on it is certified against the **worst** of those tokens, and a ground whose pixels are not enumerable carries no text at all and must say so on its face.
[75-spec-sheet.md](75-spec-sheet.md) owns the three surface styles that rule permits and their certified permission lists; the first of them immediately refused `--hw-text-muted`, which measures 4.01:1 against `--hw-border` in light theme and 3.89:1 in dark.

This is a decision rather than an omission, and the absence of the word `texture` from a design system is not the same as a system having decided against it.
The evidence, from the same 44-site capture described in [90-evidence.md](90-evidence.md):

| treatment | sites carrying it, of 44 |
|---|---:|
| a noise, grain or pattern image on any element 80x40 or larger | **2** (Linear, Sentry) |
| `backdrop-filter`, the glassmorphism primitive | **8** |
| a gradient on any element 80x40 or larger | **14** |

Two of forty-four is not a technique the field uses; it is two products that had a reason.
Linear's is a 2-element SVG data-URI grain over a dark hero, and Sentry's is a single welcome-page background image.
Neither is on a surface that carries data.

The house reason is stronger than the count.
Everything in this portfolio is an instrument of record, and a textured ground is a ground with an unknown luminance at any given pixel.
A contrast ratio is computed against one background colour.
Put grain behind text and the number the system certifies stops describing the thing on the screen, so the whole solved palette in [10-color.md](10-color.md) becomes an approximation.

Glass is the same failure with a worse constant: a `backdrop-filter` surface takes its luminance from whatever scrolls under it, so its contrast against its own text changes as the user scrolls.

## The four ways a surface may separate

In order of preference.
Reach for the next one only when the one above cannot do the job.

| level | how it separates | where | shadow |
|---|---|---|---|
| **flat** | nothing. It sits on the ground it is given | a page section, a form group, a heading block | none |
| **filled** | a fill one step off its parent: `--hw-surface` on `--hw-ground`, or `--hw-surface-sunken` as a well | a card body, the app rail, a code block, a **read-only or disabled** field | none |
| **bordered** | a 1px `--hw-border` hairline, with or without a fill | a card, a table, a panel. The default for anything that contains something | none |
| **floating** | bordered, on `--hw-surface-raised`, plus one shadow | only something that floats over content and can be dismissed | one |

The two shadow tokens are light-theme only **inside a window**.
In dark theme a shadow is invisible against a dark ground, so dark elevation is carried by surface lightness instead: `--hw-surface` at L 0.196 against `--hw-surface-raised` at L 0.232.
A panel floating over the user's desktop is the one exception and keeps its shadow in both themes, because none of our surfaces is underneath it; see [36-form-factors.md](36-form-factors.md).
In light theme both are the same white and the shadow is the only thing separating them.
That asymmetry is the design, not an oversight.

**If a thing cannot be dismissed, it does not float.**
A card is not above the page. A table is not above the page. A section is not above the page.

### Under forced colours

`forced-colors: active` means the user agent has replaced this palette with the reader's system colours.
Backgrounds flatten to one system colour and shadows are removed; borders and outlines are repainted in a system colour and survive.
So flat loses nothing it had, bordered and floating keep their hairline, and **filled loses its only edge**: a card body, the app rail, a code block, a well and a disabled field all become the page.

The filled level therefore carries a border it does not show:

```css
/* whichever selector a product gives its filled level */
.card-body, .app-rail, .well { border: 1px solid transparent; }
```

In every normal rendering it is invisible, because the element's own fill paints under it; under forced colours the user agent repaints it and the edge comes back.
It is a border rather than an outline because the outline is the focus ring in [60-states.md](60-states.md), and because a border keeps a filled box exactly the size of its bordered sibling, so moving a surface between the two levels shifts nothing.
A filled element that already has a border, such as a field on the shared box model, needs nothing.

**Taken:** from `govuk-frontend@6.5.0`, where 8 of 39 component stylesheets carry a `forced-colors: active` block and the source states the reason - "backgrounds and box-shadows disappear, so we need to ensure there's a transparent outline which will be set to a visible colour".
**Left behind:** its use of an outline, which here would collide with the focus ring.

No tool checks this rule: nothing in `tools/` reads a CSS snippet in this book, so review is its only enforcement until a lint over the snippets exists.

## Which step to use

`--hw-surface` and `--hw-surface-sunken` are not interchangeable and the difference is direction.

- **`--hw-surface` comes forward.** It holds a thing: a card, a row, a table body, a dialog.
- **`--hw-surface-sunken` recedes.** It is a well that something sits in: the rail, a code block, a table's own footer, a card's action footer, and a **read-only or disabled** field.
  A field at rest is `--hw-surface`, not sunken: the sunken fill is reserved so that it says "not for typing into" and nothing in the field family competes with it. [66-forms.md](66-forms.md) settles that, which the first two passes left contradictory between this file and [65-components.md](65-components.md).

Nesting a raised surface inside a sunken one is correct.
Nesting a sunken surface inside a sunken one is not: two wells with no lip between them read as one well with a seam.

Measured separations, so a step is a number rather than an impression:

| pair | light | dark |
|---|---:|---:|
| `--hw-surface-hover` off `--hw-surface` | 1.083:1 | 1.042:1 |
| `--hw-surface-active` off `--hw-surface` | 1.129:1 | 1.087:1 |
| `--hw-surface-sunken` off `--hw-ground` | 1.043:1 | 1.132:1 |

These are deliberately small.
A hover fill that reads as a colour change is a hover fill that makes a table flash as the pointer crosses it.

## Borders

One border token at one width.
`--hw-border-w` is 1px and there is no 2px border in this system: a 2px line is a state, which is why the only two 2px strokes that exist are `--hw-focus-w` and `--hw-tab-active-w`. <!-- covered-by: Borders -->

A border separates a container from its ground.
It does not separate every row from every other row: a rule between every row is a table that needed row spacing, and that has its own entry in [80-anti-patterns.md](80-anti-patterns.md).

`--hw-border-strong` is for a control outline that must be found without hovering: an input, a select, a secondary button.
That outline is held to 3:1 by WCAG 2.2 SC 1.4.11, which the first two passes did not check and did not meet; it is re-solved and the table is in [15-color-combinations.md](15-color-combinations.md).
It is not a heavier version of `--hw-border` to be reached for when a card looks weak.
A card that looks weak is usually a card that should not have been a card.

In dark theme the references use a translucent white border rather than an opaque grey: Linear `rgba(255,255,255,0.08)` at 61 uses, Resend `rgba(214,235,253,0.19)` at 64.
An alpha border composites over whatever surface it lands on, so one token stays coherent across every elevation.
This system's `--hw-border` is opaque in both themes, which is the simpler choice and the one a reader can compute.
If a product needs a border that reads correctly across three stacked dark surfaces, an alpha override is the sanctioned exception and [95-extending.md](95-extending.md) says how to declare it.

## The scrim

`--hw-scrim` dims the page behind a dialog and nothing else.
Nothing else dims the page: not a loading state, not a menu, not a drawer.
A scrim is a claim that the rest of the interface is unavailable, and that claim is true exactly when a modal dialog is open.

Separate a surface with a fill, then a border, and only then with a shadow.
