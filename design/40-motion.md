# Motion

Three durations, one curve, and a short list of what may move at all.

| token | value | for |
|---|---:|---|
| `--hw-duration-fast` | 120ms | feedback: hover, press, toggle |
| `--hw-duration-base` | 200ms | an entrance: a menu, a popover, a toast |
| `--hw-duration-slow` | 320ms | a move: a dialog, a sheet, a disclosure |
| `--hw-ease-out` | `cubic-bezier(0.22, 1, 0.36, 1)` | every entrance and every move |

All four are in `ramps/scales.css`, and no brand input moves them, so every product answers at 120ms on the same curve.
The curve is out-biased, fast start and long settle, which is what makes an interface feel like it answered rather than like it is playing an animation.
Base Web ships the same four numbers as its own `easeDecelerate`, arrived at independently.

## What may animate

`opacity`, `transform`, `color`, `background-color`, `border-color`, `outline-color` and `box-shadow`, and nothing else.
Never `height`, `width`, `top`, `left` or `margin`, which force layout on every frame; where a height must change, animate `grid-template-rows` from `0fr` to `1fr` instead.
The layer breaks this once: the determinate progress bar transitions its fill's `width`, where a `scale` transform from the left edge would hold the rule.

- **Hover is a fill, never a movement**, because a row that lifts reflows a long list under the pointer.
- **A press moves a button 1px and never scales it**, as `components/components.css` draws it, because a shrinking button moves its own label out from under the cursor.
- **Nothing animates on scroll.**

## What moves on its own

Three things in the house move without the reader moving them, each drawn in `components/components.css`, and nothing else does:

- **a busy button's spinner**, inside the button whose action is under way and nowhere else;
- **an indeterminate progress bar's sweep**, only while the total is unknown; a known total is a determinate bar with a sentence giving the numbers;
- **a level meter**, which follows real input and is still when none arrives.

A skeleton holds still: no shimmer and no pulse.
A spinner standing on its own is not a house surface: a wait is a progress bar and a sentence.
While a live signal, a level meter or a presence dot, is on screen nothing else in its view animates, because two moving things make neither a signal.
A live state that is not one of the three is still: quoth's open microphone is a still mark beside the word `Recording`.

**Two products break this today, and the rule stays.**
quoth pulses its skeletons with `animate-pulse` and shows spinners outside a button, ten and three of them as the house design review of 2026-10-02 counted.
pointback's presence dot pulses on a 1.4s infinite loop in its `src/browser/chrome.css`.
Each is the product's to bring onto the rule, in its own migration; the house does not widen the rule to fit them.

## A product's own moments

A product may add up to four **named moments** in its own namespace, each a `--<product>-` token, and each held to four rules:

- **It takes a house duration**, and takes a curve of its own only when it moves a distance large enough to show one.
- **It runs once per trigger and never loops.**
- **It animates a control, a line of text or a panel**, never art.
- **It is removed under `prefers-reduced-motion`**, like every other movement.

quoth's Field identity names one: the key sinking 2px on press over 120ms, which is `--hw-duration-fast`.
A product's design record lists its moments, and a movement not on the list takes the house tokens.

A brand-wide curve is not an input because the difference does not show where most things move: three alternative ease-outs sampled at 60Hz differ from the house curve by at most 18.9% of the travel, 1.5px on the 8px a control moves and 30 to 60px on a 320px panel, which is why only a moment that moves a large distance may take its own.

## Reduced motion

Under `prefers-reduced-motion: reduce`, movement goes and feedback stays.
`ramps/scales.css` collapses every duration to 100ms, cuts every animation to one 1ms iteration, and limits transitions to opacity and colour, so a state still changes visibly and nothing travels.
The component layer then stills its three movers: the busy button's spinner becomes a still ring, the indeterminate bar a still full-width bar at 35% opacity, and a dialog or sheet appears in place; the level meter still follows its input, because that movement is the data.
`tests/exports.py` holds the 100ms collapse in every export, and only under the preference.

`transition: none !important` is the error this rule is written against: it removes colour and opacity feedback with the movement, and a control that changes state with no transition at all reads as broken rather than accommodating.

## Sources

| source | taken | left |
|---|---|---|
| [Base Web](https://www.npmjs.com/package/baseui), read from `baseui` 18.2.0 | `easeDecelerate`, byte for byte the house curve | its other curves |
| [WCAG 2.2, animation from interactions](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions.html) | motion an interaction triggers can be turned off | nothing |

The duration and curve measurements across fourteen reference products are recorded in [the evidence file as it stood on 2026-10-02](https://github.com/Abhijeet34/halderworks-design/blob/a95ed0fed0c544fc12483031a2066f3eecc6b535/design/90-evidence.md).
