# Space, size and layout

Every distance and size is a token in `ramps/scales.css`, and the comment beside each one is the description every export carries.
This file says how they relate and which file holds each relation.

## The unit

**4px**, and it governs space and size: the spacing scale, control and row heights, cell and field padding, icon sizes, breakpoints, gutters, containers, the rail and the panel.
It does not govern radius, which is a curve, line weight, which is a hairline or a ring, the line box, which is a type size times a leading, or measure, which is in `ch`.

Every governed value, read at the default text size M, is on the unit or is one of five declared exceptions, each with the reason it cannot be on it:

| token | value at M | why it is off the unit |
|---|---:|---|
| `--hw-field-pad-y` | 7px | what is left of the 32px control after the line box and the border |
| `--hw-field-pad-y-compact` | 3px | the same consequence at the compact control height |
| `--hw-cell-pad-y-compact` | 6px | 19.5px of line box plus 6px above and below is the 32px compact row |
| `--hw-icon-gap` | 6px | 4px reads as an icon and its label as one object, 8px as two |
| `--hw-icon-sm` | 14px | beside 12px label text: on the unit it is too small at 12 or overshoots at 16 |

`tests/exports.py` holds the rule in every export: it refuses a governed value off the unit that is not declared, and a declared exception that has moved back onto it, so the list cannot rot in either direction.
The governed families and the exceptions are named in that file rather than in a file a change could narrow.

**The unit governs the space between things; type governs the space inside them.**
No line box is on the unit, on purpose: a baseline grid would choose each leading to satisfy arithmetic rather than to be read.
A unit removes drift, 34 distinct spacing values doing the work of about eight, as an audit of quoth's source once counted; it does not supply rhythm, and a column of gaps reading 16, 16, 16, 16 is on the unit and has none.

## Space

Eight steps, in rem so a larger text size grows the box with its text: `--hw-space-4`, `-8`, `-12`, `-16`, `-24`, `-32`, `-48` and `-64`, each named for its px at M.
Pick a step or report the gap; never split the difference.

## Controls and rows

| token | px at M | what it is |
|---|---:|---|
| `--hw-control-h-sm` | 24 | a compact control; `max(24px, 1.6rem)`, never under WCAG 2.2's 2.5.8 target |
| `--hw-control-h` | 32 | a button, select or input |
| `--hw-control-h-lg` | 40 | one call to action on a marketing surface |
| `--hw-row-h` | 44 | a table or list row |
| `--hw-row-h-compact` | 32 | a compact row |
| `--hw-cell-pad-x`, `--hw-cell-pad-y` | 16, 12 | cell padding |
| `--hw-field-pad-x`, `--hw-field-pad-y` | 12, 7 | input padding |

A control's height is the token and its vertical padding is whatever the height leaves, so a field and a button in one row share an outer height.
The 44px row is derived rather than sampled: 13px text at 1.5 is 19.5px, plus 12px above and below is 43.5px, rounded onto the unit.

## Density

`data-density="compact"` on any ancestor rebinds four tokens, in `ramps/scales.css`: `--hw-control-h` to 24px, `--hw-row-h` to 32px, `--hw-cell-pad-y` to 6px and `--hw-field-pad-y` to 3px.
There is no third setting.

What does not change is the important half: type size, horizontal padding, every colour, icon size, the focus ring's geometry, and the column count, page margin, container and measure.
A compact mode that also shrinks type or narrows the page is two changes wearing one name.

Compact is for a screen whose job is comparison across many rows, a run list, a ledger, a log, and not for making a page fit.
A product picks one density per surface, never nests one inside another, and offers the choice where the screen is the reader's.
Under a coarse pointer a control never measures under 44px, compact or not ([60-accessibility.md](60-accessibility.md#targets)).

## Radius

Three sizes, each bound to a role, because one radius everywhere removes the only non-colour cue for what contains what:

| token | role |
|---|---|
| `--hw-radius-sm` | things inside other things: a badge, a checkbox, a keycap, a menu item, a segment in its track |
| `--hw-radius-md` | a control standing on its own: a button, an input, a select, a rail item |
| `--hw-radius-lg` | containers: panels, dialogs, popovers, toasts, a stage |
| `--hw-radius-full` | avatars, count pills and the tracks of a switch, a slider and a progress bar, where the shape carries the meaning |

A brand takes one of four registers from `ramps/roster.json` rather than a free number, and `tools/contrast.py` refuses any other triple in an emitted file ([12-brand.md](12-brand.md#shape-and-stroke)).
A child's radius is never larger than its parent's, and a nested radius is the outer one minus the padding between them.
Below a control's size the layer rounds by shape rather than by token: a dot, a radio, the switch knob, the spinner, the slider thumb and the comment pin are `50%`, and the marks round at `0.12em`.
The descriptions `tools/ramps.py` writes beside the three register tokens still put menu items and tabs on `md` and the status dot on `sm`; the table above is what `components/components.css` draws.

## Elevation

Border first.

| level | how it separates | where |
|---|---|---|
| flat | nothing | a page section, a form group |
| filled | a fill one step off its parent | the rail, a code block, a read-only field |
| bordered | a 1px `--hw-line` or `--hw-line-strong` | anything that contains something: a table, a panel |
| floating | `--hw-surface-raised` and one shadow | only something that floats over content and can be dismissed: a menu, a popover, a toast, a dialog, a sheet |

`--hw-shadow-overlay` is for menus, popovers and toasts, and `--hw-shadow-dialog` for dialogs and sheets.
In dark a shadow only edges what floats, and elevation is carried by surface lightness: `--hw-surface` is gray step 2 and `--hw-surface-raised` step 3 over the step-1 ground.
**If a thing cannot be dismissed, it does not float.**

A panel floating over the user's desktop, quoth's menu-bar panel, is the one surface whose ground the house does not own, so nothing it communicates may depend on contrast with anything outside it.
It takes an opaque `--hw-surface-raised`, a 1px `--hw-line-strong` edge, which clears 3:1 against its own fill, and `--hw-shadow-dialog`, in both themes; never translucency, `backdrop-filter` or a scrim.
`--hw-panel-w` and `--hw-panel-max-h` size it.

## Surfaces

**No grain, no gradient, no glass and no `backdrop-filter` behind text.**
The light highlight is drawn with a hard-stop `linear-gradient`, which paints one flat block in `--hw-mark` and no wash.
A contrast ratio is computed against one background colour, and a ground whose pixels are unknown makes every certified number an approximation.
A ground may carry a pattern only where every pixel of it is a role and every ink on it clears its bar against the worst of those pixels; no tool checks a pattern, so review is that rule's only enforcement.

One border width: `--hw-border-w` is 1px, and the 2px lines that are states are the focus ring, `--hw-focus-w`, and the selected tab's rule, `--hw-tab-active-w`.
The layer draws three more 2px lines that are not states, each listed with its reason in `tests/components.py`: the keycap's bottom edge, the slider thumb's ring, and the ground-coloured ring that parts stacked avatars and a comment pin from what they overlap; the description of `--hw-border-w` in `ramps/scales.css`, "there is no 2px border", predates them.
`--hw-line` divides and is never a control's boundary; `--hw-line-strong` is the boundary, certified at 3:1 on every ground ([10-color.md](10-color.md#which-ink-may-sit-on-which-ground)).

## Icons

`--hw-icon-sm` 14px, `--hw-icon` 16px and `--hw-icon-lg` 20px size a product's own icons in px, with `--hw-icon-gap` 6px to the icon's label.
The component layer sizes its icons in em instead, 1em by default and 1.15em in a button or a rail item, so they grow with the text size.

Lucide is drawn on a 24-unit grid at `stroke-width="2"`, which works out to 1.33px painted at 16px.
A brand's `--hw-icon-stroke`, 1.5px, 1.75px or 2px, is the weight to paint at every size, and the attribute that paints it is the weight times 24 over the rendered size, set per size as a plain number:

| painted stroke | at 14px | at 16px | at 20px |
|---|---:|---:|---:|
| 1.5px | 2.571 | 2.25 | 1.8 |
| 1.75px | 3 | 2.625 | 2.1 |
| 2px | 3.429 | 3 | 2.4 |

A number per size rather than `calc()`, because dividing a length by a length needs CSS typed arithmetic, which not every engine a product ships in supports.
The component layer applies no stroke rule yet, so its icons paint Lucide's own 2 units at whatever size their text sets, and a brand's stroke reaches only a product's own icons: a stated gap.

## Layout

| breakpoint | value | what changes at it |
|---|---:|---|
| `--hw-bp-sm` | 600px | below it a screen is one column and the rail is a sheet |
| `--hw-bp-md` | 768px | four columns become six; the page margin goes from 16px to 24px |
| `--hw-bp-lg` | 1024px | six columns become twelve; the rail becomes permanent; the margin goes to 32px |
| `--hw-bp-xl` | 1280px | the content column stops growing and the margins take the rest |
| `--hw-bp-2xl` | 1600px | only a wide table or a three-pane shell uses the extra width; prose never does |

Breakpoints are min-width only, so no width falls between two rules.
A component never declares a breakpoint: it takes its layout from the grid it is placed in or from a container query, as the key-value list does.
A screen that seems to need a sixth breakpoint has a layout problem that a sixth breakpoint moves rather than fixes.

The grid is twelve columns above `--hw-bp-lg`, six from `--hw-bp-md` and four below, with `--hw-column-gap` at 24px at every width, on `minmax(0, 1fr)` tracks so a long hash cannot widen its column past the viewport.
The containers are `--hw-container-app` 1440px for the app shell, `--hw-container-page` 1200px for a marketing or documentation page and `--hw-container-prose` 720px for a reading column; the rail is `--hw-rail` 248px, or `--hw-rail-collapsed` 56px.

Every screen has one primary focus, nameable in one sentence before it is built; the heading, the primary action and the largest rendered element all belong to it, and none of them is disabled.

Seven layers stack in `ramps/scales.css`: `--hw-z-base` 0, `--hw-z-sticky` 100, `--hw-z-rail` 200, `--hw-z-dropdown` 300, `--hw-z-scrim` 400, `--hw-z-dialog` 500 and `--hw-z-toast` 600, toasts on top because they report what a dialog did.
A number not on that list is a layer nobody decided on.

## Direction

Every product is built left to right, and the content inside one is not always: a transcript can arrive in Arabic, and a file name or a pasted value can be in any script.

- **`dir="auto"` on every element that shows text the product did not write**, and on every text input, so the browser takes the direction from the first strong character; a transcript sets it per segment.
- **`<bdi>` around a person's text placed inside a product sentence**, as in `Deleted <bdi>{name}</bdi>`, so a right-to-left name cannot reorder the words around it.
- **`text-align: start`, never `left`**, on anything that holds such text.

The layout itself does not mirror: the rail stays on the left and numeric columns stay right-aligned.
The component layer still writes `text-align: left` on the hotkey field, the menu item and the table head, a stated gap against the third rule.

## Sources

The px values were first measured on a capture of 44 sites at 1440 by 900, and the counts beside each token in `ramps/scales.css` come from it; the capture and its method are recorded in [the evidence file as it stood on 2026-10-02](https://github.com/Abhijeet34/halderworks-design/blob/a95ed0fed0c544fc12483031a2066f3eecc6b535/design/90-evidence.md).
[WCAG 2.2's target size, minimum](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html) is the 24px the compact control never goes under.
