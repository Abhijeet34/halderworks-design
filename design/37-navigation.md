# Navigation

[35-layout.md](35-layout.md) gives the rail a width, a ground, a hairline, a collapsed width and a
z-index, and gives the items inside it nothing.
This file is the inside of the rail, the header and footer of a page that has no rail, the toolbar,
the in-page table of contents, and the skip link that makes all of them reachable.

Six surfaces, every one carried by at least one external component library and none of them
answered before. [90-evidence.md](90-evidence.md) has the cross-check that found them.

**No new token is introduced here.** Every value below is an existing token or a composition of two.

## Skip link

**The first focusable element on any shell with a permanent rail.**

Without one, a keyboard user tabs through every rail item before reaching the content, on every
page, forever. [35-layout.md](35-layout.md) puts a permanent rail in front of the content above
`--hw-bp-lg`, which is exactly the case a skip link exists for.

```css
.hw-skip {
  position: absolute; left: var(--hw-space-8); top: var(--hw-space-8);
  z-index: var(--hw-z-dropdown);
  background: var(--hw-surface-raised); color: var(--hw-text);
  border: var(--hw-border-w) solid var(--hw-border-strong);
  border-radius: var(--hw-radius-md);
  padding: var(--hw-space-8) var(--hw-space-12);
  font-size: var(--hw-text-body-sm);
  clip-path: inset(50%);           /* hidden, and still in the tab sequence */
}
.hw-skip:focus-visible { clip-path: none; }
```

- **`clip-path`, never `display: none` or `visibility: hidden`.** Those two remove the element from
  the tab sequence, which is the one thing it must be in. This is the failure that makes most skip
  links non-functional.
- `--hw-z-dropdown` at 300 clears the sticky toolbar at 100 and the rail at 200, which are the two
  things it can appear over.
- One skip link, to the main content landmark. A page with four skip links has a navigation problem
  the links are hiding.
- It is visible the moment it takes focus and not before. A permanently visible skip link is a
  control in the layout that 99% of readers will never use.

**What the consumer provides:** the `id` on the main landmark and the `href` to it.

## The navigation item

The rail's items, and the same anatomy for a header's nav on a page with no rail.

| part | token |
|---|---|
| item height | `--hw-control-h` - 32px comfortable, 24px compact, and 44px under `(pointer: coarse)` by the rebind in `tokens/tokens.css` |
| horizontal padding | `--hw-space-8`, which is the rail's own inset |
| label | `body-sm` (13px) in `--hw-text-secondary` at rest |
| icon | `--hw-icon` 16px at `--hw-icon-gap` 6px before the label, `currentColor` |
| radius | `--hw-radius-sm` |
| gap between items | none. Items abut; the rail is a list, not a stack of cards |
| group label | `micro` (11px, 0.06em, 600, uppercase) in `--hw-text-muted`, `--hw-space-16` above the group and `--hw-space-4` below it |
| nested item indent | `--hw-space-16`, once |

### Navigation item: states

| state | what changes | certified in |
|---|---|---|
| rest | `--hw-text-secondary` on `--hw-surface-sunken` | 6.00 light, 7.27 dark |
| hover | fill becomes `--hw-surface-hover`, label goes to `--hw-text` | [15-color-combinations.md](15-color-combinations.md) |
| current | fill becomes `--hw-accent-quiet`, label becomes `--hw-text`, and `aria-current="page"` | the selected-row pairing, 13.37 to 13.45 |
| focus-visible | the 2px `--hw-accent-ring` inside the item, not around it | [60-states.md](60-states.md) |
| disabled | not a state a navigation item has. A destination a user may not reach is not shown | - |

**The current item takes the fill, never the accent as ink.** An accent-coloured label plus an
accent fill spends the accent twice to say one thing, and the accent has four jobs
([15-color-combinations.md](15-color-combinations.md)) of which this is one.

### Navigation item: rules

- **One level of nesting, and no more.** A rail that needs three levels is an information
  architecture problem, and a third level moves it rather than fixing it. This is the same rule
  [35-layout.md](35-layout.md) applies to breakpoints.
- **A group with one item is not a group.** Put the item at the top level.
- **A count belongs beside the label as a `neutral` badge**, not inside it as `Runs (4)`, which is
  the rule [65-components.md](65-components.md) already applies to tabs.
- **The collapsed rail shows icons only, with the label in a tooltip**, which is the one place
  besides a toolbar where [55-iconography.md](55-iconography.md) permits an icon-only control.
  At `--hw-rail-collapsed` 56px a 16px icon has 20px each side, so the target is the item height
  and not the glyph.
- **Never a badge and a count and an icon on one item.** Two marks on one row means the row is
  carrying two subjects.

### Navigation item: what the consumer provides

The list semantics, `aria-current="page"` on exactly one item, `aria-expanded` on a group that
opens, and the roving `tabindex` described in [72-keyboard.md](72-keyboard.md).

## Toolbar

[35-layout.md](35-layout.md) pins it to the top of the content pane at `--hw-z-sticky` on
`--hw-surface` with its bottom border. This is what goes inside it.

| part | token | derivation |
|---|---|---|
| height | `--hw-space-48`, 48px | a `--hw-control-h` 32px control with `--hw-space-8` above and below |
| horizontal inset | the page margin the pane carries, `--hw-gutter-lg` at 32px above `--hw-bp-lg` | it shares the pane's left edge so the toolbar and the content align |
| between items in a group | `--hw-space-8` | |
| between groups | `--hw-space-16`, or a separator | |
| separator | `1px` of `--hw-border`, full height minus `--hw-space-8` top and bottom, `--hw-space-8` clear each side | |
| overflow | a trailing icon-only button opening a menu | |

### Toolbar: rules

- **A toolbar is one tab stop.** The arrows move inside it; see [72-keyboard.md](72-keyboard.md).
  Nine buttons that are nine tab stops is a toolbar a keyboard user has to walk through.
- **It never wraps and it never scrolls horizontally.** Items that do not fit collapse into the
  overflow menu from the right, so the leftmost items - which are the ones a product put first -
  survive at every width.
- **At most one `primary` button**, and it is the last item. Everything else is `quiet` or
  icon-only. A toolbar of filled buttons has no primary action, it has nine.
- **A separator groups; it does not decorate.** Two separators with one item between them is two
  groups of one.
- **Never transparent over scrolling content.** It carries `--hw-surface` and its bottom border, or
  it is not sticky.

## Site header

The page that has no rail: marketing, documentation, a sign-in page, an error page.

| part | token | derivation |
|---|---|---|
| height | `--hw-space-64`, 64px | a `--hw-control-h` 32px row with `--hw-space-16` above and below |
| ground | `--hw-ground`, with a `--hw-border` bottom rule | |
| content width | inset to `--hw-container-page`, 1200px, inside the page margin | [35-layout.md](35-layout.md) |
| the mark | the product name at `title-3` (17px/600) in `--hw-text`, left | [00-brand-book.md](00-brand-book.md) - there is no logomark <!-- covered-by: Logomark and wordmark --> |
| nav items | the navigation item above, laid horizontally | |
| the one action | a `primary` button at `--hw-control-h`, right | |

### Site header: rules

- **Sticky or not, never both by scroll position.** A header that hides going down and reappears
  going up is a header that is somewhere else every time the reader looks for it.
- **The mark is a link to the root and is not a navigation item.** It sits outside the nav landmark.
- **At most one action in the header.** A header with `Sign in`, `Sign up` and `Book a demo` in it
  has told the reader that nobody decided.
- Below `--hw-bp-md` the nav collapses to a single disclosure button and the items become a sheet,
  which is the same mechanism the rail uses at `--hw-bp-lg`.

## Site footer

| part | token |
|---|---|
| ground | `--hw-surface-sunken`, full-bleed, with a `--hw-border` top rule |
| vertical padding | `--hw-space-48` |
| content | `--hw-container-page` at 1200px, on the grid |
| columns | at most four, each three of the twelve columns; one column below `--hw-bp-md` |
| column head | `micro` uppercase in `--hw-text-muted` |
| links | `body-sm` in `--hw-text-secondary`, `--hw-space-8` apart, going to `--hw-text` on hover |
| the last line | `body-sm` in `--hw-text-muted`, above `--hw-space-24` of clear |

### Site footer: rules

- **Four columns is the ceiling.** A footer with seven columns is a sitemap, and a sitemap is a
  page.
- **No newsletter field unless the product actually sends one**, and if it does, it is a real form
  and takes [66-forms.md](66-forms.md) and [67-validation.md](67-validation.md) whole. A decorative
  email input that goes nowhere is on the anti-pattern list by the same argument as an invented
  metric.
- **No social icon row that repeats the header.** And an icon-only social link still needs its
  accessible name.
- **The year in the last line is generated, never typed.** A footer reading 2019 says more about the
  product than the copyright notice does.
- The footer carries no accent. Links on it are `--hw-text-secondary`, because a page of accent-blue
  links at the bottom of every page is the accent spent on navigation
  ([15-color-combinations.md](15-color-combinations.md) gives it four jobs and this is not one).

## In-page table of contents

[35-layout.md](35-layout.md) allots it a third column above `--hw-bp-xl` and drops it below that
rather than shrinking it. This is its anatomy and its one hard behaviour.

| part | token |
|---|---|
| column width | `--hw-rail`, 248px, so it and the rail are one width in the system |
| position | sticky at `--hw-z-base`, `--hw-space-32` from the top of the viewport |
| entries | `body-sm` in `--hw-text-secondary`, `--hw-space-8` row rhythm |
| the active entry | `--hw-text`, with a 2px `--hw-accent` rule on its leading edge over the `--hw-border` rail |
| second-level indent | `--hw-space-16` |
| heading | `micro` uppercase in `--hw-text-muted`, `--hw-space-8` below |

### In-page table of contents: rules

- **Two levels, `h2` and `h3`, and no third.** A fourth-level heading that needs to be findable is a
  section that needed to be a page.
- **The active entry is the last heading whose top has passed the viewport top, not the first
  heading intersecting the viewport.** Those two rules differ exactly when a short section is fully
  on screen, and the second one flickers between two entries while the reader is not scrolling.
- **Scroll-spy uses `IntersectionObserver`, never a `scroll` handler.** A handler runs on every
  frame of every scroll on a page whose whole job is being read.
- **The accent rule is the only accent in the component**, which is the same rule
  [65-components.md](65-components.md) applies to tabs.
- It is generated from the headings in the document. A hand-maintained table of contents is a second
  copy of the document structure and one of the two is always wrong.

### In-page table of contents: what the consumer provides

The heading ids, the observer, and the `aria-label` naming it - because a page can carry both this
and a site navigation, and two unlabelled navigation landmarks are indistinguishable to a screen
reader.

A rail the keyboard cannot get past is a rail nobody past it ever reaches.
