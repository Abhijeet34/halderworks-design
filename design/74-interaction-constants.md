# Interaction constants

[40-motion.md](40-motion.md) says how long a thing takes and what curve it takes.
This file says what makes it start and what makes it stop: the thresholds a gesture has to clear, the
geometry a stack uses, and the one case where two properties in one transition take different
durations.

**Why it exists.** Swept across the whole book before this file, `swipe|velocity|drag|fling|flick`
returned three lines in two files and all three were about drag-and-drop file upload. This system
specified a dialog, a toast and a sheet, and said nothing anywhere about what happens when a finger
pushes one of them. [90-evidence.md](90-evidence.md) carries the shipped contracts this is
transcribed from.

**No new token is introduced here.** Every duration and curve below is an existing one, and where
this system's value differs from the source's, the difference is stated with its reason.

## What is dismissible, and how each one goes

| surface | pointer | keyboard | gesture |
|---|---|---|---|
| dialog | click the scrim | Escape | none. A modal decision is not swiped away |
| toast | its own close affordance, or its action | none - a toast never takes focus | swipe, per the contract below |
| the rail as a sheet below `--hw-bp-lg` | click outside | Escape | swipe toward its own edge |
| the menu-bar panel | click outside | Escape | none |
| menu, popover, tooltip | click outside | Escape | none |

**Dismissing is always the safe outcome**, which [65-components.md](65-components.md) already states
for the dialog. If dismissing would destroy something, the surface is wrong.

## The dismissal contract

A dragged surface closes when **either** of two independent thresholds is passed. Either is
sufficient; neither is required.

| threshold | value | what it catches |
|---|---|---|
| **velocity** | 0.4 px/ms at release, along the dismissal axis | a flick - a short, fast movement that never travelled far |
| **distance** | 0.25 of the surface's own dimension along that axis | a deliberate drag - a slow movement that went most of the way |

**Provenance, stated because these two numbers are not this system's own measurements.** Both are
the shipped constants of `vaul@1.1.2` (`VELOCITY_THRESHOLD = 0.4`, `CLOSE_THRESHOLD = 0.25`), read
from its source. They are adopted as the field's working answer and have **not** been re-measured
here. A product that finds either wrong on its own surface should report the number it measured;
that is a finding, and [95-extending.md](95-extending.md) says what to do with one.

**Why two thresholds rather than one.** A single distance threshold refuses a flick that the user
clearly meant. A single velocity threshold refuses a careful drag all the way across. Each one alone
produces a surface that feels like it ignores you, in opposite circumstances.

### The settle, in this system's own values

When a drag is released and neither threshold is passed, the surface returns.
When one is passed, it leaves.

| | value | why not the source's |
|---|---|---|
| duration | `--hw-duration-slow`, 380ms | `vaul` settles at 500ms. 380ms is this system's existing token for a dialog or a sheet, which is the same class of movement over the same kind of distance. Taking 500ms would mean adding a fifth duration to match somebody else's number |
| easing | `--hw-ease-out` | `vaul`'s only curve is `cubic-bezier(0.32, 0.72, 0, 1)`. On the quarter-point axis in [90-evidence.md](90-evidence.md) that curve sits at **0.779** and `--hw-ease-out` at **0.765** - 1.4 points apart on a scale whose two ends are 0.099 and 0.849. They are the same shape, so this system needs no fourth curve |

### Dismissal: rules

- **The gesture never removes the other two routes.** Every surface in the table above keeps its
  pointer route and its keyboard route whether or not a gesture exists. A dismissal that only works
  by swipe does not exist for a keyboard.
- **The surface follows the finger during the drag, 1:1, and resists past its own edge.** A surface
  that moves at half the finger's speed reports that it is not being dragged.
- **Under `prefers-reduced-motion`, the thresholds stand and the settle collapses.** The
  accommodation is about movement, not about whether the gesture works;
  [40-motion.md](40-motion.md)'s reduced-motion block already collapses `--hw-duration-slow` to
  100ms, and that is the whole change.

**`vaul`'s nested-drawer displacement of 16px is deliberately not adopted.** This system has exactly
one sheet - the rail below `--hw-bp-lg`, specified in
[36-form-factors.md](36-form-factors.md) - and nothing can open a second one over it. A displacement
constant for a case the system forbids is a value with no caller.

## Toast stack geometry

[65-components.md](65-components.md) says toasts stack downward from one corner, newest nearest that
corner, maximum three visible, and the fourth replaces the oldest.
**That is a count with no geometry, and two implementations of it will not look alike.**

| position behind the front | scale | offset from the front |
|---|---:|---|
| 0, the front toast | 1.00 | 0 |
| 1 | 0.95 | one `--hw-space-8` |
| 2 | 0.90 | two `--hw-space-8` |

Scale step **0.05 per position**, offset **one gap per position**, transcribed from `sonner@2.0.8`'s
`--scale: var(--toasts-before) * 0.05 + 1`. The gap is this system's `--hw-space-8`.

### Stack: rules

- **The stack is a depth cue, not content.** Only the front toast is read. That is what makes
  scaling acceptable here when [20-type.md](20-type.md) otherwise fixes type to the ramp: a toast at
  0.90 is not text anybody is reading at 0.90, it is an edge saying two more exist.
- **Three visible, and the third is the last one that scales.** A fourth position would be 0.85,
  which is small enough to read as a rendering artefact rather than as a stack.
- **A toast does not scale while it is the front one.** Entry and exit are opacity and translate at
  `--hw-duration-base` ([65-components.md](65-components.md)); the scale changes only when a toast
  moves back a position.
- **Under `prefers-reduced-motion` the positions still apply and the transitions between them
  collapse.** The stack is information about how many are waiting.

## Two properties in one transition

[40-motion.md](40-motion.md) assigns one duration per interaction kind. That is correct and it is
coarser by one dimension, which shows up in exactly two places.

**A shadow settles one step faster than the geometry it belongs to.**

| the move | geometry | its shadow |
|---|---|---|
| a dialog entering | `--hw-duration-slow`, 380ms | `--hw-duration-base`, 220ms |
| a toast entering or changing position | `--hw-duration-base`, 220ms | `--hw-duration-fast`, 150ms |

The source practice is `sonner`, which gives `box-shadow` half the geometry's duration everywhere
the two appear together. Expressed on this system's four-step ladder that is one step, which lands
at 0.58 and 0.68 rather than exactly 0.50 - stated rather than rounded, because a shadow duration
invented to hit 0.50 exactly would need a fifth duration token.

The reason the rule exists at all: a shadow that grows for as long as the surface moves reads as the
shadow being dragged behind it. Landing the shadow first is what makes the surface look like it
arrived.

**On exit, the fade leads the move.**

```css
transition: transform var(--hw-duration-base), opacity var(--hw-duration-fast);
```

`sonner`'s exit pairing gives the fade two and a half times the urgency of the move. One step on this
system's ladder is 150 against 220. The effect is the same and the reason is that on the way out the
reader has stopped attending to the thing, so it should be gone before it has finished going.

**This is the only place in the system where one transition carries two durations**, and it applies
only to the pairings in the table above. Everywhere else, one interaction is one duration.

A gesture is a promise about what the surface will do. Two thresholds is how it keeps it in both
directions.
