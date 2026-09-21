# Anti-patterns

This file exists because of a measurement rather than a preference.

A model produces what it has seen most, so the looks generated design clusters around are the field's own crowded places, and the first of them - a warm cream ground, a serif display and a terracotta accent - can be counted.
A corpus of 91 published product design systems, measured for this book, puts **20 of its 90 light grounds in a warm band** at hue 50-130 with a median of `oklch(0.977 0.0079 86.5)`, and its accent hues, rounded to 30 degrees, put **orange second at 16 of 87**, behind violet at 24.

An independent audit of quoth's shipped palette measured its light ground at `#F2EEE7`, which is `oklch(0.9503 0.0103 81.79)`, and its accent at `oklch(0.6 0.16 42)`, which is `#CC5824`.
The ground sits inside that warm band, 4.7 degrees of hue from its median; the accent sits in the orange bucket.

So this is not "our design is a bit generic".
Our design landed on a documented default and can be shown to have done so.

Each entry below is a **tell**, a reason models produce it, and the **house rule** that replaces it.
The tell is what you look for on the screen; the reason is why you will keep reaching for it; the rule is what to do instead.

Organised by surface, because that is how a screen is reviewed.

## Colour

| the tell | why models produce it | the house rule |
|---|---|---|
| **Warm cream ground, serif display, terracotta accent** | it is the highest-probability palette, and it looks warm and expensive in a thumbnail | neutral ground at chroma 0.003, accent at hue 198, and `hw-ink` rather than a chromatic colour for the primary action. A display serif is used here, but on a cool ground with a teal accent, which breaks the pattern at two of its three legs. Newsreader is a low-contrast reading serif, not the high-contrast display serif of that cluster |
| **Near-black with a lone acid-green or vermilion pop** | one saturated colour on a dark ground is the cheapest way to look designed | the dark ground exists, but colour is spent on four defined jobs in both themes, and `hw-accent` is not an acid colour: chroma 0.096, roughly half of what the gamut allows at that lightness |
| **Purple-to-blue gradient hero on white** | the default hero of every AI product page since 2023 | no gradients. There is no gradient token and there is no plan to add one. 14 of 44 measured sites paint a gradient on a large element; none of the ones this system took principles from paints one behind text <!-- covered-by: Texture, grain, gradient, glass --> |
| **A blue-violet accent between hue 245 and 296** | it is where the whole developer-tool field already is | hue 198, chosen by measuring the field and staying out of it. 17 of 29 accents sampled across the reference set fall in that corridor |
| **The whole page painted in the accent** | colour reads as "designed", so more colour reads as more designed | four jobs and no others: a link, a selected row, a live state, the focus ring. A screen with no state on it should have no hue on it |
| **A semantic colour used as a brand colour** | green is available and looks healthy | a green that also means "this is our brand" cannot also mean "this passed". Semantics are permanently separate from the accent |
| **A coloured dot with no word beside it** | it is compact and looks like a dashboard | every state carries a word. A row of dots fails for roughly 8% of men and for anyone reading a screenshot |
| **Text placed on a tinted fill that was never solved for it** | the fill looked light enough | [15-color-combinations.md](15-color-combinations.md) is the permission list. The first pass of this system made exactly this mistake and shipped `hw-accent` on `hw-accent-quiet` at 4.37:1 in dark theme |

## Type

| the tell | why models produce it | the house rule |
|---|---|---|
| **Inter, or Space Grotesk, as the safe face** | they are genuinely good, which is why 5 of 14 measured products use Inter | Public Sans for interface, with the size compensation its 5.3% smaller x-height requires written down in [20-type.md](20-type.md) |
| **A high-contrast display serif for headings over a sans body** | it is the "editorial" signal and costs no design work | Newsreader is a low-contrast reading serif, used at two steps only, on marketing and docs surfaces only |
| **Twenty-four type sizes** | each screen got the size it needed at the moment it was written | nine steps. quoth's own audit found 24 sizes and 34 spacing values in use |
| **Uppercase button labels with wide tracking** | it reads as "premium" | uppercase exists at one step, `micro`, for a column head or an eyebrow. An uppercase button label is shouting |
| **A number column without `tabular-nums`** | the default figures look fine in a single row | in Public Sans a `1` is a third narrower than a `0`: 407px against 606px per ten digits at 100px. Any column of figures jitters |
| **Centred headings over centred body text** | it looks composed in a screenshot | left-aligned by default. See Layout below |
| **A 95-character measure because the container was wide** | the container was the only constraint applied | 56ch in product, 68ch in long-form. A container width and a measure are different constraints and a page needs both |
| **A numeral set large beside a headline that never refers to it** | a big number makes any block look like a system | delete the numeral and read what is left. If the headline is still a whole sentence and nothing was lost, the numeral was a decorative marker set at 56px. [75-spec-sheet.md](75-spec-sheet.md) has the three tests |
| **An eyebrow that restates its own heading in small caps** | a second line above the first reads as editorial | an eyebrow names a category that has other members. "Fast and reliable" above "Fast and reliable" is the decorative-icon failure rendered in type |

## Layout

| the tell | why models produce it | the house rule |
|---|---|---|
| **Everything centred** | centring hides the fact that nothing was aligned to anything | left-aligned by default. Centre only a single-element empty state or a dialog's action row |
| **A uniform full-width section rhythm, every section the same height and padding** | one repeated block is one decision instead of six, and it looks orderly scrolling past | vertical padding is chosen per section from `--hw-space-48`, `--hw-space-64`, `--hw-space-96` by what the section carries. A page whose every section is the same height has had no editing done to it |
| **Three feature cards in a row, an icon, a bold noun, two lines of filler** | it is the single most probable block on any product page | a card groups things read together and acted on together. Three cards that exist because three fits the grid are one paragraph that was afraid to be a paragraph |
| **A hero that is a headline over a gradient with two buttons** | it is the default opening of the genre | the page opens with what the product does, set in type, on the ground. One primary action, never two side by side |
| **A testimonial row nobody wrote** | social proof is a recognised section and plausible quotes are easy | no invented quotes, no invented logos, no invented metrics, ever. An unattributable claim does not ship |
| **Breakpoints chosen per screen** | each screen broke at a different width during development | five breakpoints, min-width only, and a component declares none of them |
| **A masthead, date stamp or issue number on something that is not a series** | a masthead makes one page look like a publication | there must be a previous issue a reader can open, and the identifier must resolve to something outside the page. Issue 1 of 1 is a costume |
| **A card with one line of content in it** | it makes the line look considered | that is a list row that grew a border by accident |
| **Cards stretched to equal height over dead space** | the row looks tidier | let the content set the height. Cards in a row share edges, baselines and inner padding, not height |

## Component

| the tell | why models produce it | the house rule |
|---|---|---|
| **Pills and badges on everything** | a badge makes any noun look like a status | one badge per row or per card. Two badges means the row is carrying two subjects. A badge is non-interactive: if it can be clicked it is a button or a filter chip |
| **A glassmorphic panel: blur, translucency, a white hairline** | it is the most recognisable "modern UI" signal in the training distribution | no `backdrop-filter` anywhere. A translucent surface takes its luminance from whatever scrolls under it, so its contrast against its own text changes as the user scrolls. 8 of 44 measured sites use it; none on a surface carrying data |
| **The same drop shadow on every block** | shadow reads as depth and costs one line | border first. 73 of 75 sampled reference elements carry `box-shadow: none`. Two shadows exist, both light-theme only, and only for something that can be dismissed |
| **An accent bar or coloured rail on a rounded card** | it adds colour without committing to a hierarchy | no card carries an accent edge. Selected means the whole fill becomes `hw-accent-quiet`; error means the border becomes `hw-danger` |
| **One radius everywhere** | picking one is one decision instead of three | three radii bound to roles plus a pill for two cases, and a child's radius never exceeds its parent's |
| **A pill-shaped primary button** | it reads as friendly and modern | `hw-radius-md` at 6px. The pill radius is reserved for avatars and count chips, where the round shape itself carries meaning |
| **Broadsheet hairline rules with dense columns** | it signals "editorial" with no design work | one border token, separating a container from its ground. A rule between every row is a table that needed row spacing |
| **Zebra striping** | it looks like a data product | a 1px border per row is quieter and does the same job. Striping adds a surface that means nothing |
| **`outline: none` on focus** | the default ring is ugly and removing it is one line | never removed. `outline: none` is the most common focus declaration in the whole capture, 294 declarations across 26 of 41 sites, and the ring here is solved to 3:1 precisely so it can stay on |
| **Disabled as 45% opacity** | it is one property and it looks inactive | a solved `--hw-text-disabled` per theme. The same 45% composites to 1.73:1 in light and 7.40:1 in dark: one opacity cannot mean one thing in two themes |
| **A spinner for every wait** | it is the universal "loading" glyph | a skeleton at the shape of the real content. A spinner that spins forever says only that the product does not know either |

## Forms

The form layer is new in the third pass and these are the tells it exists to stop.
Several of them were in this system's own first two passes.

| the tell | why models produce it | the house rule |
|---|---|---|
| **A placeholder used as the label** | it looks clean in a screenshot and saves a line | a placeholder is an example of the format. It disappears exactly when the value needs checking, and it is not announced as a name. The label is always there, above the field |
| **A bare red asterisk for "required"** | it is the convention everyone has seen | a colour and a glyph carrying meaning with no word beside it, which this system already forbids for state. Mark the smaller set, with the word `Optional` or `Required` |
| **The submit button disabled until the form is valid** | it looks like it is preventing an error | it hides which field is wrong and gives the user nothing to press to find out. It stays enabled; pressing it validates and moves focus to the first failure |
| **Validating from the first keystroke** | more feedback reads as more helpful | telling someone their 4-character hash is too short while they type it is telling them what they already know. Validate on blur, and only then re-validate per keystroke so the error clears the moment it passes |
| **The error stacked under the hint** | appending is what a naive implementation does | the error replaces the hint. Two ids in `aria-describedby` read the rule and the failure as one run-on sentence |
| **A red fill on the field in error** | red means wrong and more red means more wrong | the border goes `hw-danger` and the fill does not change. A red fill puts the user's own text on a ground no pair here was solved for |
| **A green tick on every valid field** | it feels like reassurance | passing is the expected case. A column of ticks makes the one red field harder to find, not easier. Success belongs at form level, as the toast |
| **A custom select where the native one would do** | the native control looks unstyled | the native one brings platform keyboard handling, type-ahead, the touch wheel and scroll containment, and every custom listbox re-implements those four imperfectly. Go custom only when an option needs a second line |
| **A date picker with no typable field** | the calendar is the visible part | it costs a keyboard user four times the keystrokes. The typed field is the control and the calendar is the aid |
| **A drag-and-drop zone with no button in it** | the drop target is the designed element | drag and drop is unreachable by keyboard and awkward on touch, so it is never the only route |
| **Labels beside their fields, in two columns** | it fills a wide container and looks like a form | label above, always. It survives 390px without a second layout, never truncates, and keeps one left edge down the column |
| **A form stretched to the container width** | the container was the only constraint applied | a form is a reading column with controls in it, so it takes `--hw-measure-ui`, not a column count. A 1200px input is the 95-character measure wearing a different hat |
| **Switches and checkboxes mixed in one form** | both say yes or no | a switch takes effect on the spot and a checkbox waits for the button. Mixing them tells the user two different things about when their change lands |
| **A list of chosen files with no remove control** | the upload succeeded, so the list is output | then it is a report, not a control, and the only recovery is reloading the form |
| **Silently clamping an out-of-range number** | it keeps the value valid | turning 500 into 100 with no message tells the user their value was accepted. It is an error and it says so |

## Form factors

| the tell | why models produce it | the house rule |
|---|---|---|
| **A floating panel that relies on the background behind it** | in the mock, the background was ours | a menu-bar panel sits on the user's desktop, whose luminance is unknown and unmeasurable. Opaque fill, an edge solved against its own fill, and a shadow in **both** themes. Nothing it must communicate may depend on contrast with anything outside it |
| **A translucent or blurred floating panel** | it is the most recognisable "native macOS" signal | its contrast against its own text changes as the content behind it scrolls. Already banned for in-app surfaces, and the reason is stronger here |
| **A panel that traps focus like a dialog** | the dialog pattern is the one to hand | a menu-bar panel is non-activating. Trapping focus steals the caret from whatever the user was typing in another application |
| **A 16px icon with a 16px hit area** | it is correct on a desktop and invisible there | 44px is the pointer floor. Where the control cannot grow, the hit area is padded around it |
| **One layout stretched to every viewport** | the breakpoints were never exercised | the rail becomes a sheet, the action row stacks, paired fields separate, and a table becomes list rows |

## Motion

| the tell | why models produce it | the house rule |
|---|---|---|
| **Everything fades and slides in on scroll** | it makes a static page feel built | nothing animates on scroll. Motion answers an action; it does not decorate an arrival |
| **A 300ms ease-in-out on every transition** | it is the framework default and it is inoffensive | 150ms `ease-out` as the default. 0.15s is the most-used duration on 7 of 14 measured products, and the custom curves people actually wrote are out-biased |
| **A button that scales down when pressed** | it reads as tactile | no transform on press. A button that shrinks moves its own label out from under the cursor |
| **A row that lifts on hover** | depth on hover reads as responsive | hover is a fill. `transform` on hover is the most common cause of a list that stutters at a few hundred rows |
| **`transition: none !important` for reduced motion** | it satisfies the media query in one rule | remove the movement, keep the answer. A control whose state changes with no transition reads as broken rather than as accommodated |
| **A shimmer sweeping across a skeleton** | it signals "working" | skeletons do not shimmer. The only thing allowed to loop is a determinate progress indicator |

## Imagery and icons

| the tell | why models produce it | the house rule |
|---|---|---|
| **Decorative iconography that repeats the heading** | an icon beside a heading fills space and looks considered | a clipboard beside "Records" is noise with a colour. An icon earns its place by identifying a control or a state |
| **An illustration per empty state** | it makes an empty screen feel designed | no illustration set exists here and inventing one per empty state is how a product ends up with six unrelated drawings <!-- covered-by: Illustration --> |
| **Emoji as section markers** | they read as friendly and cost nothing to type | never. A section is marked by a heading, a state by a colour token with a word beside it |
| **Noise, grain or a paper texture under text** | it reads as crafted and expensive | a contrast ratio is computed against one background colour, and grain makes every certified number an approximation. 2 of 44 measured sites carry one, neither behind data. A ground may carry a pattern only where every pixel is a solved token and the ink is certified against the worst of them; a ground whose pixels are not enumerable carries no text at all. [75-spec-sheet.md](75-spec-sheet.md) has the three permitted styles |
| **A mixed icon set** | whichever icon was to hand | one set, Lucide, ISC-licensed, at a painted 1.5px stroke at every size |
| **Stock photography of people at laptops** | the slot exists in the template | no photography in product surfaces |

## Copy

| the tell | why models produce it | the house rule |
|---|---|---|
| **"Seamlessly integrate", "Supercharge your workflow", "Unlock the power of"** | it is the highest-probability register for a product page | say what it does. "Records what an agent was asked to do, did, and decided" |
| **"Effortless", "powerful", "intuitive", "robust", "blazing fast", "game-changing"** | adjectives are cheap and read as confident | an adjective that the reader cannot check is filler. Replace it with the number that would justify it, or cut it |
| **Title Case On Every Button** | it looks like a designed interface | sentence case. 60.9% of 1211 measured control labels are sentence case; 11.0% are title case |
| **`Submit`, `Confirm`, `OK`, `Continue`** | they are the generic safe labels | the control says what will happen. `Revoke key`, then `Key revoked` |
| **`An error occurred`, `Something went wrong`, `Oops!`** | a real message needs a real cause | what failed, why, and the next action, with the specifics |
| **Lorem ipsum, or plausible-but-fake data shipped as real** | a filled table demos better than an empty one | never. Fabricated records in an instrument of record are the one failure this portfolio cannot survive. Use an empty state, or data marked as sample on its face |
| **An exclamation mark** | it reads as enthusiastic | none. The product is not excited; it is telling you something |
| **A different noun for the same thing on three screens** | each screen was written on its own | one name per concept per product |

## Three more that are ours

- **A shadow on something that cannot be dismissed.** Elevation is a claim that a thing is above the page; a card is not.
- **Inventing a value because the token set did not have one.** This is the failure that produces 24 type sizes and 34 spacing values. Report the gap.
- **Solving a contrast pair by eye, or against the easiest surface.** Both shipped sub-AA pairs in this system's own first pass. A token is solved against the surface closest to it in lightness, and that rule was worth 11 failing pairs when it was corrected.

## The checklist

Run this against the screen before it ships.
Every answer must be **yes**.
A **no** is not a judgement call to weigh; it is a defect with a named rule above it.

1. Is every colour on this screen a token, and is every ink-on-ground pair in the permission table?
2. Is the primary action `hw-ink` rather than a chromatic colour, and is there exactly one of it?
3. Does every state on the screen carry a word, not only a colour?
4. Is there no gradient, no `backdrop-filter`, and no shadow on anything that cannot be dismissed, and does any patterned ground carry only ink certified against its own worst pixel?
5. Is every type size one of the nine steps, and is running text inside its measure?
6. Does every column of numbers carry `tabular-nums` and right alignment?
7. Is the content left-aligned, with centring only on a single-element empty state or a dialog's action row?
8. Does the vertical rhythm vary by what each section carries, rather than repeating one value?
9. Is every card a group of things read together and acted on together, rather than a shape the grid suggested?
10. Does every interactive element answer all nine states, disabled and loading and read-only included?
11. Is the focus ring present, 2px at 2px offset, and unremoved anywhere?
12. Is every icon from one set, at a painted 1.5px stroke, beside a label or inside a toolbar with a tooltip?
13. Does nothing animate on scroll, and does nothing move on hover or press?
14. Is every label sentence case and a verb that says what will happen?
15. Does every error name what failed and what to do next, with the specifics?
16. Are both empty states distinguished, so a filtered-to-zero view does not offer to create a first record?
17. Is every number on the screen real, with no lorem and no plausible placeholder data presented as real?
18. Does the screen work at 390px, at 768px, and at 1440px, with no horizontal scroll?
19. Read it in dark theme: is every pair still in the permission table, and has nothing gone invisible?

And six more wherever the screen takes input or leaves the desktop window:

20. Does every control in a row share one outer height, so a field and a button line up?
21. Does every control's boundary clear 3:1 against the surface it sits on, and not only look like an edge?
22. Is every required or optional marker a word, rather than a colour or a glyph on its own?
23. Does each error replace its hint, sit under its field, and carry `aria-invalid` and `aria-describedby`?
24. Is every hit target 44px on a coarse pointer, including the small ones inside rows?
25. If anything floats over content this system does not own, does it keep its opaque fill, its solved edge and its shadow in **both** themes?

And five more, which the surfaces specified in [37-navigation.md](37-navigation.md), [68-page-patterns.md](68-page-patterns.md) and [72-keyboard.md](72-keyboard.md) added to the gate:

26. Can a keyboard reach every action, including the ones that appear on hover, and is every composite widget one tab stop with the arrows moving inside it?
27. If the screen has a permanent rail, is the skip link the first tab stop, and is it hidden by clipping rather than by `display: none`?
28. Does a destructive action name its object, put focus on the safe answer, and take the inline confirm only when its scope is one reversible row?
29. Does a bulk selection say what it selected, and does selecting everything beyond the loaded page take a second explicit act that states the count?
30. Does every failure message say only what the reader is entitled to know - so that an authentication failure names the pair rather than which half was wrong?

**The test underneath all thirty:** if this could be any AI product's screen, something on this list is in it.

## What this checklist does, and what it cannot do

Stated plainly, because a gate that is believed to do more than it does is worse than no gate.

**A screen that fails one of the thirty is reliably generic.** Every item names a specific failure
with a measured rule above it, and each is the shape a default takes when nobody decided. That
direction of the test is strong and it is the direction that matters most, because generic is what
this system exists to prevent.

**A screen that answers all thirty is not automatically good.** The list removes failures; it does
not supply judgement. It cannot tell you that the heading is the wrong heading, that the table
should have been three columns, that the screen is answering a question nobody asked, or that a
gap of 24px was right where you used 16px - every one of those passes every item above.
[32-rhythm.md](32-rhythm.md) makes the same point about the spacing unit: a column of gaps reading
16, 16, 16, 16 is on the unit and has no rhythm at all.

So: run it as the last gate and not as the design. It is what stops a screen being indistinguishable
from every other product's, which is a floor rather than a ceiling, and this book is honest about
which of the two it is selling.
