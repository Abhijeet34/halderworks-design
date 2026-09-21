# Form factors

[35-layout.md](35-layout.md) owns the grid, the breakpoints and the two page shapes.
This file says what changes, in tokens and rules, for each shape a Halderworks product is actually built in, and it names the shapes that are deliberately out of scope so that an absence and a decision stop looking identical.

A keyword sweep over the first two passes of this system returned **zero** for `mobile`, `desktop` and `menu bar`.
quoth is a menu-bar application with a floating non-activating panel, and that shape appeared nowhere in the system it is supposed to be built from.

## This file is one axis of two

A form factor is **how much room there is**: the shell, the container, what stacks and at which
breakpoint. That is this file.

An input modality is **what is driving it**: the tab sequence, the key bindings, the hit target,
whether hover exists at all. That is [72-keyboard.md](72-keyboard.md), and until it existed this
book had no home for it - which is why a keyboard rule could only live inside a component card and
why there was no single page to check a screen against.

The two are not one axis. **A touch laptop is a large viewport with a coarse pointer**, and a
keyboard-only desktop user is a fine-pointer form factor with no pointer in use at all. Section 4
below is named for both and owns only the viewport half; the pointer half is one media query and
the keyboard half is a file.

One apparent gap was checked and dismissed.
`dark mode` also returns zero, and it is a keyword miss rather than a hole: theming is carried by `[data-theme="dark"]` and a `prefers-color-scheme` block in `tokens/tokens.css`, every colour pair is certified in both themes, and [10-color.md](10-color.md) and [15-color-combinations.md](15-color-combinations.md) print both tables.
The phrase is absent; the layer is not.

## 1. The desktop application shell

A permanent rail and a content pane, which is what treadling, foliot and gates are, and what quoth's own window is when it is opened from the panel.

Fully specified in [35-layout.md](35-layout.md), and nothing here changes it.
What that file does not say, and forms need:

- A form in the content pane takes `--hw-measure-ui`, not the pane width, per [66-forms.md](66-forms.md).
  The pane can be 1440px wide; the form is 56ch inside it, left-aligned with the page margin.
- The toolbar at `--hw-z-sticky` is where a form's actions go **only** when the form is the whole screen and is longer than the viewport.
  Otherwise the action row sits under the last field where the user's eye already is.
- The rail is never part of a form's tab order detour: focus order runs label, control, helper, next field, and the rail is before all of it.

## 2. The menu-bar utility and its floating panel

**This is quoth's primary surface and it was missing from the system entirely.**

A panel hanging off a menu-bar item is small, dense, dismissible, and sitting over content this system does not own and cannot measure.
Every rule below follows from that last clause.

### Geometry

| token | value | derivation |
|---|---:|---|
| `--hw-panel-w` | 352px | 40ch of `body-sm` Public Sans measures **318.4px** in a browser with the face loaded, plus `--hw-cell-pad-x` each side is 350.4px, rounded up to the 4px grid. 40ch is the measure [65-components.md](65-components.md) already uses for an empty state, and a panel is read in glances like one |
| `--hw-panel-max-h` | 464px | a 32px header, 12 rows at `--hw-row-h-compact`, and a 48px footer. Past twelve rows the reader is scanning rather than glancing, and scanning belongs in the app window |

The height is always clamped by the screen as well: `max-height: min(var(--hw-panel-max-h), calc(100vh - var(--hw-space-48)))`.
The panel scrolls internally past that; the header and the footer do not scroll.

### It is compact by default, and that is the one exception

[45-density.md](45-density.md) says density is the user's choice where the screen is theirs.
A menu-bar panel is not a screen the user lays out, so it carries `data-density="compact"` on its list by construction and offers no toggle.
Its header and footer stay at `--hw-control-h`, which compact already moves, so the whole panel moves together.

### Elevation, which is where this shape breaks an existing rule

[30-space-radius-elevation.md](30-space-radius-elevation.md) and [50-surface-texture.md](50-surface-texture.md) both state that the two shadow tokens are light-theme only, because a shadow on a dark ground is invisible and dark elevation is carried by surface lightness instead.

**That rule is correct inside a window and wrong for this panel**, because the ground under the panel is the user's desktop, not one of our surfaces.
A dark-theme panel over a near-black wallpaper has no lightness step to be carried by.

Rendered to check rather than argued: with the border and shadow removed, a dark panel over a `#0d1011` desktop and a light panel over a `#f4f6f7` desktop both lose their edge completely and read as text floating on the wallpaper.
With both present, each is bounded in both directions.

So the panel's elevation is:

- **A fully opaque fill**, `--hw-surface-raised`. Never translucent, never `backdrop-filter`, which [50-surface-texture.md](50-surface-texture.md) already bans for the same reason stated from the other side: a surface that takes its luminance from what is behind it has no certifiable contrast.
- **A 1px `--hw-border-strong` edge**, which is solved to 3:1 against the panel's own fill and is therefore findable from the inside whatever is outside.
- **`--hw-shadow-dialog`, in both themes.**

A correction that makes this possible without inventing anything: `tokens/tokens.css` and `tokens/tokens.json` **already ship dark values for both shadow tokens**, while all three prose files say the tokens are light-theme only.
The values exist and are usable; only the prose forbade them.
[50-surface-texture.md](50-surface-texture.md) now carries the exception.

### Contrast, when the ground is unknown

The panel's own interior is a normal surface and every pair on it is already certified, because `--hw-surface-raised` is in the tables in [15-color-combinations.md](15-color-combinations.md) for both themes.

What cannot be certified is the panel against the desktop, and no token can fix that.
The rule is therefore structural rather than numerical: **nothing the panel needs to communicate may depend on contrast with anything outside the panel.**
No transparency, no hairline that only reads on a mid-grey wallpaper, no text or control that overhangs the edge, and no shadow-only separation.

### Non-activating, which changes the interaction rules

The panel opens without making its application frontmost, so it must not behave like a dialog.

- **No focus trap and no autofocus.**
  A dialog traps focus and returns it on close, per [65-components.md](65-components.md).
  This panel takes focus only when the user gives it, because taking it steals the caret from whatever they were typing in.
- **Every action is reachable by pointer alone**, since the keyboard may never arrive.
- **Every hover affordance still needs its non-hover path** once the panel is activated, which is the rule already in [60-states.md](60-states.md).
- Escape dismisses. Clicking outside dismisses. Dismissing is always the safe outcome, as with a dialog.
- **No scrim, ever.** A scrim claims the rest of the interface is unavailable, and this panel makes no such claim about the user's other applications.
- The panel is anchored to its menu-bar item and does not move, so it is not a popover that can be repositioned to fit.

### What goes in it

One subject, one live state, one primary action.
A panel with two subjects is a window.

The live state carries the accent, which is the third of the accent's four jobs: `--hw-accent` text with a 6px `currentColor` dot, on the panel's own surface.
The primary action is `--hw-ink` in the footer on `--hw-surface-sunken`, full width of the panel's inner column.

## 3. The marketing or documentation page

Fully specified in [35-layout.md](35-layout.md): 1200px container, 720px prose, sections alternating ground rather than alignment, vertical rhythm varying by what the section carries.

The only addition forms make to it: a form on a marketing page is **one column at `--hw-measure-ui`, left-aligned inside the 1200px container**, exactly as in the app.
A centred two-column signup block is on the anti-pattern list twice over, for the centring and for the pair of fields that are not one value.

### What a marketing page is made of

[75-spec-sheet.md](75-spec-sheet.md#3-formats) names five composition formats and every one of
them is a **typographic device**. None is a page section, so an agent asked to build a marketing
page from this system had five devices and no idea what the page is made of.

This is a **checklist, not fourteen components**, and that distinction is the whole point: these
are sections a reader recognises, each built from the grid, the type ramp and the components that
already exist. Turning them into inventory rows would be the bloat this book is explicitly built
against, and [05-coverage.md](05-coverage.md) carries them as one composition row saying so.

```text
Hero            Value proposition   Features      How it works
Testimonial     Brands              Stats         Pricing
Resources       FAQ                 Call to action
Footer          About us            Case study
```

Fourteen names, taken from one published gallery's own closed section taxonomy and recorded in
[90-evidence.md](90-evidence.md) with that limit stated: **it is one vendor's taxonomy, not a
census.** Two of the fourteen already have entries here - Pricing as a page, Footer in
[37-navigation.md](37-navigation.md) - and `Sign up` from the same gallery's page-type list is
specified in [68-page-patterns.md](68-page-patterns.md).

Three rules for using it:

- **A page does not need all fourteen and no page should have all fourteen.** The list exists so
  that a missing section is a decision rather than an oversight.
- **Testimonial, Brands, Stats and Case study each require something real.**
  [80-anti-patterns.md](80-anti-patterns.md) refuses invented quotes, invented logos and invented
  metrics without exception, and those four sections are the shapes that most invite all three. A
  section with nothing real to put in it is deleted, not filled with placeholder.
- **Sections alternate their ground, never their alignment**, which is already
  [35-layout.md](35-layout.md)'s rule and is what stops fourteen named sections becoming fourteen
  different layouts.

## 4. Small viewports, and the coarse pointer that usually comes with one

Two things that arrive together often enough to be confused and are independent:
the **viewport**, which this section owns, and the **pointer**, which is one rebind below and
otherwise belongs to [72-keyboard.md](72-keyboard.md) along with the keyboard.

No Halderworks product ships a phone application today.
This section exists anyway, as a rule rather than as a plan, so that the first product that needs one does not invent the numbers.

### The pointer floor

**44px, which is `--hw-row-h`.**

The number is already in this system: [45-density.md](45-density.md) states that 44px is the accessible pointer-target floor and that it is why the comfortable row and not the compact one is the default.
What was missing is the consequence for controls.

On a coarse pointer the control **is** the target, so the height rebinds rather than being padded around:

```css
@media (pointer: coarse) {
  :root { --hw-control-h: var(--hw-row-h); }   /* 32px becomes 44px */
}
```

This composes with density rather than fighting it: a compact list on a touch screen keeps its 32px rows for reading, and its controls are still 44px, because a row is scanned and a control is hit.

Where a control genuinely cannot grow, such as the remove button on a chosen file, it keeps its 16px icon and takes a 44px padded hit area around it.
A 16px icon with a 16px hit area is the most common touch defect and it is invisible on a desktop.

### What stacks, and at which breakpoint

| at | what changes |
|---|---|
| below `--hw-bp-lg` | the rail leaves the layout and returns as a dismissible sheet at `--hw-z-rail`, which is the one time it earns a shadow. Already in [35-layout.md](35-layout.md) |
| below `--hw-bp-md` | the form goes to one column full width inside `--hw-gutter-sm`. Any paired fields separate |
| below `--hw-bp-md` | the action row stacks vertically, primary first, each button full width at `--hw-row-h` |
| below `--hw-bp-md` | a data table becomes list rows, because a table that scrolls horizontally on a phone is a table nobody compares anything in. [70-data-display.md](70-data-display.md) owns which is which |
| below `--hw-bp-sm` | nothing structural. 16px is a floor, not a preference: below it a thumb resting on the edge overlaps the first character of every line |

Hover does not exist on touch, and the rule that every hover-reachable state is also focus-reachable is already in [60-states.md](60-states.md).
On a touch build it stops being an accessibility rule and becomes the only way those states are reachable at all.

## Deliberately out of scope

Each of these is a decision with a reason, not an omission.
Any of them can be added, and each names what it would cost.

| factor | why not | what it would take |
|---|---|---|
| **Native iOS or Android** | no product ships one, and the type ramp, spacing scale and elevation rules here are CSS in px. A native ramp is `sp`/`pt` with platform line-height rules | a parallel token emission, not a new system. The values and the reasoning carry; the units and the elevation model do not |
| **HTML email**, such as a run digest | email clients do not support CSS custom properties, `oklch()`, or in many cases a `<style>` block at all, so every token here would have to be flattened to a literal hex at build time, which is the one thing this system tells you never to write by hand | a flattened export from the token build: one hex per token per theme, plus a table-based layout set. Worth doing the first time a product emails anything, and **this system has no such export today** <!-- covered-by: Native mobile, email, print, terminal, and the rest --> |
| **Print and PDF export** | a printed record has no themes, no hover and no focus, and its constraint is ink on white at a fixed page size, which none of the solved pairs address | a print stylesheet pinned to the light theme with shadows and fills removed, and a re-run of the matrix against paper white rather than `--hw-ground` |
| **Terminal and CLI output**, which gates and treadling both have | a terminal has no CSS and a 16-colour ANSI palette it does not own. Mapping `oklch(0.619 0.096 198)` onto "bright cyan" is a fiction, and the user's own theme overrides it anyway | a separate, small decision about which four ANSI slots carry the semantics, taking the naming and content rules from here and none of the colour |
| **Watch, TV, car, and any voice surface** | no product has one and none is planned | a new system |

A browser-extension popup is **not** on this list: it is the menu-bar panel with a different anchor, and section 2 covers it unchanged.
