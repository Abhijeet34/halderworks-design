# Halderworks Instrument

The house design system for everything Halderworks ships: quoth, papertrace, pointback, treadling, foliot, gates and the tools around them.
This book is the foundations, written once, and the component sheets, generated from the catalogue that draws the components.
Every rule here names the file that enforces it, and a rule that no file enforces says so, because a rule a reader cannot check is a rule that drifts.

## What the products are

Everything in this portfolio is an instrument of record.
quoth captures speech and writes it down.
papertrace checks a manuscript's integrity on the author's own machine and reports the evidence rather than a verdict.
pointback carries a reviewer's pointing back to an agent.
treadling records what an agent was asked to do, did, and decided.
foliot orchestrates that work.
gates refuses a change that cannot prove itself.

The common job is not to be admired.
It is to be trusted about a number, a state or a record, so the system behaves like a calibrated instrument:

- **Colour means something or it is not there.**
  The loudest control on a screen is ink and carries no hue ([10-color.md](10-color.md#how-colour-is-spent)).
- **Nothing is decorated to look important.**
  Weight, size and position carry hierarchy; shadow and colour do not.
- **The type is set to be read for a long time**, at a size the reader chooses ([20-type.md](20-type.md#the-text-size-setting)).

## The rule that matters most

Every colour, size, radius, duration, breakpoint and z-index is a `var(--hw-*)` token.
A value the system lacks is a gap to report, not a number to invent: ship the screen with the nearest house value and say in the same breath what you needed.

> Used `--hw-space-24` for the pane divider; the pane wants about 28px and the scale has no step there.

That sentence is worth more than a correct-looking screen with `28px` written into it, because the next person hits the same gap and either finds the report or invents a second number.
`tests/components.py` refuses a literal colour, and any `px`, `ms` or `s` value, in the component layer that it does not list with a reason; it does not read `em`, `rem` or percentage values, and a product's own stylesheet is held to the rule by its review alone.

## Where each answer lives

| subject | the book | the files that enforce it |
|---|---|---|
| colour: ramps, roles, which ink may sit on which ground | [10-color.md](10-color.md) | `ramps/roles.css`, `tools/ramps.py`, `tools/contrast.py`, `tools/painted.py` |
| a product's identity | [12-brand.md](12-brand.md) | `ramps/brands/<name>.json`, `ramps/roster.json`, `tools/ramps.py`, `tools/contrast.py`, `tools/distinct.py` |
| type, faces and the text-size setting | [20-type.md](20-type.md) | `ramps/scales.css`, `components/components.css`, `fonts/`, `tools/faces.py`, `tests/exports.py` |
| space, size, radius, elevation, density and layout | [30-space.md](30-space.md) | `ramps/scales.css`, `tests/exports.py`; for radius, `ramps/roster.json` and `tools/contrast.py` |
| motion | [40-motion.md](40-motion.md) | `ramps/scales.css`, `components/components.css`, `tests/exports.py` |
| accessibility floors, states and keys | [60-accessibility.md](60-accessibility.md) | `tools/contrast.py`, `tests/exports.py`, `tests/components.py`, `components/components.css` |
| every component | [64-component-sheets.md](64-component-sheets.md) | `components/catalogue.py`, `components/components.css`, `tools/components.py` |

A component is documented once, in its sheet, which `tools/components.py` writes from the same catalogue entry that draws its rendered card.
No file in this book describes a component a second time.

## Two registers: the quiet page and the loud stage

**The quiet page** is every working view: a history, a settings screen, a report, review chrome.
It is ink and neutrals, one primary action in ink, and colour only where a state, a link, a selection or a mark is reported.

**The stage** is one component, [Stage](64-component-sheets.md#stage): a full field in the highlighter solid, the product's accent or ink, display type at the stage sizes, at most one action and one drawing.
It goes on a welcome, a site section or a store frame, and on an empty state at most once.
It never reaches a working view, and quoth's welcome stays on paper.
Anything loud a product wants lives there, which is how a vivid identity and a quiet instrument are the same product.

## The house signature: marks on paper

The products' shared subject is someone's words or someone's record, so the signature is the marks an editor puts on paper:

- **Highlight**, the words a product knows, in the yellow mark: a swipe behind ink in light, a block in mark step 7 under `--hw-text` in dark.
- **Proof marks**, what a product changed in someone's words: removed words struck in `--hw-delete`, inserted words in `--hw-insert` on its fill, with a caret under the line.
- **Diff**, changed lines with their context: ink text on `--hw-insert-fill` or `--hw-delete-fill`, with a sign.
- **Pin and margin note**, a numbered point on a page and the note it carries back.
- **Code**, an identifier or command exactly as written, in the mono face.

The colour is at full strength and the area it covers is a few words, so a list never has its brightest pixels on more than the words the product can explain.
Each mark's anatomy, states and keys are its sheet under [Marks, the house signature](64-component-sheets.md#marks-the-house-signature), and its colour roles are in `ramps/roles.css`, where `tools/contrast.py` certifies them.

## Words

The words are part of the system, and no tool checks them; review is their only enforcement.

- **Sentence case everywhere**: headings, buttons, labels, menu items, column heads, tabs, toasts and errors.
  Proper nouns keep their own case: `Sign in with GitHub`, `sha256`.
- **Name things the way the person names them.**
  A run, an artifact, a gate, a key; not a job, a blob, a validator, a credential record.
  One name per concept per product.
- **A control says what will happen, and the confirmation says it happened.**
  `Revoke key`, then `Key revoked`.
  Never `Submit`, never `Success!`.
- **An error says what went wrong and what to do.**
  "The signing key expired on 12 March. Generate a new one in Settings, Keys."
  Not "An error occurred."
- **Numbers carry their unit and their precision**: `04:12`, `$1.84`, `86 of 148 MB`, `sha256:77c2d4e…`.
  Never "a few minutes ago" where a timestamp is known.
  A column of figures is right-aligned and takes `tabular-nums` ([20-type.md](20-type.md#figures)).
- **No exclamation marks and no apologies.**
  The product is not sorry; it is telling you something.
- **Nothing invented.**
  No placeholder quote, logo, metric or record presented as real.

## Icons and art

The icon set is **Lucide**, under the ISC licence; the files the sheets use are vendored in `components/icons/` with that licence.
Every icon sits beside a word, except in a toolbar, where an icon-only button carries an `aria-label` and a tooltip.
Stroke and fill are `currentColor`, so an icon takes the colour of the text it sits in and never carries a state colour on its own.
[30-space.md](30-space.md#icons) has the sizes and the stroke.

Art is held to the owner's rules of 2026-09-22 and 2026-09-28, which no tool checks:

- **Nothing machine-made goes into any asset**, and nothing is bought: a product curates free, human-made sources whose licence allows use in a sold app, or draws its own real controls.
- **One kind of art per view**, and none beside an instrument surface, dense data, or a live signal.
- **Art never carries a state colour** and never moves.
- **No video, GIF, Lottie or Rive inside an app**; a recording of the shipped build belongs on a website or a store page.

The house's own pictograms, for a marketing section, are `@carbon/pictograms` (Apache-2.0) at `--hw-space-48` or `--hw-space-64` in `currentColor`; a product installs the package itself, and this repository vendors none of it.

## The mark

There is no logomark and no wordmark yet, because a mark is a commission rather than something an agent invents.
Until one exists, a product's name is set plainly in its brand's display face.

**One mark per screen, and it is the product's own.**
A mark answers whose screen this is, and a screen that answers twice makes the reader choose, so the house name, another product's name and an app icon beside the name are not added as further marks.
Checked on the render: count the elements that set a product or house name as a mark or draw a logo, and the count is one.

`halderworks.com` is the registered umbrella domain, and it is a name here rather than a link: its mail resolves, and no web host answers the apex yet.

## What the house has, and what it does not

The component sheets are the inventory: a surface with a sheet is the house's, and [64-component-sheets.md](64-component-sheets.md) lists every one.
Meter and sheet are admitted and have sheets, and print is answered by [the layer's print block](64-component-sheets.md#print).
Two more surfaces are admitted by the maintainer and have no sheet yet, so each is built from house components and reported as a gap:

| admitted, no sheet yet | build it from |
|---|---|
| Product tour and coachmarks | a popover anchored to the control it explains |
| Account and profile page | a key-value list and an avatar |

Three surfaces are partly answered, and the missing half is a gap to report:

| partial | what exists | what is missing |
|---|---|---|
| Banner and page-level alert | the [Callout](64-component-sheets.md#callout), inline | a page-level anatomy: placement, dismissal, its relation to a toast |
| Breadcrumb, pagination, command palette | nothing | all three; pagination bites first, on any table of hundreds of rows |
| A localised, mirrored build | right-to-left text inside a left-to-right page ([30-space.md](30-space.md#direction)) | a decision: no product mirrors its interface or ships a non-English one, and the recommendation is not to until one does |

These are decided against, each with its reason, and a decline is reversible when the reason stops holding:

| not in the house | why |
|---|---|
| Photography in a product surface, and an image lightbox | an instrument shows its record, not a picture of it |
| Sound and haptics as an interface signal | no product uses either; quoth records audio as content, which is not the same thing |
| Rich text and code editing | no product takes formatted input; an editor is a component with its own selection model and undo |
| Colour, rating, and tag or token input; input masks; payment inputs | these products take hashes, ids, durations and choices, which a mask fights rather than helps |
| Native mobile, HTML email, terminal output, watch, TV and voice | no product ships one; email and a terminal cannot read a custom property, so each needs its own export |
| Window splitter | a per-user layout the product must store, migrate and support |
| Tree view, treegrid, multi-level select and transfer list | no product displays a hierarchy; a list with a filter is the house answer |
| Range slider with two thumbs | no product filters a range |
| Feed and infinite scroll | it loses the footer and the reader's place |
| Notification centre | a centre is durable state a product must store, expire and mark read, and no product has an inbox |
| Step indicator and multi-step form | no product splits a form across screens |
| Timeline and activity log | a log is a table |
| Mentions | these are single-operator instruments with no second user to mention |
| Drag-to-reorder | no product orders anything by hand, and drag is never the only route to an action |

A surface in none of these tables and with no sheet is a genuine gap: build the nearest thing from house components and say so.

## Loading it in a product

```css
@import "hw/fonts/fonts.css";            /* the house faces, vendored with their OFL texts */
@import "hw/variables.css";              /* exports/variables.css, or examples/<brand>/exports/variables.css */
@import "hw/components/components.css";  /* the component layer, after the variables */
@import "product.css";                   /* the product's own namespace, loaded after, never instead */
```

Copy the whole `fonts/` directory, because `fonts/fonts.css` names its files by relative URL.
A brand whose faces are system stacks loads no `fonts.css`.
`components/radiogroup.js` is the one script, loaded once, for the segmented control's arrow keys.

A product extends in its own namespace, one prefix derived from its name, `--quoth-`, `--gates-`, and never by redefining an `hw-` token.
A composition over house tokens, `calc(var(--hw-row-h) * 3)`, is preferred to a constant, because it keeps tracking the house when a value moves.
A colour the house has no token for is a hue in the product's brand file, built and certified like every other ([12-brand.md](12-brand.md#a-colour-of-the-products-own)).

## Before a screen ships

Every answer is yes, and a no is a defect with the rule named beside it:

1. Is every colour, size, radius, duration, breakpoint and z-index a `var(--hw-*)`? ([the rule above](#the-rule-that-matters-most))
2. Is every ink on every ground a pair `tools/contrast.py` certifies? ([10-color.md](10-color.md#which-ink-may-sit-on-which-ground))
3. Is the primary action `--hw-ink`, and is there exactly one? ([10-color.md](10-color.md#how-colour-is-spent))
4. Does every state carry a word, and every chart series a direct label? ([60-accessibility.md](60-accessibility.md#colour-is-never-alone))
5. Is every component built from its sheet rather than from a screenshot? ([64-component-sheets.md](64-component-sheets.md))
6. Does the screen hold at every text size, S to XXL, and at 390, 768 and 1440px wide with no horizontal scroll? ([20-type.md](20-type.md#the-text-size-setting))
7. Can a keyboard reach every action, with the focus ring never removed? ([60-accessibility.md](60-accessibility.md#keys))
8. Does nothing move that [40-motion.md](40-motion.md#what-moves-on-its-own) does not allow?
9. Read it in dark and under `prefers-contrast: more`: has anything gone invisible?
10. Is every number real, with its unit, and is there one mark, the product's own?

The list removes the failures a default makes when nobody decided.
It does not supply judgement: a screen can answer yes to all of it and still answer the wrong question.
