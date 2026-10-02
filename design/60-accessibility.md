# Accessibility floors

The floors every screen stands on, each with the file that holds it.
A component's own states and keys are its sheet in [64-component-sheets.md](64-component-sheets.md); this file is what every sheet has in common.

## The floors

| floor | value | held by |
|---|---|---|
| text contrast | 4.5:1 for every text role on every ground, fill and tint it is permitted on; 13:1 for `--hw-text` | `tools/contrast.py`, on the float and the 8-bit value; `tools/painted.py`, on a browser's pixels |
| non-text contrast | 3:1 for a control boundary, the focus ring and a chart mark on every ground | `tools/contrast.py` |
| raised contrast | under `prefers-contrast: more`, 7:1 for text and 4.5:1 for a boundary, a ring or a mark | `ramps/roles.css`, `tools/contrast.py`, `tests/exports.py` |
| text size | five reader settings, a 13 to 22px root; nothing under 11px at any of them | `ramps/scales.css`, `tests/exports.py`, `tests/components.py` |
| target size | 24px always; 44px under a coarse pointer, compact or not, at every text size | `ramps/scales.css`, the coarse-pointer block in `components/components.css`, `tests/exports.py` |
| focus | a 2px ring in `--hw-focus`, outside the control at 2px wherever the box allows it, never removed | the shared `:focus-visible` rule in `components/components.css`; `tools/contrast.py` for the ring's colour |
| motion | movement removed, feedback kept, under `prefers-reduced-motion` | `ramps/scales.css`, `tests/exports.py` ([40-motion.md](40-motion.md#reduced-motion)) |
| forced colours | the checked and current states, the marks and the progress fills redrawn in system colours | the `forced-colors: active` block in `components/components.css` |
| pairs a component paints | every text-and-background pair the layer sets is one `tools/contrast.py` certifies, or one exception `tests/components.py` measures itself | `tests/components.py` |

[10-color.md](10-color.md#which-ink-may-sit-on-which-ground) is the list of permitted pairs, and [20-type.md](20-type.md#the-text-size-setting) says what WCAG 2.2's 1.4.4 and 1.4.10 ask of the text size and the layout and how far the house goes toward each.

## Colour is never alone

- **Every state carries a word**, and a glyph where there is room: a badge says `Passed`, not only green.
- **An error is an edge and a sentence**: the field's edge turns `--hw-danger` and a sentence under it says what is wrong and what is expected, tied to the field with `aria-describedby`, with `aria-invalid="true"` on the field.
- **Every chart series carries a direct label**, not only a legend swatch.
- **A link is underlined** in running text, so it never relies on its colour.
- **A required or optional field says so in a word.**

The states are told apart by their words even for a reader who cannot tell their colours apart, which is why `tools/contrast.py` reports what a dichromat sees of the chart series and refuses nothing on it.

## Focus

The ring is drawn on `:focus-visible`, so a pointer click paints none and a Tab key does.
It is `--hw-focus-w`, 2px, at `--hw-focus-offset`, 2px, outside the control, in `--hw-focus`, which `tools/contrast.py` certifies at 3:1 on every ground and holds 14 CIEDE2000 from a control's own edge and 17 from the error colour, so a focused field never reads as an invalid one.
Five places in `components/components.css` move it, each because the default ring would be clipped or lost: a field's ring insets 1px over its own edge and a menu item's 2px inside the menu, a slider's sits at `--hw-space-4` to clear its thumb, and on the ink toast and on a stage the ring takes the text colour of the ground it sits on.
`outline: none` with nothing in its place is never written.

## Targets

Every target is at least 24px, WCAG 2.2's 2.5.8: `--hw-control-h-sm` is `max(24px, 1.6rem)`.
Under `(pointer: coarse)` the control is the target, so `ramps/scales.css` holds `--hw-control-h` at 44px or more, and its block comes after the compact block so a compact ancestor cannot pull a touch control back to 24px.
The component layer lifts the sizes derived from the other heights the same way, small and large buttons, icon buttons, segments, menu items, tabs, rail items and a tag's remove button among them.
`tests/exports.py` cascades every export under a coarse pointer, compact and not, at every text size, and refuses a control under 44px, with the touch block as it shipped before this fix replayed as a negative control.

## States

Each sheet lists the states its component answers.
What they share:

- **Hover is a fill, never a movement**, and anything reachable by hover is reachable by focus too: a tooltip opens on `:hover` and on `:focus-visible` inside it.
- **Disabled is a solved colour, never an opacity**: `--hw-text-disabled` on `--hw-fill`, held to 3:1 on every ground, because WCAG exempts disabled text and nothing else would keep it from vanishing.
  A control disabled for a reason says the reason beside it; a disabled control never carries the largest weight on its screen.
- **Inside a composite, a disabled item stays reachable**: `aria-disabled="true"` rather than `disabled`, so a screen-reader user can find it and hear why.
  Outside one, a single disabled control takes `disabled`.
- **Read-only is not disabled**: full `--hw-text` on `--hw-bg-subtle` with a dashed edge, selectable and copyable, because a hash a reader must copy cannot sit at 3:1.
- **Busy holds the layout**: `aria-busy="true"` on what is loading, the control keeps its width, and the outcome, not the start, is announced in a live region.
- **Selection keeps its text colour**: it is drawn with a fill or an edge, `aria-selected` inside a widget and `aria-current="page"` in navigation, never by turning the text accent-coloured.

## Keys

**Tab and Shift+Tab move between components; everything else moves within one**, the convention the ARIA Authoring Practices Guide publishes.

- **Native elements first.**
  A button is a `button` and a link an `a`, so Tab, Enter and Space work with no script.
- **A composite widget is one tab stop**, and the arrow keys move inside it with a roving `tabindex`, or with `aria-activedescendant` where focus must stay in a text field.
  The layer gives the segmented control its arrow keys in `components/radiogroup.js`; every other composite's sheet says the roving is the product's.
- **Tabs select on arrow**: moving to a tab selects it and shows its panel, because tabs here switch between views of one subject and switching is cheap.
- **Escape closes what floats, and focus returns** to the control that opened it; a modal dialog or sheet holds focus while open.
- **A permanent rail puts a skip link first** in the tab order, hidden by clipping rather than `display: none`.
- **A panel over the desktop takes focus only when given it**: quoth's menu-bar panel opens without activating its application, so it traps nothing and autofocuses nothing, and every action in it works by pointer alone.

No tool here presses a key; the sheets' Keyboard lines are the contract, and a product's review is where it is checked.

## Sources

| source | taken | left |
|---|---|---|
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/) | 1.4.3, 1.4.4, 1.4.6, 1.4.11, 2.4.7, 2.5.8 as the floors above | nothing |
| [ARIA Authoring Practices Guide patterns](https://www.w3.org/WAI/ARIA/apg/patterns/) | Tab between components and arrows within; `aria-disabled` inside a composite | the optional bindings, each decided here |
