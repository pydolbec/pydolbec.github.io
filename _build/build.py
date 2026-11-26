#!/usr/bin/env python3
"""Builds the static bilingual site into the repository root.
Run from anywhere: python3 _build/build.py
"""
import html, os, sys, shutil
sys.path.insert(0, os.path.dirname(__file__))
from content import SITE, UI, PUBS, TOPICS, MEDIA, COURSES, TEXTBOOKS, CASE, BACKGROUND, BOARDS, ABOUT, BIOS, MEDIA_CONTACT, TEACHING, RESEARCH_INTRO

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import hashlib
CSS_V = hashlib.md5(open(os.path.join(ROOT, "assets/css/site.css"), "rb").read()).hexdigest()[:8]
LANGS = ["en", "fr"]
e = html.escape


def url(lang, path=""):
    path = path.strip("/")
    base = "/" if lang == "en" else "/fr/"
    return base + (path + "/" if path else "")


def tbd(lang, label=None):
    return f'<p class="tbd">[{e(label or UI[lang]["tbd"])}]</p>'


def year_label(p, lang):
    return str(p["year"]) if p["year"] else UI[lang]["in_press"]


def citation(p, lang):
    y = year_label(p, lang)
    det = f", {e(p['details'])}" if p["details"] else ""
    return f"{e(p['authors'])} ({y}). {e(p['title'])}. <i>{e(p['venue'])}</i>{det}."


def pub_link(p):
    return f"https://doi.org/{p['doi']}" if p["doi"] else p.get("url", "#")


def head(lang, title, desc, path):
    other = "fr" if lang == "en" else "en"
    t = UI[lang]
    nav = "".join(
        f'<a href="{url(lang, k)}"{" class=on" if path.split("/")[0] == k else ""}>{e(v)}</a>'
        for k, v in t["nav"])
    if lang == "en":
        toggle = f'<span class="cur">EN</span><a href="{url("fr", path)}" hreflang="fr" lang="fr">FR</a>'
    else:
        toggle = f'<a href="{url("en", path)}" hreflang="en" lang="en">EN</a><span class="cur">FR</span>'
    full = f"{e(title)} · {SITE['name']}" if title != SITE["name"] else SITE["name"]
    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="description" content="{e(desc)}">
<link rel="alternate" hreflang="en" href="{SITE['domain']}{url('en', path)}">
<link rel="alternate" hreflang="fr" href="{SITE['domain']}{url('fr', path)}">
<meta property="og:title" content="{full}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css?v={CSS_V}">
</head>
<body>
<header class="site-head"><div class="wrap">
<a class="brand" href="{url(lang)}">{SITE['name']}</a>
<nav class="nav" aria-label="Main">{nav}<span class="lang" aria-label="Language">{toggle}</span></nav>
</div></header>
<main>
"""


def foot(lang):
    links = "".join(f'<a href="{e(v)}" target="_blank" rel="noopener">{e(k)}</a>' for k, v in SITE["links"].items())
    return f"""</main>
<footer class="site-foot"><div class="wrap">
<div><b>{SITE['name']}</b><div style="margin-top:8px"><a href="mailto:{SITE['email']}">{SITE['email']}</a> · {UI[lang]['footer_city']}</div></div>
<nav aria-label="Profiles">{links}</nav>
</div></footer>
</body>
</html>
"""


def write(lang, path, doc):
    out = os.path.join(ROOT, "" if lang == "en" else "fr", path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)


def pub_row(p, lang):
    return (f'<a class="row" href="{url(lang, "research/" + p["slug"])}" data-kind="{p["kind"]}">'
            f'<span class="t">{e(p["title"])}</span><span class="v">{e(p["venue"])}</span>'
            f'<span class="y">{year_label(p, lang)}</span></a>')


def featured():
    return [p for p in PUBS if p.get("featured")]


def others():
    return sorted([p for p in PUBS if not p.get("featured")], key=lambda p: -(p["year"] or 9999))


def take_div(html_, cls):
    """Remove the first <div class="cls"> block (balanced) and return (rest, block)."""
    start = html_.find(f'<div class="{cls}">')
    if start < 0:
        return html_, ""
    i, depth = start, 0
    while i < len(html_):
        if html_.startswith("<div", i):
            depth += 1
        elif html_.startswith("</div>", i):
            depth -= 1
            if depth == 0:
                end = i + len("</div>")
                return html_[:start] + html_[end:], html_[start:end]
        i += 1
    return html_, ""


def take_tag(html_, tag, cls):
    start = html_.find(f'<{tag} class="{cls}">')
    if start < 0:
        return html_, ""
    end = html_.find(f"</{tag}>", start) + len(f"</{tag}>")
    return html_[:start] + html_[end:], html_[start:end]


# ---------- pages ----------

def home(lang):
    t = UI[lang]
    cards = ""
    for p in featured():
        cards += f"""<a class="card" href="{url(lang, 'research/' + p['slug'])}">
<img class="cardimg" src="{p['img']}" alt="" loading="lazy">
<div class="kicker">{e(p['tag'][lang])} · {e(p['venue'])}, {p['year']}</div>
<h3>{e(p['q'][lang])}</h3>
<div class="mgr"><b>{t['for_managers']}</b> {e(p['mgr'][lang])}</div>
</a>"""
    rows = "".join(pub_row(p, lang) for p in others()[:5])
    body = f"""<div class="wrap">
<section class="hero">
<div>
<div class="s1">{e(t['hero_small'])}</div>
<div class="big">{e(t['hero_big'])}</div>
<p class="s2">{e(t['hero_p2'])}</p>
<p class="s3"><b>{SITE['name']}</b> · {e(t['hero_p3'])}</p>
</div>
<img class="portrait" src="/assets/img/portrait.webp" alt="Portrait of Pierre-Yann Dolbec" width="800" height="800">
</section>
<section class="cards">{cards}</section>
<h2>{t['more_research']}</h2>
{rows}
<a class="more" href="{url(lang, 'research')}">{t['all_research']}</a>
</div>"""
    write(lang, "", head(lang, SITE["name"], t["hero_small"] + " " + t["hero_big"].lower(), "") + body + foot(lang))


def about(lang):
    t = UI[lang]
    bg = "".join(f'<div class="row bg"><span class="y" style="text-align:left">{y}</span><span>{e(d[lang])}</span></div>'
                 for y, d in BACKGROUND)
    boards = ", ".join(BOARDS)
    title = dict(t["nav"])["about"]
    body = f"""<div class="wrap"><div class="about">
<div><img class="portrait" src="/assets/img/portrait.webp" alt="Portrait of Pierre-Yann Dolbec" width="800" height="800">
<div class="facts"><b>{e(t['hero_p3'])}</b></div></div>
<div><h1 class="page" style="margin-top:0">{e(title)}</h1>
{"".join(f"<p>{e(x)}</p>" for x in ABOUT[lang])}
<h2>{t['background']}</h2>
{bg}
<p style="margin-top:40px"><a class="btn" href="/assets/cv.pdf">{t['cv']}</a></p>
</div></div></div>"""
    write(lang, "about", head(lang, title, t["hero_p3"], "about") + body + foot(lang))


def research(lang):
    t = UI[lang]
    feat = "".join(f"""<a class="card" href="{url(lang, 'research/' + p['slug'])}"><img class="cardimg" src="{p['img']}" alt="" loading="lazy">
<div class="kicker" style="margin-top:12px">{e(p['tag'][lang])}</div><h3>{e(p['q'][lang])}</h3></a>""" for p in featured())
    chips = "".join(f'<button class="chip{" on" if k == "all" else ""}" data-f="{k}">{e(v)}</button>' for k, v in t["filters"])
    allp = sorted(PUBS, key=lambda p: -(p["year"] or 9999))
    rows = "".join(pub_row(p, lang) for p in allp)
    title = dict(t["nav"])["research"]
    body = f"""<div class="wrap">
<h1 class="page">{e(title)}</h1>
<p class="intro">{e(RESEARCH_INTRO[lang])}</p>
<h2>{t['featured']}</h2>
<div class="feat4">{feat}</div>
<h2>{t['all_pubs']}</h2>
<div id="filters" style="margin-bottom:18px">{chips}</div>
<div id="pubs">{rows}</div>
</div>
<script>
document.querySelectorAll('#filters .chip').forEach(function(b){{b.addEventListener('click',function(){{
document.querySelectorAll('#filters .chip').forEach(function(c){{c.classList.remove('on')}});b.classList.add('on');
var f=b.dataset.f;document.querySelectorAll('#pubs .row').forEach(function(r){{r.style.display=(f==='all'||r.dataset.kind===f)?'':'none'}});
}})}});
</script>"""
    write(lang, "research", head(lang, title, t["hero_small"] + " " + t["hero_big"].lower(), "research") + body + foot(lang))


def media(lang):
    t = UI[lang]
    topics = "".join(f'<span class="chip" style="cursor:default">{e(x)}</span>' for x in TOPICS[lang])
    news = "".join(f'<div class="row news"><b>{e(o)}</b><span>{e(h)}</span><span class="y">{d}</span></div>' for d, o, h in MEDIA)
    title = dict(t["nav"])["media"]
    body = f"""<div class="wrap">
<div class="media-top"><div><h1 class="page">{e(title)}</h1><p class="intro">{e(t['media_intro'])}</p></div>
<div class="panel"><div class="kicker">{t['media_requests']}</div><p style="font-weight:600;font-size:18px;margin:10px 0 4px"><a href="mailto:{SITE['email']}">{SITE['email']}</a></p><p style="margin:0 0 10px">{MEDIA_CONTACT['phone']}</p><p style="font-size:14px;color:var(--muted);margin:0">{MEDIA_CONTACT['relations']}</p></div></div>
<h2>{t['topics']}</h2>
<div>{topics}</div>
<h2>{t['bio']}</h2>
<div class="bios">
<div class="bio"><div class="kicker">{t['short_bio']}</div><p id="bio-s">{e(BIOS[lang]['short'])}</p><button class="chip" onclick="navigator.clipboard.writeText(document.getElementById('bio-s').innerText)">{t['copy']}</button></div>
<div class="bio"><div class="kicker">{t['long_bio']}</div><p id="bio-l">{e(BIOS[lang]['long'])}</p><button class="chip" onclick="navigator.clipboard.writeText(document.getElementById('bio-l').innerText)">{t['copy']}</button></div>
</div>
<h2>{t['in_news']}</h2>
{news}
</div>"""
    write(lang, "media", head(lang, title, t["media_intro"], "media") + body + foot(lang))


def teaching(lang):
    t = UI[lang]
    books = ""
    for bk in TEXTBOOKS:
        cover = (f'<img src="{e(bk["cover"])}" alt="Cover of {e(bk["title"])}" loading="lazy" style="width:100%;height:auto;border:1px solid var(--line)">'
                 if bk["cover"] else '<div class="ph">[Cover]</div>')
        label = t["read_free"] if bk["action"] == "read" else t["download_pdf"]
        dl = ' download' if bk["action"] == "download" else ''
        missing = bk["link"].startswith("/") and not os.path.exists(os.path.join(ROOT, bk["link"].lstrip("/")))
        button = "" if missing else f'<a class="btn o" href="{e(bk["link"])}"{dl}>{label}</a>'
        books += f"""<div class="book">{cover}<div><div class="kicker">{bk['year']}</div><h3 style="margin-top:6px">{e(bk['title'])}</h3>
<p style="color:#333;font-size:16px">{e(bk['blurb'][lang])}</p>
{button}</div></div>"""
    courses = "".join(f'<div class="row course"><span class="y" style="text-align:left">{c}</span><span>{e(n)}</span><span class="v">{lv}</span></div>' for c, n, lv in COURSES)
    title = dict(t["nav"])["teaching"]
    intro = "".join(f"<p>{e(x)}</p>" for x in TEACHING[lang])
    body = f"""<div class="wrap">
<h1 class="page">{e(title)}</h1>
<div style="max-width:760px">{intro}</div>
<h2>{t['textbooks']}</h2>
<div class="books">{books}</div>
<h2>{t['courses']}</h2>
{courses}
<h2>{t['cases']}</h2>
<div class="case"><img src="/assets/img/kolo-nafaso.webp" alt="Two women carrying basins of shea nuts on their heads" loading="lazy" style="width:100%;height:auto;border:1px solid var(--line)"><div><div class="kicker">{CASE['venue']} · {CASE['year']}</div>
<h3 style="margin-top:8px">{e(CASE['title'])}</h3><div style="font-size:15px;color:var(--muted)">{e(CASE['authors'])}</div>
<p style="margin-top:16px"><a class="btn o" href="https://publishing.insead.edu/case/aak-kolo-nafaso">{t['view_case']}</a></p></div></div>
</div>"""
    write(lang, "teaching", head(lang, title, t["hero_p3"], "teaching") + body + foot(lang))


def featured_page(p, lang, nxt):
    t = UI[lang]
    path = "research/" + p["slug"]
    frag = os.path.join(os.path.dirname(__file__), "essays", f"{p['slug']}.{lang}.html")
    if os.path.exists(frag):
        essay = open(frag, encoding="utf-8").read()
        body = f"""<article class="essay"><div class="narrow essay-head">
<a class="more" style="margin:0 0 24px" href="{url(lang, 'research')}">{t['all_research_back']}</a>
<div class="kicker">{dict(t['nav'])['research']} · {e(p['tag'][lang])}</div>
<h1>{e(p['q'][lang])}</h1>
{essay}
<div class="narrow">
<div class="cite"><p>{citation(p, lang)} {'Figures: CC BY 4.0, Pierre-Yann Dolbec.' if lang == 'en' else 'Figures : CC BY 4.0, Pierre-Yann Dolbec.'}</p><a class="btn" href="{pub_link(p)}">{t['read_paper']}</a></div>
<div class="pager"><a href="{url(lang, 'research')}">{t['all_research_back']}</a>
<a href="{url(lang, 'research/' + nxt['slug'])}">{t['next']} {e(nxt['q'][lang])} →</a></div>
</div></article>"""
        write(lang, path, head(lang, p["q"][lang], p["title"], path) + body + foot(lang))
        return
    body = f"""<div class="narrow essay-head">
<a class="more" style="margin:0 0 24px" href="{url(lang, 'research')}">{t['all_research_back']}</a>
<div class="kicker">{dict(t['nav'])['research']} · {e(p['tag'][lang])}</div>
<h1>{e(p['q'][lang])}</h1>
{tbd(lang, 'Standfirst' if lang == 'en' else 'Chapeau')}
<div class="meta">{e(p['authors'])} · {e(p['venue'])}, {p['year']}</div>
</div>
<div class="wrap"><div class="ph hero-img">[{t['photo']}]</div></div>
<div class="narrow">
<div class="inshort"><div class="kicker">{t['in_short']}</div>{tbd(lang)}</div>
<h2>[{'The puzzle' if lang == 'en' else "L'énigme"}]</h2>
{tbd(lang)}{tbd(lang)}
<div class="figure"><div class="ph">[{t['fig_tbd']}]</div><div class="cap">[Caption]</div></div>
<h2>[{'What I found' if lang == 'en' else "Ce que j'ai trouvé"}]</h2>
{tbd(lang)}{tbd(lang)}
<h2>[{'What it changes' if lang == 'en' else 'Ce que cela change'}]</h2>
{tbd(lang)}
<div class="mgrbox"><div class="kicker">{t['managers_box']}</div>{tbd(lang)}</div>
<div class="cite"><p>{citation(p, lang)}</p><a class="btn" href="{pub_link(p)}">{t['read_paper']}</a></div>
<div class="pager"><a href="{url(lang, 'research')}">{t['all_research_back']}</a>
<a href="{url(lang, 'research/' + nxt['slug'])}">{t['next']} {e(nxt['q'][lang])} →</a></div>
</div>"""
    write(lang, path, head(lang, p["q"][lang], p["title"], path) + body + foot(lang))


def summary_page(p, lang):
    t = UI[lang]
    path = "research/" + p["slug"]
    kind = t[p["kind"]]
    frag = os.path.join(os.path.dirname(__file__), "summaries", f"{p['slug']}.{lang}.html")
    if os.path.exists(frag):
        html_ = open(frag, encoding="utf-8").read()
        html_, inshort = take_div(html_, "inshort")
        html_, mgr = take_div(html_, "mgrbox")
        html_, standfirst = take_tag(html_, "p", "standfirst")
        body = f"""<div class="wrap summary-page">
<a class="more" style="margin:48px 0 0" href="{url(lang, 'research')}">{t['all_research_back']}</a>
<header class="summary-head">
<div class="kicker" style="margin-top:28px">{kind} · {e(p['venue'])}, {year_label(p, lang)}</div>
<h1>{e(p['title'])}</h1>
<div style="color:var(--muted)">{e(p['authors'])}</div>
{standfirst}
</header>
<div class="summary-grid">
<article class="essay summary-main">{html_}</article>
<aside class="summary-side">{inshort}{mgr}</aside>
</div>
<div class="panel paper-cta"><div><div class="kicker">{t['the_paper']}</div><p>{citation(p, lang)}</p></div>
<a class="btn" href="{pub_link(p)}" target="_blank" rel="noopener">{t['read_publisher']}</a></div>
</div>"""
        write(lang, path, head(lang, p["title"], p["title"], path) + body + foot(lang))
        return
    body = f"""<div class="wrap"><div class="paper">
<div>
<a class="more" style="margin:48px 0 0" href="{url(lang, 'research')}">{t['all_research_back']}</a>
<div class="kicker" style="margin-top:28px">{kind} · {e(p['venue'])}, {year_label(p, lang)}</div>
<h1>{e(p['title'])}</h1>
<div style="color:var(--muted)">{e(p['authors'])}</div>
<h2 style="font-size:24px;margin-top:48px">{t['summary']}</h2>
{tbd(lang)}{tbd(lang)}
<div class="figure"><div class="ph">[{t['fig_tbd']}]</div><div class="cap">[Caption · Source]</div></div>
{tbd(lang)}{tbd(lang)}
</div>
<aside class="side"><div class="panel">
<div class="kicker">{t['the_paper']}</div>
<p style="font-size:15px;color:#333">{citation(p, lang)}</p>
<a class="btn" href="{pub_link(p)}">{t['read_publisher']}</a>
</div></aside>
</div></div>"""
    write(lang, path, head(lang, p["title"], p["title"], path) + body + foot(lang))


def main():
    fr_dir = os.path.join(ROOT, "fr")
    if os.path.isdir(fr_dir):
        shutil.rmtree(fr_dir)
    for d in ("about", "research", "media", "teaching"):
        if os.path.isdir(os.path.join(ROOT, d)):
            shutil.rmtree(os.path.join(ROOT, d))
    feats = featured()
    for lang in LANGS:
        home(lang); about(lang); research(lang); media(lang); teaching(lang)
        for i, p in enumerate(feats):
            featured_page(p, lang, feats[(i + 1) % len(feats)])
        for p in others():
            summary_page(p, lang)
    open(os.path.join(ROOT, ".nojekyll"), "w").close()
    print("built", sum(len(fs) for _, _, fs in os.walk(ROOT) if "index.html" in fs))


if __name__ == "__main__":
    main()
