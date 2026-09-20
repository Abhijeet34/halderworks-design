# Rhythm

[30-space-radius-elevation.md](30-space-radius-elevation.md) has a spacing scale.
[20-type.md](20-type.md) has a type ramp and a line-height for every step.
Until this file, **nothing said how the two relate** - so "on the grid" was a habit rather than a
property, and a reader had no way to check a screen against it.

This file states the relationship, gives the number, and names every place the system breaks it on
purpose. `tools/build.py` refuses to emit a token that breaks it by accident.

## The unit, and exactly what it governs

**4px.** It governs **space and size**: how far apart two things are, and how big a thing is.

| governed | not governed |
|---|---|
| every step of the spacing scale | **radius**, which is a curve rather than a distance along an axis |
| breakpoints, gutters, container widths, the rail, the panel | **line weight** - a border, a focus ring, an icon stroke. A 4px hairline is not a hairline |
| control heights, row heights, cell and field padding | **the line box**, which is where readability puts it and is the section below |
| icon sizes | **measure**, which is stated in `ch` because a pixel width means nothing until the face is known |

Measured over the four families the unit governs:

```text
35 space and size values on the 4px unit, 7 off it and all 7 declared with a reason.
```

That line is printed by every build. It is not a claim in prose; it is the build refusing to write
a token file in which it would be false.

## The seven exceptions, each with the reason it cannot be on the unit

Four of these are **consequences** rather than choices, which is the distinction that matters: a
control's height is the token and its padding is whatever is left.

| token | value | why it is off the unit |
|---|---:|---|
| `--hw-field-pad-y` | 7px | consequence. `--hw-control-h` is the token; the padding is what remains after the line box and the border. [65-components.md](65-components.md) records the 35.5px field beside a 32px button that this rule was written from |
| `--hw-field-pad-y-compact` | 3px | the same consequence at the compact control height |
| `--hw-cell-pad-y-compact` | 6px | the same consequence at the compact row height: 19.5px of line box plus 6px above and below is the 32px row |
| `--hw-icon-stroke` | 1.5px | a line weight rather than a distance. [55-iconography.md](55-iconography.md) solves it to a constant 1.5px *painted* stroke at every rendered size |
| `--hw-icon-gap` | 6px | optical rather than arithmetic: 4px reads as one object and 8px as two. The only value in the system chosen against two named bounds |
| `--hw-icon-sm` | 14px | beside 12px `label` text. On the unit it either matches the cap height at 12px, which is unreadable, or overshoots it at 16px |
| `--hw-space-2` | 2px | the badge's vertical inset. At 4px a `micro` badge stands taller than the label beside it and the row grows around it |

**Two of those reasons are new, and one is a correction.**
Before this file, `--hw-space-2` and `--hw-icon-gap` both claimed the gap between an icon and its
own label - at 2px and at 6px - with directly contradictory reasons attached, one saying 4px
"already reads as separate" and the other saying 4px "reads as one object".
[55-iconography.md](55-iconography.md) owns that gap and specifies 6px.
`--hw-space-2` now carries the job it actually has in [65-components.md](65-components.md), the
badge inset, and the build fails if a token in scope drifts off the unit without a reason.

## The line box is not on the unit, and that is the decision

This is the part a baseline grid would force and this system refuses.

| step | size | line-height | line box | on a 4px unit? |
|---|---:|---:|---:|:--:|
| `display-1` | 56px | 1.02 | 57.12px | no |
| `display-2` | 40px | 1.08 | 43.20px | no |
| `title-1` | 28px | 1.15 | 32.20px | no |
| `title-2` | 21px | 1.25 | 26.25px | no |
| `title-3` | 17px | 1.35 | 22.95px | no |
| `body-lg` | 17px | 1.60 | 27.20px | no |
| `body` | 15px | 1.55 | 23.25px | no |
| `body-sm` | 13px | 1.50 | 19.50px | no |
| `label` | 12px | 1.35 | 16.20px | no |
| `micro` | 11px | 1.20 | 13.20px | no |

**Zero of ten.** Not one line box in this system lands on the unit, and none is within half a pixel
of one.

That is a decision and it has a reason. A baseline grid puts every line box on a multiple of the
unit, which means choosing leading to satisfy arithmetic rather than to be read - `body` at 15px
would have to take 1.6 for a 24px box, and `body-sm` at 13px would have to take 1.538 for 20px.
The leading in this system is chosen per step, and the shape it makes is the actual rule:

**Leading is tightest at the top of the ramp, loosest in the middle, and tightens again at the
bottom.** 1.02 at `display-1` rising to **1.60** at `body-lg`, then falling back to 1.20 at `micro`.
A 56px headline at `body`'s 1.55 would have 31px of air inside a two-line headline; an 11px
uppercase eyebrow at 1.55 would float away from the heading it belongs to.

So the honest statement of this system's rhythm, and it is a rule a reader can hold:

> **The unit governs the space between things. Type governs the space inside them.**
> A block's outer spacing is a `--hw-space-*` token and therefore on the unit.
> A block's internal leading is a ramp value and therefore is not.

A reader who expects a baseline grid here and does not find one has found the decision, not a
defect.

## A screen measured against it

The app shell from [35-layout.md](35-layout.md), at or above `--hw-bp-lg`, with a title, a
paragraph and a table. Every vertical gap, top to bottom:

```text
                                          gap      token              /4
┌──────────────────────────────────────┐
│ rail 248px │  page margin 32px       │   32   --hw-gutter-lg         8
│            │  ┌────────────────────┐ │
│            │  │ Signing keys       │ │  32.2  title-1 line box       -  type
│            │  ├────────────────────┤ │   12   --hw-space-12          3
│            │  │ Keys this workspace│ │  23.25 body line box          -  type
│            │  │ has issued.        │ │
│            │  ├────────────────────┤ │   24   --hw-space-24          6
│            │  │ NAME    ISSUED  ...│ │  13.2  micro line box         -  type
│            │  ├────────────────────┤ │   12   --hw-cell-pad-y        3
│            │  │ ci-signer  12 Mar  │ │   44   --hw-row-h            11
│            │  │ release    04 Mar  │ │   44   --hw-row-h            11
│            │  └────────────────────┘ │
│            │                         │   48   --hw-space-48         12
│            │  [ Issue a key ]        │   32   --hw-control-h         8
└──────────────────────────────────────┘
```

**Every gap between two things is on the unit. Every height inside a thing is a line box or a
control height.** Eight values on the unit, three line boxes that are not.

Two things a reader should check on their own screen from this:

1. **Add up the gaps and the sum is a multiple of 4.** 32 + 12 + 24 + 12 + 48 + 32 = 160 = 40 x 4.
   If your column's gaps do not sum to a multiple of the unit, one of them is not a token.
2. **The row height is the token, not the sum of its parts.** `--hw-row-h` is 44px because
   [45-density.md](45-density.md) derives it - 19.5px of `body-sm` plus 12px above and below is
   43.5px - and then rounds it **onto the unit**. That rounding is the rhythm rule doing its job:
   the derived number is off the unit, the shipped token is on it, and the half pixel goes into the
   padding rather than into the row.

## Where it is deliberately broken

Four places, and each is a rule rather than a lapse.

- **Inside a control.** A field's vertical padding is whatever the height token leaves. Putting it
  on the unit would mean the control is no longer its stated height, and a field and a button
  beside it would stop lining up - which is question 20 on the ship checklist.
- **The optical gap.** `--hw-icon-gap` at 6px is the one value in this system chosen by eye against
  two named bounds rather than derived. It is off the unit because both neighbouring unit values
  are wrong in opposite directions.
- **Anything measured in `ch`.** `--hw-measure-ui` and `--hw-measure-prose` are 56ch and 68ch. A
  measure in pixels is a measure that changes meaning when the face does, which is the argument
  [35-layout.md](35-layout.md) already makes.
- **Vertical section rhythm on a page**, which varies on purpose. `--hw-space-48`, `--hw-space-64`
  and `--hw-space-96` are all on the unit, and a page that uses one of them for every section reads
  as generated. The unit says the gap is a token; it does not say the gaps are equal, and
  [80-anti-patterns.md](80-anti-patterns.md) carries the failure that comes from reading it that
  way.

## What this does not claim

**A screen on the unit is not automatically a screen with rhythm.** The unit removes the failure
[30-space-radius-elevation.md](30-space-radius-elevation.md) measures - 34 distinct spacing values
doing the work of about eight, with no interval the eye can lock onto. It does not supply the
intervals. Choosing 24 where 16 was right is a mistake the unit cannot see, and a column of gaps
reading 16, 16, 16, 16 is on the unit and has no rhythm at all.

What the unit gives a reader is the ability to **check**: a value that is not a token is visible,
and a value that is off the unit either has a name and a reason in the table above or the build
refuses to emit it.
