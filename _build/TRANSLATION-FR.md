# French translation brief (essays and summaries)

Translate one English fragment into French and save it next to the source:
`_build/essays/<slug>.en.html` → `_build/essays/<slug>.fr.html`
`_build/summaries/<slug>.en.html` → `_build/summaries/<slug>.fr.html`

The site belongs to Pierre-Yann Dolbec, a Québécois marketing professor at Concordia (Montréal). Readers are educated non-specialists, scholars from other fields, journalists and managers.

## What to translate
- All visible text: paragraphs, headings, kickers, captions, table cells, figure labels inside SVG `<text>`, `alt` and `aria-label` attributes, credits.
- Fixed labels: "In short" → "En bref"; "What this means for managers" → "Ce que cela signifie pour les gestionnaires"; "Figure 1" → "Figure 1"; "Source:" → "Source :".

## What to keep exactly
- Every HTML tag, class, id, attribute name, `href`, `src`, SVG geometry (coordinates, sizes, viewBox). Only text nodes and human-readable attribute values change.
- Paper titles, journal names, book titles, brand and company names, personal names, quotations' sources.
- Direct quotations from interviewees or documents: translate them into French and keep the quotation marks as « … ». Do not invent or merge quotations.
- Numbers, statistics, dates, years, coefficients. Use French number formatting in prose (0,16; 1 200; 45 %), but leave β, p-values and model notation readable.
- The meaning, claims, qualifications and causal strength of every sentence. Add nothing, drop nothing.

## Language and style
- Standard written French as used in Québec academic and business writing: "gestionnaires" (not "managers"), "courriel", "entreprise", "marque", "commerce de détail". Avoid France-only anglicisms and Québec colloquialisms alike.
- Write natural French prose, not a calque of the English. Restructure sentences when English word order would read awkwardly. Keep the author's direct, active voice and first person ("j'ai constaté", "nous montrons"); sole-authored pieces use "je", co-authored use "nous" as in the source.
- One concept, one term: once you choose a French term for a construct, repeat it everywhere in the file. Keep the English term in parentheses on first use only when the French term would otherwise be unrecognizable to scholars (e.g., « travail institutionnel (institutional work) »).
- Avoid filler connectives (« De plus », « En outre », « Par ailleurs ») unless the relation needs them; prefer the word that names the relation (« parce que », « alors que », « donc »). Avoid the construction « non pas X, mais Y » used for rhetorical effect.
- French typography: non-breaking space (U+00A0) before : ; ? ! and inside « », and as thousands separator. Use the narrow no-break space U+202F only if you are consistent; U+00A0 is fine. Capitalize headings in sentence case.

## SVG figures
French runs about 15–20% longer. Labels must still fit their boxes: shorten wording before shrinking font. Keep font sizes ≥ 14 and the viewBox unchanged. Render the figure to check (Playwright + Chrome at /usr/bin/google-chrome is available; screenshot the built page or a standalone HTML wrapping the SVG) and fix any overflow or overlap.

## Check before finishing
1. Tag structure matches the source: compare counts of each tag and class between .en and .fr (a short Python script).
2. No English sentences left (except proper names and titles).
3. Every number in the English file appears in the French file (allowing for decimal comma).
4. Read the French once start to finish as a reader: does it flow as French?

Do not edit any other file, do not run the build, do not commit or push. Report: files written, the French terms you chose for the main constructs, and any passage where the meaning was uncertain.
