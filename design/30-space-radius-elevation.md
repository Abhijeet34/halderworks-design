# Space, radius, elevation

## Space

Base unit 4px. Ten steps: 2, 4, 8, 12, 16, 24, 32, 48, 64, 96.

2px is the one exception **in this scale** and its job is the badge's vertical inset, where 4px makes a `micro` badge stand taller than the label beside it.
It used to claim the gap between an icon and its own label as well; that gap is `--hw-icon-gap` at 6px, [55-iconography.md](55-iconography.md) owns it, and the two tokens carried contradictory reasons for three rounds until [32-rhythm.md](32-rhythm.md) counted them.
Everything else in this scale is a multiple of 4.

[32-rhythm.md](32-rhythm.md) is where the unit's scope is stated, where all seven off-unit values across the system are listed with their reasons, and where the relationship between this scale and the type ramp is finally written down.

The reason for a scale at all is measurable. A recent audit of quoth's source found **34 distinct spacing values in use, 20 of the 31 integers off the 4px grid** - effectively every integer from 1 to 20 serving as a gap somewhere.
A 13px gap and a 14px gap are not perceptually different, so 34 values do the work of about eight and the eye gets no rhythm to lock onto.
That is what people mean when they say a UI feels dense and undifferentiated, and it is not about colour at all.

Pick from the scale or report the gap. Never split the difference.

## Radius

Three sizes and a pill, each bound to a role, because one radius everywhere removes the only non-colour cue for what contains what.

| token | value | role |
|---|---:|---|
| `hw-radius-sm` | 4px | things inside other things: badges, checkboxes, swatches, the status dot |
| `hw-radius-md` | 6px | interactive controls: buttons, inputs, selects, menu items, tabs |
| `hw-radius-lg` | 10px | containers: cards, panels, dialogs, popovers, toasts |
| `hw-radius-full` | 9999px | avatars and count pills only, where the round shape itself carries the meaning |

Two rules keep it coherent:

1. **A child's radius is never larger than its parent's.** A 10px badge inside a 6px input looks broken because it is.
2. **Nested radius = outer radius minus the padding between them.** A 10px card with 8px of padding wants a 2px inner radius, not another 10px one. Where that lands below 4px, use a square corner.

The reference set backs the small end: the dominant radius is 3px at Radix (401 uses), 4px at Vercel and Stripe, 6px at 21st.dev's component views, 8px at Railway and Arc.
Pills appear as a second radius for buttons and count chips (Linear 9999px, 51 uses), never as the only one.

## Elevation

Border first. The measurement here is blunt: across the 14 reference products, **73 of 75 sampled heading, body and button elements carry `box-shadow: none`, and 74 of the 75 paint no visible shadow at all**. The two exceptions are both on Arc.

| level | what it is | where |
|---|---|---|
| **flat** | no border, no shadow, sits on the ground | a section of a page, a form group |
| **bordered** | `1px solid var(--hw-border)` on `--hw-surface` | a card, a table, a panel. The default for anything that contains something |
| **floating** | bordered, on `--hw-surface-raised`, plus one shadow | only something that floats over content and can be dismissed: dialog, popover, menu, toast |

There are exactly two shadow tokens and **inside a window both are light-theme only**.

The exception is a panel floating over content this system does not own, such as quoth's menu-bar panel, which keeps its shadow in **both** themes because there is no surface of ours underneath it whose lightness could carry the step.
[36-form-factors.md](36-form-factors.md) owns that case and shows the render: with the shadow removed, a dark panel over a near-black desktop loses its edge entirely.
`tokens/tokens.css` has always carried dark values for both shadow tokens; only the prose forbade them.

In dark theme a shadow is invisible against a dark ground, so dark elevation is carried by surface lightness and border instead: `--hw-surface` at 0.196, `--hw-surface-raised` at 0.232.
In light theme the surfaces are the same white, and the shadow is what separates them.
That asymmetry is the design, not an oversight.

Borders differ between themes too, and this is worth copying rather than re-deriving. In dark theme the references use a translucent white rather than an opaque grey: Linear `rgba(255,255,255,0.08)` at 61 uses, Resend `rgba(214,235,253,0.19)` at 64 uses.
An alpha border composites over whatever surface it lands on, so one token stays coherent across every elevation. In light theme they use an opaque step off the ground: rauno.me `rgb(232,232,232)` at 81 uses, Vercel `rgb(235,235,235)`.
This system's `--hw-border` is opaque in both, which is the simpler choice; if a product needs a border that works across three stacked surfaces in dark theme, an alpha override is the sanctioned exception.

If a thing cannot be dismissed, it does not float.
