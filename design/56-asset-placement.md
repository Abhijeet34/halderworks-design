# Asset placement

Where each kind of asset lives, where it never appears, and when it shows.
"Not everything goes with everything" is the owner's instruction of 2026-09-22, and this file is the map that makes it checkable.

Styles may vary across products and within one, as [12-brand.md](12-brand.md#identities-are-not-one-style) records.
What keeps that from becoming six unrelated drawings on six screens is placement, not a single style: a licensed set does not stop a drawing being chosen per screen, and a map of where each kind may go does.
The construction of art itself is [55-iconography.md](55-iconography.md#illustration)'s, and what may move is [40-motion.md](40-motion.md#a-products-own-moments)'s.

## Never together

These hold in every product, the house included.

| never | beside | why |
|---|---|---|
| any art | an instrument surface: quoth's recorder pill and key, pointback's note card, papertrace's ledger | an instrument is read in a glance, and its view is on a hot path: quoth's pill mounts in 181 to 289ms |
| a figure | dense data: a table, a ledger, a history list with rows | a face pulls the eye off the rows; figures go only where a screen has nothing yet or asks for something |
| motion | a live signal: a level meter, a presence dot | two moving things make neither a signal, so while a live signal is on screen nothing else animates |
| a vivid field | data text or `hw-text-secondary` | a field carries display copy and one action, or stages one of the product's own objects, and everything set on it is its solved label, `hw-on-field` |
| a state colour | art | art never says passed, warned or failed |
| two kinds of art | one view | one drawing, or one field, or one diagram per view; a field staging an object is that view's field, so no drawing joins it |
| a loop | anything but a live signal or a determinate progress bar | [40-motion.md](40-motion.md#what-may-animate) |
| video, GIF, Lottie, Rive | any app | the runtime cost: `lottie-web` is 75 kB gzipped and `@rive-app/canvas` 51.5 kB plus a 1.9 MB wasm, against 1.9 KB for a whole first-run demo written in CSS |

## A field as a stage

A field may stage one of the product's own objects in place of display copy: a real piece of its interface, rendered by the product's own components, with corner labels and annotations around it.
It is the field's second use, beside display copy and one action.

- **One staged object per field, and one field per view.** A staged field counts as the view's field in the never-together table above, so it is never combined with an illustration, a figure or a diagram in the same view.
- **The object is real.** It is the shipped component in a demonstration state, never a drawing of it, because a drawing can show a feature that does not ship.
- **Everything on the field is `--hw-on-field`.** Corner labels, annotation labels and leader lines all take the field's solved label, and nothing in `hw-text-secondary` or a state colour is set on the field.
- **The object keeps its own surfaces.** Its text sits on its own surfaces, in pairs the permission table already certifies, and the field ends at the object's edge, so the field still carries no data text.
- **Corner labels are the slide frame's.** Each corner carries a fact that is true of the object, and a corner with nothing true to carry stays empty ([75-spec-sheet.md](75-spec-sheet.md#slide-sequence)). On a screen a corner label is text and never the mark set again, because the screen already carries its one mark ([80-anti-patterns.md](80-anti-patterns.md#the-checklist), question 33).
- **Annotations are the house component**, [65-components.md](65-components.md#annotation), and they never move; whatever the object itself plays is held to [40-motion.md](40-motion.md#a-products-own-moments).
- **No action on a staged field.** The screen's one primary action sits beside the field, on the ground, so the field's only text is labels.
- **Never the live instrument.** A staged object is a demonstration: it takes no input and no focus and adds no tab stop. So it is not the working control that checklist question 35 keeps off a first-run screen until its task, and the field never sits beside an instrument in use, which the first row of the never-together table refuses.

Measured on quoth's Field identity: `--hw-on-field` on `--hw-field` is 12.29:1 in light and 14.09:1 in dark, unchanged under `prefers-contrast: more`, from the same values quoth ships and `tests/fixtures/field/` builds.

## Per product

Each product owns its column: the column records what its design record decided, and a change starts there, not here.
quoth's column is its Field identity, decided 2026-09-28; papertrace's and pointback's are the product-identities proposal of 2026-09-22, which neither product has adopted yet.

| asset | quoth | papertrace | pointback | house |
|---|---|---|---|---|
| **hero art** | website: the 1880 public-domain engraving of dictation into Edison's phonograph, as an ink mask with one yellow mark and its credit caption; listing: a 6s recording of the real screen; in-app welcome: a play-once demo inside the recorder deck, three stills under reduced motion | website: the report itself as the proof panel on a seal field | website: the scribble and sticky note over a real page | docs: a gauge with real numbers |
| **spot illustration** | the Microphone and Accessibility steps: in-house drawings of the real macOS prompt and the System Settings list; static, shown while that step is current | website sections only, never in the report | website only, never in the chrome | none |
| **empty-state art** | in-house object drawings on History and Insights at zero, replaced by content on the first row | none: an empty section says "No findings." in italics | none: the margin's empty state is its instruction sentence | one pictogram, 48 or 64px |
| **success moment** | the first inserted dictation in setup, once per install; the typed line appears whole | none: a verified DOI is a word | a mark's ring fills solid when sent | none |
| **icons** | Lucide in the rail and controls | none in the report | the one mark | Lucide |
| **motion** | one named moment, the key sinking 2px on press over 120ms; the level ladder is data, not motion | none in the report; one stamp press on the site | the scribble draws on once per selection; the presence dot is the only loop | the house curves |
| **carousel slides** | social and store, never in the app | social | social and the README | release notes |
| **video** | website and store only, a recording of the shipped build, never a mock, with a poster frame for reduced motion | none | a README clip of one review round | none |
| **texture** | a dot grille at a 9px pitch on the recorder deck only: the Field refresh took it off the rail, and the welcome's play-once deck is the one surface that paints it today | a ruled margin outside the sheet | a grid in the mount's margin, never under the reviewed page | none |

Every texture in the table is a ground whose every pixel is a solved token, certified against its worst pixel, as [75-spec-sheet.md](75-spec-sheet.md#2-surface-and-texture-styles) requires.
A figure appears in none of the three product columns: quoth's art is an engraving and drawings of real controls, and its record refuses the one figure set its curation proposed.

## Carousel slides

The slide sequence is [75-spec-sheet.md](75-spec-sheet.md#slide-sequence)'s, and a product reuses it rather than re-deriving it.
Per product, three things differ and nothing else: the field colour, the display face and the art language.
The frame, the margin, the corner labels, the two ordinals and the advance mark are the house's.
