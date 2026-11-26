# Handoff: writing paper summary pages for pydolbec.com

Use this in a new session to write a batch of paper summary pages. The approved model is `_build/summaries/online-reviewing.en.html`: match its length (about 750 words), structure and figure style. These are the shorter pages linked from "More research" and the Research list. The four featured essays (streetwear, coffee, creators, world-cup) are done; read `_build/essays/streetwear.en.html` for tone and figure style, but summary pages are shorter and simpler.

## Setup
1. Attach the repo `pydolbec/pydolbec.github.io` and clone it. Pull before you start and before you push: other sessions write to the same repo.
2. Ask Pierre-Yann for each paper's PDF (file names below). Read the whole paper body before drafting. Never invent findings, quotes, numbers, dates, names or mechanisms; if a claim cannot be evidenced from the paper, cut it.
3. Load the skill `academic-polish` (clear-writing, academic-writing-style, antidetector, in that order) and apply all three passes to each summary, then a fidelity check against the paper.

## Papers (slug → PDF)
- online-reviewing → `De Kerviler et al. - 2025 - Why and How Consumers Perform Online Reviewing Dif.pdf`
- sharing-and-hiding → `Darmody Dolbec Yuksel and Venkatraman 2025 Between sharing and hiding.pdf`
- hybrid-branding → `Gorman and Dolbec 2025 Entering a complex market, how hybrid branding helps new brands create distinctive and resonant identities.pdf`
- religious-schools → `Dolbec, Castilhos, Fonseca, and Trez 2022.pdf`
- enabled-theory-building → `dolbec-et-al-2021-something-old-something-new-enabled-theory-building-in-qualitative-marketing-research.pdf`
- spatial-types → `Castilhos and Dolbec 2017 Conceptualizing spatial types.pdf` (published 2018)
- spatial-perspective → `Castilhos, Dolbec, Veresiu (2017) Introducing a spatial perspective to analyze market dynamics.pdf`
- fallacy-of-facility → `Dolbec Fischer and Smith 2026 the fallacy of facility.pdf`
- refashioning-a-field → `Dolbec and Fischer 2015.pdf`
- flagship-store → `Chebat and Dolbec (2013).pdf`
- template-creep → `Fischer Dolbec 2024 template creep.pdf`
- in-or-out → `Dolbec and Fischer In_or_Out_How_Consumer_Performances_Lead.pdf` (chapter by Dolbec and Maciel, 2018)
- netnographic-analysis → `NetnographicAnalysisKozinetsDolbecEarley2014.pdf`

## Output
One HTML fragment per paper: `_build/summaries/<slug>.en.html`. `python3 _build/build.py` wraps it with the page header, the paper's full title, authors, a citation panel and the publisher link (all from `_build/content.py`; do not repeat them). Rebuild, commit and push to `main` after each paper, so a failed session loses at most one page.

Fragment structure (about 750 words, plain HTML, same CSS classes as the essays):
1. `<p class="standfirst">` — one or two sentences on what the paper shows, for a general reader.
2. `<div class="inshort"><div class="kicker">In short</div>…</div>` — three short paragraphs: the question, what the authors did, what they found. Name the paper's central construct here, once, in plain language.
3. Two to four sections with informative `<h2>` headings: the question and why it was open; the case or data, with the paper's numbers; the findings, in the nouns of the case; why it matters for scholars from other fields.
4. `<figure class="figure">` — the paper's main table or figure, redrawn as an original inline SVG (Inter font, ink `#141414`, greys, accent `#2546c9`), with `<figcaption class="cap"><b>Figure.</b> … Redrawn from Authors (Year).</figcaption>`. If the paper has no summary table or figure, propose one that captures its argument (a typology, a sequence, a comparison) and say in the caption that it is a summary of the paper.
5. Optional `<div class="mgrbox"><div class="kicker">What this means for managers</div><p class="lead">…</p><ol>…</ol></div>` — only when the paper supports concrete implications for managers. Two or three items. Leave it out for methods papers and chapters unless the paper itself speaks to practice.

## Writing rules (from the author's corrections)
- Translate the paper for a general reader and for scholars from other fields. Write in the nouns of the case; keep the paper's construct and mechanism labels out of the prose except the one naming in "In short".
- Verify every mechanism against the paper's own definition before writing it. Past failure: rewriting a mechanism into a catchier phrase that changed its meaning.
- Informative headings, never atmospheric. Address the reader; no positioning against prior literature for its own sake.
- "We" for co-authored papers, "I" for sole-authored ones. Active voice. Canadian spelling (behaviour, colour, -ize verbs).
- No negated-foil constructions ("not X but Y", "not simply X"). No summary-flourish endings, figurative turns, dramatic em dashes or rhetorical questions. Minimize judge, standing, ground, claim.
- One quotation per source, each under 15 words. Evidence on every claim.
- No photographs on summary pages.

## After the English pages are approved
French versions go in `_build/summaries/<slug>.fr.html`, same structure.
