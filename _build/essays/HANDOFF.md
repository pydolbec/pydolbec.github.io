# Handoff: writing a featured essay page for pydolbec.com

Use this in a new session to write one featured page (coffee, creators or world-cup). The streetwear page is the approved model: read `_build/essays/streetwear.en.html` first and match it.

## Setup
1. Attach the repo `pydolbec/pydolbec.github.io` and clone it.
2. Ask Pierre-Yann for the paper PDF:
   - coffee: `Dolbec, Arsel and Aboelenien 2022 A Practice Perspective on Market Evolution.pdf`
   - creators: `Dolbec and Smith 2025 From frame and follers to fortune How person-brands capture value in the creator economy.pdf`
   - world-cup: `Bitektine Dolbec 2025 Temporary regulations and institutional change.pdf`
   Read the whole paper body before drafting. Never invent findings, quotes, numbers, dates, names or mechanisms; if a claim cannot be evidenced from the paper, cut it.
3. Load the skills `academic-polish` (it runs clear-writing, academic-writing-style and antidetector, in that order) and apply all three passes, then a fidelity check against the paper.

## Output
One HTML fragment: `_build/essays/<slug>.en.html` (slug = coffee, creators or world-cup). `python3 _build/build.py` wraps it with the header, title (the card question in `_build/content.py`), citation, publisher link and pager. Commit and push to `main`; GitHub Pages deploys it.

The fragment starts inside the page's opening narrow column. Copy the streetwear file's structure and CSS classes exactly:
1. `<p class="standfirst">` — two sentences, about 40 words.
2. `<div class="meta">` — authors in order, journal (italic), year, read time.
3. `</div>` to close the column, then the hero photo slot, then reopen `<div class="narrow">`.
4. Abstract box (`inshort`, kicker "Abstract") — about 200 words. Name the paper's central construct here, once, in plain language.
5. Managers box (`mgrbox`) — a one-line lead and 3–4 numbered, concrete implications for managers, drawn only from the paper (its implications or recommendations sections, or direct translations of its mechanisms).
6. The puzzle — what was open, what was assumed. Informative heading, never atmospheric.
7. What we studied — the data, with the paper's numbers.
8. Figure 1 (inline SVG in `<figure class="figure">` with a `figcaption class="cap"`) — positions the contribution or shows the process over time.
9. The findings as theme blocks (`section.theme` > `theme-head` > `.mech` rows): explanation left (heading, 80–130 words, named examples, one evidence line with source), illustration right — an original SVG data figure when the paper gives numbers, otherwise a photo slot (`.slot`) with a precise brief and a licensing source.
10. Figure 2 — the phenomenon or exchange as a whole.
11. The complication — what the finding costs, who it is uncomfortable for, what it does not solve.
12. Where else this happens — transferability and the paper's scope conditions.
Target about 3,000 words.

## Writing rules (from the author's corrections)
- Translate the paper for a general reader and for scholars from other fields. Write in the nouns of the case (roasters, baristas, cafés; creators, followers, sponsors; regulators, FIFA, brewers), never the paper's construct or mechanism labels in the prose. Name the construct once, in the abstract.
- Verify every mechanism against the paper's own definition before writing it. Two past failures: rewriting a mechanism into a catchier phrase that changed its meaning ("turn the commercial into the joke" when the paper said streetwear's own commercial associations were reframed; "keeping what they'd been mocked for" when the paper said designers competed on streetwear's reference culture instead of technique).
- Headings informative, never atmospheric. No positioning against prior literature for its own sake; address the reader.
- "We" for co-authored papers, "I" for sole-authored ones. Active voice. Canadian spelling (behaviour, colour, -ize verbs).
- No negated-foil constructions ("not X but Y", "not simply X"). No summary-flourish endings, figurative turns, dramatic em dashes or rhetorical questions. Minimize judge, standing, ground, claim.
- One quotation per source, each under 15 words. Evidence on every claim.
- Photo slots: describe exactly what the image must show and where to license it. Never generate photographs.

## After the English page is approved
French translation goes in `_build/essays/<slug>.fr.html` (same structure). Text-only paper summaries (1,000–1,500 words, main table or figure, or a proposed one if the paper has none) are the next batch.
