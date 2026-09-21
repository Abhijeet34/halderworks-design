# Interaction states

Nine states, and every interactive element in the system answers all nine.
An element that answers seven of them is not finished; it has two states that fall back to whatever the browser does, which is a different answer per browser.

The word `disabled` appeared once in the whole first pass of this system.
That is what this file corrects.

## The matrix

`->` means "changes to". Anything not listed does not change.

| state | fill | ink | border | other |
|---|---|---|---|---|
| **rest** | per component | per component | per component | the baseline every other row is a delta from |
| **hover** | `-> --hw-surface-hover`, or `-> --hw-ink-hover` on a filled control | unchanged | unchanged | `--hw-duration-fast`, `--hw-ease-out` |
| **active** (pressed) | `-> --hw-surface-active`, or `-> --hw-ink-active` on a filled control | unchanged | unchanged | `--hw-duration-instant`. No transform, no scale |
| **focus-visible** | unchanged | unchanged | unchanged | `outline: 2px solid var(--hw-accent-ring)` at `outline-offset: 2px` |
| **disabled** | `-> --hw-surface-sunken` | `-> --hw-text-disabled` | `-> --hw-border` | `cursor: not-allowed`. No hover, no active, still focusable |
| **loading** | unchanged | unchanged | unchanged | label `-> verb in progress`, width held, `aria-busy="true"` |
| **selected** | `-> --hw-accent-quiet` | stays `--hw-text` | unchanged | `aria-selected` or `aria-current` |
| **error** | unchanged | unchanged | `-> --hw-danger` | a message below in `--hw-danger`, `aria-invalid="true"` |
| **read-only** | `-> --hw-surface-sunken` | stays `--hw-text` | `-> --hw-border` | `readonly`. Focusable, selectable, copyable |

## The rules behind the rows

### Hover is a fill, never a movement

Measured across the 41 sites in the capture whose own stylesheets are readable, hover is carried by `background-color` on 39, `color` on 38, `border-color` on 33, `opacity` on 33 and `transform` on 23.
The house choice is the first: one fill token, no `transform`.

A row that lifts on hover is a row that reflows a table of 400 rows as a pointer crosses it, and `transform` on hover is the single most common source of a list that stutters on the machine the product is actually used on.

Hover does not exist on touch.
Any state reachable only by hover must also be reachable by focus, which is why a row action appears on `:hover, :focus-within` and never on `:hover` alone.

### Active is faster than hover, and it is not a scale

`--hw-duration-instant` at 90ms, because a press must feel like a direct response rather than an animation.
No `scale(0.98)`. A button that shrinks when pressed is a button that moves its own label out from under the cursor.

A **filled** control takes its own ink step rather than a surface fill: `--hw-ink` at rest,
`--hw-ink-hover`, then `--hw-ink-active`. That third step exists because rendering this matrix
showed hover and active painting the identical colour on a primary button: the system had two ink
values and three states, on the one control that commits an action. `hw-ink-text` clears
10.68:1 on it in light and 10.60:1 in dark.

### focus-visible, never focus, and never removed

`:focus-visible`, so a pointer click does not paint a ring and a Tab key does.
32 of the 41 readable sites use `:focus-visible`; the 9 that use only plain `:focus` are all editorial or foundry sites rather than products.

The ring is `--hw-focus-w` 2px at `--hw-focus-offset` 2px.
2px is the measured value: 246 real `outline-width` declarations at 2px in the capture against 75 at 1px.

**`outline: none` is the most common focus declaration in the entire capture: 294 declarations across 26 of 41 sites.**
Most of those sites replace the ring with a `box-shadow`, which is a legitimate technique.
Some do not, and those are keyboard-inaccessible.
In this system the outline is never removed, because `--hw-accent-ring` is solved to clear 3:1 against every surface it can be drawn on precisely so that it can stay on.

That solve is not cosmetic. Solved against the ground alone, as the first pass did, the dark ring measured **2.56:1 on `--hw-surface-raised`**, which is a focus ring inside a dialog, where keyboard focus matters more than anywhere else on the screen.

The ring goes *inside* a scrolling container's padding, never around the container, so it is not clipped by `overflow: hidden`.

### Disabled is a solved colour, not an opacity

The first pass set disabled to 45% opacity.
Composited, `--hw-text` at 45% over `--hw-surface` measures **1.73:1 in light theme and 7.40:1 in dark**.
One opacity cannot mean one thing in two themes, and 1.73:1 is text nobody can read rather than text that reads as inactive.

So `--hw-text-disabled` is a solved token, held to the 3:1 non-text bar rather than to AA, per theme:

| | on `ground` | on `surface` | on `surface-sunken` |
|---|---:|---:|---:|
| light | 3.21 | 3.42 | 3.03 |
| dark | 3.51 | 3.26 | 3.64 |

WCAG exempts a disabled control from the contrast requirement.
The exemption is why the number is stated here anyway: it is the only thing standing between "disabled" and "invisible".

Three further rules:

- **A disabled control stays in the tab order** where the reason it is disabled is not obvious, so a screen-reader user can reach it and hear why.
  Where it is obvious, `disabled` is correct.
  Measured practice splits the same way: `cursor: not-allowed` on 21 sites, `pointer-events: none` on only 7.
- **A control disabled for a reason says the reason beside it**, not in a tooltip the pointer must find.
- `aria-disabled="true"` with a real handler that explains, rather than `disabled`, is the right choice for a submit button blocked by an unfilled field.
- **Inside a composite widget, `aria-disabled` is not a preference, it is the rule.** A disabled
  item in a menu, a listbox or a toolbar stays reachable by the arrow keys, because skipping it
  saves a sighted keyboard user a key press and costs a screen-reader user any chance of
  discovering it. [72-keyboard.md](72-keyboard.md) owns the distinction and the two cases it
  splits into.

### Loading holds the width

The label becomes the verb in progress and the button keeps its rest width, so the row does not reflow: `Revoke key` becomes `Revoking...` and nothing beside it moves.

A container that is loading uses a skeleton in `--hw-surface-active`, not a spinner.
A skeleton says what shape is coming; a spinner says the product does not know either.
Skeletons do not shimmer: the only thing in this system allowed to loop is a determinate progress indicator, per [40-motion.md](40-motion.md).

`aria-busy="true"` goes on the container that is loading, and the live region announces the outcome, not the start.

### Selected keeps its text colour

Selected fills with `--hw-accent-quiet` and the text stays `--hw-text`.
Text does not go accent-coloured when its row is selected: two signals for one state, and the weaker of the two is the one that fails for a colour-blind reader.

`aria-selected` for a selection inside a widget, `aria-current="page"` for the current item in navigation.
They are not interchangeable and 11 sites in the capture declare the first while 9 declare the second.

### Error is a border and a sentence

The border becomes `--hw-danger` and a message appears below in `--hw-danger`.
The fill does not change: a red field is a field whose own text is now sitting on an unsolved ground.

**The error replaces the hint, it does not stack under it.**
The message names the problem and the fix, and [25-content.md](25-content.md) owns its shape.

### Read-only is not disabled

Read-only text is `--hw-text`, fully legible, selectable and copyable, on `--hw-surface-sunken`.
Disabled text is `--hw-text-disabled` and is not meant to be read.

Confusing the two is how a hash, an id or a generated key ends up at 3:1 in a field the user was supposed to copy.
Only 6 of 41 sites declare a `readonly` rule at all, which is why this row is the one most often missing.

## Combining states

Precedence, highest first: **disabled, error, selected, active, hover**.
Focus-visible composes with all of them: a focused disabled control still shows its ring.

A disabled control shows no hover and no active state.
A selected row still hovers; the hover fill composites over the selected fill, which is why both are solved separately.

## What the consumer provides

The `:focus-visible` polyfill decision, the ARIA attribute for each state, the tab order, and the handler that is absent when a control is disabled.
This system provides the tokens and the rule for what each state looks like.
