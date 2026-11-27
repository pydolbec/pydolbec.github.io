# Rules for any session working in this repository

## Personal information: check before every push
This repository is public, and GitHub Pages serves every file in it at pydolbec.com, including `_build/`. Treat every commit as published.

1. Before every commit and push, read the staged diff and the commit message for personal information: anything about Pierre-Yann or another person that is not already on the public site. This includes career plans, private contact details, personal email addresses, file or folder paths from his computer or cloud storage, health, finances, unpublished work, private correspondence, and internal handoffs or review notes.
2. If you find any, stop. Tell Pierre-Yann what it is and where, and wait for his answer before pushing. Do not decide for him.
3. Never commit handoffs, briefs or review reports written for another session. They belong in the Claude Project. The two existing `HANDOFF.md` briefs under `_build/` are the only exception; keep personal details out of them.
4. Commit under a no-reply address, never a personal email address.

## Working on the site
- Edit sources only, never generated HTML: `_build/content.py` (text and data), `_build/build.py` (templates), `assets/css/site.css` (styles), `_build/essays/` and `_build/summaries/` (page text).
- Rebuild with `python3 _build/build.py`, check the pages, then commit the generated files with the sources.
- Other sessions push too: run `git pull --ff-only` before every commit.
- Never edit or delete `CNAME`.
- Ask before adding a new file type, a library or JavaScript.
