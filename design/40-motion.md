# Motion

Four durations, three easings, and a short list of what is allowed to move at all.

| token | value | what it is for |
|---|---:|---|
| `duration-instant` | 90ms | a state flip that must feel like a direct response: checkbox, toggle, hover on a dense row |
| `duration-fast` | 150ms | the default. Hover, focus ring, colour change, a small reveal |
| `duration-base` | 220ms | enter and exit of a popover, menu, tooltip or toast |
| `duration-slow` | 380ms | a dialog or a sheet, which moves a longer distance |

150ms is the default because it is the measured modal value. Sampling `transition-duration` across all 14 reference products, 0.15s is the most-used duration on seven of them and 0.2s on five.
Durations above 0.5s exist in that set (Linear 0.7s, Stripe 0.8s, Vercel and Family 1s) and every one of them is attached to a hero or a scroll effect, never to a control.

## Easing

| token | curve | where |
|---|---|---|
| `ease-out` | `cubic-bezier(0.22, 1, 0.36, 1)` | the default. Anything entering, expanding, or responding to a click |
| `ease-in` | `cubic-bezier(0.4, 0, 1, 1)` | exits only, and only when something is leaving the screen entirely |
| `ease-standard` | `cubic-bezier(0.4, 0, 0.2, 1)` | a position change that both starts and ends on screen |

The default is out-biased on purpose, and the evidence for that is in what the distinctive products chose versus what everyone inherited.
`cubic-bezier(0.4, 0, 0.2, 1)` is the most common curve in the reference set, but it is Tailwind's shipped default, so its frequency measures adoption of a framework rather than a preference.
The custom curves people actually wrote are out-biased: Stripe `cubic-bezier(0.25, 1, 0.5, 1)` at 605 uses, Linear `cubic-bezier(0.32, 0.72, 0, 1)` and `cubic-bezier(0.25, 0.46, 0.45, 0.94)`, Superlist `cubic-bezier(0.44, 0, 0.56, 1)`.
Fast start, long settle. That is what makes an interface feel like it answered you rather than like it is playing an animation at you.

## What may animate

`opacity`, `transform`, `background-color`, `border-color`, `color`, `outline-color`, `box-shadow`.

Nothing else. In particular: never `height`, `width`, `top`, `left`, or `margin`. Those force layout on every frame, and on a table of a few hundred rows they will drop frames on the machine the product is actually used on.
Where a height must animate, animate `transform: scaleY()` on a wrapper, or `grid-template-rows` from `0fr` to `1fr`, which the compositor can handle.

No loop runs longer than 1.2s, and the only thing allowed to loop at all is a determinate progress indicator.
A spinner that spins forever is telling the user nothing except that the product does not know either.

## A product's own transition

The four durations and three curves are the house's in every product, and no brand input moves them ([12-brand.md](12-brand.md#declined-as-inputs)).
One exception lives in a product's own namespace: **one named transition**, the product's defining moment, that moves a large distance, such as quoth's recording panel appearing.
It is a `--quoth-` token, it takes a house duration, it may take a curve of its own, and it is removed under `prefers-reduced-motion` like every other movement.

The reason one is allowed and a brand-wide curve is not is a measurement.
Three alternative ease-out curves, sampled at 60Hz against the house curve, differ from it by at most 18.9% of the travel: 1.5px on the 8px a control moves, which nobody sees, and 30 to 60px on a 320px panel, which everybody does.
A curve is identity only where the distance is large enough to show it.

## Reduced motion

Under `prefers-reduced-motion: reduce`, movement goes and feedback stays.

```css
@media (prefers-reduced-motion: reduce) {
  :root {
    --hw-duration-instant: 1ms;
    --hw-duration-fast: 100ms;
    --hw-duration-base: 100ms;
    --hw-duration-slow: 100ms;
  }
  *, *::before, *::after {
    animation-duration: 1ms !important;
    animation-iteration-count: 1 !important;
    transition-property: opacity, color, background-color, border-color, outline-color !important;
    scroll-behavior: auto !important;
  }
}
```

The `transition-property` override is the part that matters and the part usually got wrong.
Blanket rules of the form `transition: none !important` remove colour and opacity transitions along with the movement, and a button whose state changes with no transition at all reads as a broken control rather than as an accommodation.
Reduced motion is a request to stop moving things, not a request to make the interface feel dead.

**Two widely used sources ship the exact error this rule was written against.** `sonner@2.0.8`
sets `transition: none !important` and `animation: none !important` under
`prefers-reduced-motion`, and a published design-reference skill does the same in its own
shortcut. Two unrelated sources committing the same error independently is what moves this from a
defensible opinion to a rule with two shipped counter-examples behind it, and
[90-evidence.md](90-evidence.md) carries both.

## What starts and stops a movement

This file owns how long a thing takes and what curve it takes.
[74-interaction-constants.md](74-interaction-constants.md) owns what makes it start and stop: the
velocity and distance thresholds a dismissal gesture has to clear, the toast stack's scale and
offset, and the one case where two properties inside one transition take different durations.

That last one is a real limit of the table above, stated rather than left to be discovered: this
file assigns one duration per interaction kind, which is correct and is coarser by one dimension
than the field's practice. The two pairings where it matters are in that file and nowhere else.

## What these three curves are, measured

[90-evidence.md](90-evidence.md) puts all three on one axis against 14 other published curves,
using the fraction of the change already done at the quarter point. Three readings belong here:

- **`--hw-ease-out` is 0.765**, fourth most out-biased of the seventeen measured. The claim above
  that it is out-biased on purpose now has a number rather than an adjective.
- **Base Web ships `cubic-bezier(0.22, 1, 0.36, 1)` as its own `easeDecelerate`**, byte-for-byte
  this system's `--hw-ease-out`, arrived at independently by a published design system. That is
  the strongest confirmation any single value in this book has.
- **`--hw-ease-standard` is byte-identical to Tailwind's default**, which the paragraph above says
  while arguing against the curve and which the token itself did not record. It now does, in its
  own `usage` string in `tokens/tokens.json`, so a reader of the token can tell the value is
  inherited rather than chosen.

Remove the movement, keep the answer.
