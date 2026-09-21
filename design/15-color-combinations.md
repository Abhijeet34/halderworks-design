# Colour combinations

[10-color.md](10-color.md) says what the colours are.
This file says which ones go together, which is the layer that stops a correct token set producing an incoherent screen.

Read this as permission.
A pairing that is not in a table here is not a pairing you may reach for; it is a gap to report.

## Ink on ground

A text token may sit on any ground whose cell shows a ratio, and on no other.
Every figure is the measured WCAG contrast ratio of the two solved tokens, not an estimate.

### Light

| ink | on `ground` | on `surface` | on `surface-hover` | on `surface-active` | on `surface-sunken` |
|---|---:|---:|---:|---:|---:|
| `hw-text` | 14.83 | 15.78 | 14.57 | 13.98 | 13.98 |
| `hw-text-secondary` | 6.37 | 6.78 | 6.26 | 6.00 | 6.00 |
| `hw-text-muted` | 4.88 | 5.20 | 4.80 | 4.60 | 4.60 |
| `hw-accent` | 5.09 | 5.42 | 5.00 | 4.80 | 4.80 |
| `hw-success` | 5.10 | 5.42 | 5.01 | 4.80 | 4.80 |
| `hw-warning` | 5.10 | 5.43 | 5.01 | 4.81 | 4.81 |
| `hw-danger` | 5.09 | 5.42 | 5.00 | 4.80 | 4.80 |

### Dark

| ink | on `ground` | on `surface` | on `surface-hover` | on `surface-active` | on `surface-raised` | on `surface-sunken` |
|---|---:|---:|---:|---:|---:|---:|
| `hw-text` | 16.38 | 15.23 | 14.62 | 14.02 | 14.02 | 16.98 |
| `hw-text-secondary` | 7.01 | 6.52 | 6.25 | 6.00 | 6.00 | 7.27 |
| `hw-text-muted` | 5.38 | 5.00 | 4.80 | 4.60 | 4.60 | 5.58 |
| `hw-accent` | 5.60 | 5.21 | 5.00 | 4.79 | 4.79 | 5.80 |
| `hw-success` | 5.61 | 5.22 | 5.01 | 4.80 | 4.80 | 5.82 |
| `hw-warning` | 5.61 | 5.22 | 5.01 | 4.80 | 4.80 | 5.82 |
| `hw-danger` | 5.61 | 5.22 | 5.01 | 4.80 | 4.80 | 5.82 |

`hw-ink-text` on `hw-ink`: 17.63 light, 17.36 dark.
That is the only pairing either of those two tokens has.

## Ink on a quiet fill

A quiet fill is the ground for a selected row, a status pill or a callout.
The first pass of this system told you to put `hw-accent` on `hw-accent-quiet` and never certified the pair; in dark theme it measured **4.37:1**, below AA, and `hw-success` on `hw-success-quiet` measured **4.46:1**.
Both fills have been re-solved. These are the pairs as they now stand:

| ink | on its own quiet fill, light | dark |
|---|---:|---:|
| `hw-accent` on `hw-accent-quiet` | 4.60 | 4.60 |
| `hw-success` on `hw-success-quiet` | 4.60 | 4.61 |
| `hw-warning` on `hw-warning-quiet` | 4.60 | 4.59 |
| `hw-danger` on `hw-danger-quiet` | 4.61 | 4.59 |
| `hw-text` on any quiet fill | 13.37 to 13.42 | 13.41 to 13.45 |

**Exactly two inks may sit on a quiet fill: its own semantic, or `hw-text`.**
`hw-text-secondary` on `hw-accent-quiet` is not in this table, so it is not permitted.

**A quiet fill never sits on the same quiet fill.**
An accent badge inside a selected row is `hw-accent-quiet` on `hw-accent-quiet`: 1.00:1, so the
badge's pill vanishes and only its text remains, which reads as a rendering bug rather than as a
badge. On a row already carrying that fill the badge drops its own fill and keeps its dot and its
word. This was found by rendering the app shell, not by reading the table, which is the argument
for rendering every pairing rather than certifying it on paper.

## Accent and its ground

The accent is spent on four things and nothing else: a link, a selected row, a live state, and the focus ring.

| use | ink | ground |
|---|---|---|
| link in running text | `hw-accent` | whatever the text sits on |
| selected list row or card | `hw-text` | `hw-accent-quiet` |
| live or active badge | `hw-accent` | `hw-accent-quiet` |
| focus ring | `hw-accent-ring`, 2px at 2px offset | the control's own ground |
| active tab rule | `hw-accent`, 2px | over the `hw-border` baseline |

The accent is never the fill of a primary button.
That is `hw-ink`, which carries no hue, and the reason is in [10-color.md](10-color.md): where a whole page is one accent, the accent stops meaning anything.

## Semantic and its quiet fill

| state | ink | fill | border, when the container itself is in that state |
|---|---|---|---|
| passed, verified, settled | `hw-success` | `hw-success-quiet` | `hw-success` |
| retried, degraded, expiring | `hw-warning` | `hw-warning-quiet` | `hw-warning` |
| failed, revoked, expired | `hw-danger` | `hw-danger-quiet` | `hw-danger` |
| live, selected | `hw-accent` | `hw-accent-quiet` | `hw-accent` |

**A semantic colour never appears without a word beside it.**
A row of coloured dots with no labels fails for the roughly 8% of men with a colour vision deficiency, and it fails for anyone reading a screenshot.

## What must never sit on what

Each of these is a real pairing an agent reaches for, and each is refused.

| never | why | instead |
|---|---|---|
| `hw-text-secondary` or `hw-text-muted` on any quiet fill | not solved for it, and not in the table above | `hw-text`, or the fill's own semantic |
| any ink on `hw-accent` as a fill | the accent is an ink and a 2px ring. It is not a surface | `hw-ink` with `hw-ink-text` for a filled control; `hw-accent-quiet` for a tinted one |
| `hw-accent` on `hw-ink` | 3.30:1 light, 3.07:1 dark: below AA for text, and two strong values neither of which is legible on the other | `hw-ink-text` on `hw-ink` |
| a semantic ink on a different semantic's quiet fill | `hw-danger` on `hw-warning-quiet` says two contradictory things | one state per element |
| `hw-text-muted` on `hw-surface-active` | 4.60:1 clears AA, but muted text on a pressed row is text nobody was meant to read while pressing | `hw-text-secondary` |
| any text on `--hw-scrim` | the scrim composites over unknown content | put the text in the dialog |
| `hw-border` as an ink | it is 1.30:1 against its own surface by construction | `hw-text-muted` is the lightest ink that exists |
| two chart colours adjacent as large fills | they alternate in lightness and are held 8.0 apart, but neighbours still measure only 2.20 to 2.47:1 in light and 1.59 to 1.74:1 in dark, under the 3:1 a boundary needs | keep `--hw-border` or a gap between chart segments |

## A control's boundary, which is a third bar

A text token is held to 4.5:1 and a non-text indicator to 3:1.
A **control boundary** is the third case and it is held to 3:1 by WCAG 2.2 SC 1.4.11, because it is the visual information that says where the control is.

The first two passes of this system missed it.
`hw-border-strong` is the token [50-surface-texture.md](50-surface-texture.md) assigns to an input, a select and a secondary button, and it measured **1.45:1 to 2.14:1** across the surfaces it sits on, in both themes.
This file printed `1.64:1` for it as an argument against using it as an ink and never checked it against the bar it actually had to clear, which is the same habit as the 2.56:1 focus ring: a number measured for one question and never asked the other.

It is re-solved against the surface closest to it in lightness.

| `hw-border-strong` on | light | dark |
|---|---:|---:|
| `hw-surface` | 3.42 | 3.29 |
| `hw-ground` | 3.21 | 3.54 |
| `hw-surface-raised` | 3.42 | **3.03** |
| `hw-surface-sunken` | **3.03** | 3.67 |
| `hw-surface-hover` | 3.16 | 3.16 |
| `hw-surface-active` | **3.03** | 3.03 |

Every control boundary in [66-forms.md](66-forms.md) uses this token: the field outline, the unchecked checkbox and radio, the switch track, the slider rail, the stepper divider, the selected segment of a segmented control, and a floating panel's edge.

**A fill is not a boundary.**
`hw-surface` against `hw-surface-sunken` is 1.129:1 in light and 1.115:1 in dark, so a segmented control whose selected segment is only a fill has no certified way to say which segment is selected.
It takes the border as well, and that is why.

## Composing a screen from this

A screen that follows this file uses, in a typical case, four colours and no more:

1. `--hw-ground` for the page.
2. `--hw-surface` with `--hw-border` for whatever holds content.
3. `--hw-text` and `--hw-text-secondary` for everything readable.
4. `--hw-ink` for the one action the screen exists for.

The accent and the semantics appear only where a state is being reported.
A screen with no state on it should have no hue on it, and that is a check, not a coincidence.
