# Density

Two settings, one attribute, and a short list of what each one is allowed to change.

```html
<div data-density="compact"> ... </div>
```

`data-density="compact"` on any ancestor rebinds four tokens.
There is no third setting, and a product that wants one has a screen problem rather than a density problem.

## What changes

| token | comfortable | compact | what it is |
|---|---:|---:|---|
| `--hw-control-h` | 32px | 24px | button, select, input outer height |
| `--hw-row-h` | 44px | 32px | table or list row |
| `--hw-cell-pad-y` | 12px | 6px | cell padding, vertical |
| `--hw-field-pad-y` | 7px | 3px | input padding, vertical |

## What does not change, and this is the important half

- **Type size.** 13px body-sm in both. Shrinking type and spacing together is how a compact mode becomes an unreadable mode.

  **A published system does the opposite, and recording its number turns this from an oversight
  into a choice.** Ant Design's `compactAlgorithm` changes exactly 30 of 443 tokens and every one
  is type or height - no colour, no radius, no border, no shadow, no icon size, which is the same
  list this file holds fixed. Where it differs is that it does shrink type, and it pays for it in
  leading: body goes 14px at 1.5714 to 12px at 1.6667, so the glyph drops 14% and the line box
  drops only 9%, 22.0px to 20.0px. That is a real third option - shrink the glyph and raise the
  ratio - and this system does not take it, because 13px is already the floor this book's type
  ramp sets for body text and a 12px body is the `label` step, which is not a reading size.
  [90-evidence.md](90-evidence.md) carries the measurement.
- **Horizontal padding.** `--hw-cell-pad-x` stays 16px and `--hw-field-pad-x` stays 12px, so a column of numbers and a column of fields both line up against the other density and a user switching modes does not lose their place.
- **Colour, every token of it.** Compact is not dimmer.
- **Alignment, sort state, truncation and the column set.** Density is a vertical rhythm, not a different table.
- **Icon size.** 16px in both. A 14px icon beside 13px text at 24px row height is three sizes fighting in 24 pixels.
- **Focus ring geometry.** 2px at 2px offset in both, because the ring must clear the control at the smaller height too, which is why `--hw-control-h-sm` is 24px and not 20px.

## Why these numbers

32px is the measured default control height: it is the most common button height in the 44-site capture, on 14 sites.
40px is second on 11 sites and is `--hw-control-h-lg` here, reserved for a single call to action on a marketing surface.
24px and 28px each appear on 8 sites and are the compact band; 24px is taken because it is on the 4px grid and 28px leaves no room for a 2px ring at a 2px offset inside a 32px row.

44px for a comfortable row is derived rather than sampled: 13px text at 1.5 line-height is 19.5px, plus `--hw-cell-pad-y` of 12px above and below, is 43.5px.
32px compact is the same text with 6px above and below.

**44px is also the accessible pointer-target floor**, which is why the comfortable row and not the compact one is the default.
On a coarse pointer that floor applies to controls too, and `--hw-control-h` rebinds to it; [36-form-factors.md](36-form-factors.md) owns the rule and `tokens/tokens.css` carries the media query.
A compact row of 32px is below that floor, so a compact table's row actions carry their own 32px-wide hit area rather than relying on the row.

## When to use compact

Compact is for a screen whose job is comparison across many rows: a run list, a ledger, a log, a diff.
It is not for making a page fit.

Three rules:

- **A product picks one density per surface and does not mix them.**
  A compact table inside a comfortable page is fine; a compact table beside a comfortable table is not.
- **Density is the user's choice where the screen is theirs.**
  A log viewer offers the toggle and remembers it. A settings page does not offer it.
- **Never nest a density.**
  `data-density` inside `data-density` resolves, but the second one is a component overriding a user preference.

## Density and the grid are independent

Compact changes row rhythm.
It never changes the column count, the page margin, the container width or the measure, all of which belong to [35-layout.md](35-layout.md).
A compact mode that also narrows the page is two changes wearing one name.
