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
| a vivid field | data text or `hw-text-secondary` | a field carries display copy and one action, set in its solved label, `hw-on-field` |
| a state colour | art | art never says passed, warned or failed |
| two kinds of art | one view | one drawing, or one field, or one diagram per view |
| a loop | anything but a live signal or a determinate progress bar | [40-motion.md](40-motion.md#what-may-animate) |
| video, GIF, Lottie, Rive | any app | the runtime cost: `lottie-web` is 75 kB gzipped and `@rive-app/canvas` 51.5 kB plus a 1.9 MB wasm, against 1.9 KB for a whole first-run demo written in CSS |

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
| **texture** | a dot grille at a 9px pitch on the rail and the recorder deck | a ruled margin outside the sheet | a grid in the mount's margin, never under the reviewed page | none |

Every texture in the table is a ground whose every pixel is a solved token, certified against its worst pixel, as [75-spec-sheet.md](75-spec-sheet.md#2-surface-and-texture-styles) requires.
A figure appears in none of the three product columns: quoth's art is an engraving and drawings of real controls, and its record refuses the one figure set its curation proposed.

## Carousel slides

The slide sequence is [75-spec-sheet.md](75-spec-sheet.md#slide-sequence)'s, and a product reuses it rather than re-deriving it.
Per product, three things differ and nothing else: the field colour, the display face and the art language.
The frame, the margin, the corner labels, the two ordinals and the advance mark are the house's.
