#!/usr/bin/env python3
"""Builds the static bilingual site into the repository root.
Run from anywhere: python3 _build/build.py
"""
import html, json, os, re, sys, shutil
sys.path.insert(0, os.path.dirname(__file__))
from content import HOME_SEO, PAGE_DESC, SITE, UI, PUBS, TOPICS, MEDIA, COURSES, TEXTBOOKS, CASE, BACKGROUND, BOARDS, ABOUT, BIOS, MEDIA_CONTACT, TEACHING, RESEARCH_INTRO

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


NB = "\u00a0"


def authors(a, lang):
    """Author list as written in content.py; French pages use « et » and no serial comma."""
    return a if lang == "en" else re.sub(r",? and ", " et ", a)


def venue(p, lang):
    return p["venue"] if lang == "en" else p["venue"].replace("2nd ed.", "2e éd.")


def en(text, lang, tag="span"):
    """Mark English text (paper and course titles) inside French pages."""
    return text if lang == "en" else f'<{tag} lang="en">{text}</{tag}>'


def newtab(lang):
    return f'<span class="sr-only"> ({"opens in a new tab" if lang == "en" else "s’ouvre dans un nouvel onglet"})</span>'


def fr_typo(text):
    """French spacing: non-breaking space before : ; ? ! », after «, and inside numbers."""
    text = re.sub(r" ([:;?!»])", NB + r"\1", text)
    text = text.replace("« ", "«" + NB)
    text = re.sub(r"(\d) (M\$|G\$|\$|%|min\b|h\b|g\b|millions?\b|milliards?\b)", r"\1" + NB + r"\2", text)
    for _ in range(2):
        text = re.sub(r"(?<![\d.,])(\d{1,3}) (\d{3})(?!\d)", r"\1" + NB + r"\2", text)
    return text


def fr_page(doc):
    """Apply fr_typo to text nodes and to alt, aria-label and content attributes; skip scripts and styles."""
    def attrs(m):
        return re.sub(r'\b(alt|aria-label|content)="([^"]*)"', lambda a: f'{a.group(1)}="{fr_typo(a.group(2))}"', m)
    parts = re.split(r"(<script\b.*?</script>|<style\b.*?</style>|<[^>]+>)", doc, flags=re.S)
    out = []
    for part in parts:
        if part.startswith("<script") or part.startswith("<style"):
            out.append(part)
        elif part.startswith("<"):
            out.append(attrs(part))
        else:
            out.append(fr_typo(part))
    return "".join(out)


def fr_headings(doc):
    """In French headings, keep inverted verbs (« a-t-il », « transforment-ils ») and « au-delà » on one line."""
    pat = re.compile(r"\b\w+(?:-t)?-(?:ils?|elles?|on)\b|\bau-delà\b", re.I)

    def heading(m):
        parts = re.split(r"(<[^>]+>)", m.group(3))
        inner = "".join(x if x.startswith("<") else pat.sub(lambda w: f'<span class="nb">{w.group(0)}</span>', x) for x in parts)
        return m.group(1) + inner + m.group(4)
    return re.sub(r"(<h([1-4])\b[^>]*>)(.*?)(</h\2>)", heading, doc, flags=re.S)


def fix_tables(doc):
    """Table headers: empty corner cell is a td; column and row headers carry scope."""
    def thead(m):
        return re.sub(r"<th(?=[ >])(?![^>]*scope)", '<th scope="col"', m.group(0).replace("<th></th>", "<td></td>"))

    def tbody(m):
        return re.sub(r"<th(?=[ >])(?![^>]*scope)", '<th scope="row"', m.group(0))
    doc = re.sub(r"<thead>.*?</thead>", thead, doc, flags=re.S)
    return re.sub(r"<tbody>.*?</tbody>", tbody, doc, flags=re.S)


def citation(p, lang):
    y = year_label(p, lang)
    det = f", {e(p['details'])}" if p["details"] else ""
    return f"{e(authors(p['authors'], lang))} ({y}). {en(e(p['title']), lang)}. {en(e(venue(p, lang)), 'fr', 'i') if lang == 'fr' else '<i>' + e(venue(p, lang)) + '</i>'}{det}."


PERSON_ID = "https://pydolbec.com/#person"
SITE_ID = "https://pydolbec.com/#website"


def person_ld(lang, path):
    """schema.org graph for the pages about him: the site, the profile page and the person."""
    role = HOME_SEO[lang]
    page = SITE["domain"] + url(lang, path)
    person = {
        "@type": "Person", "@id": PERSON_ID,
        "name": SITE["name"], "alternateName": ["PY Dolbec", "Pierre Yann Dolbec"],
        "jobTitle": role["job"], "url": SITE["domain"] + "/",
        "image": SITE["domain"] + "/assets/img/portrait.webp", "email": "mailto:" + SITE["email"],
        "worksFor": {"@type": "CollegeOrUniversity", "name": "Concordia University",
                     "department": {"@type": "Organization", "name": "John Molson School of Business"}},
        "affiliation": {"@type": "CollegeOrUniversity", "name": "Concordia University"},
        "alumniOf": {"@type": "CollegeOrUniversity", "name": "York University",
                     "department": {"@type": "Organization", "name": "Schulich School of Business"}},
        "sameAs": list(SITE["links"].values()),
        "knowsAbout": ["Marketing", "Market creation", "Consumer culture", "Streetwear and luxury fashion",
                       "Specialty coffee", "Creator economy", "Institutional change"],
    }
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "@id": SITE_ID, "name": SITE["name"], "url": SITE["domain"] + "/", "inLanguage": ["en", "fr"]},
        {"@type": "ProfilePage", "@id": page, "url": page, "inLanguage": lang,
         "isPartOf": {"@id": SITE_ID}, "mainEntity": {"@id": PERSON_ID}},
        person]}
    return '<script type="application/ld+json">' + json.dumps(graph, ensure_ascii=False) + '</script>\n'


def pub_link(p):
    return f"https://doi.org/{p['doi']}" if p["doi"] else p.get("url", "#")


def head(lang, title, desc, path, img=None, ld=""):
    other = "fr" if lang == "en" else "en"
    t = UI[lang]
    nav = "".join(
        f'<a href="{url(lang, k)}"{(" class=on aria-current=" + ("page" if path == k else "true")) if path.split("/")[0] == k else ""}>{e(v)}</a>'
        for k, v in t["nav"])
    if lang == "en":
        toggle = f'<span class="cur">EN</span><a href="{url("fr", path)}" hreflang="fr" lang="fr">FR<span class="sr-only"> – français</span></a>'
    else:
        toggle = f'<a href="{url("en", path)}" hreflang="en" lang="en">EN<span class="sr-only"> – English</span></a><span class="cur">FR</span>'
    full = f"{e(title)} · {SITE['name']}" if title != SITE["name"] else SITE["name"]
    if path == "":
        role = HOME_SEO[lang]
        full = f"{SITE['name']} · {role['title']}"
        desc = role["desc"]
    if path in ("", "about"):
        ld = person_ld(lang, path)
    if lang == "fr":
        full, desc = fr_typo(full), fr_typo(desc)
    og_type = "article" if path.startswith("research/") else ("profile" if path in ("", "about") else "website")
    loc, loc_alt = ("en_CA", "fr_CA") if lang == "en" else ("fr_CA", "en_CA")
    labels = {"main": "Main", "lang": "Language", "skip": "Skip to content"} if lang == "en" else {"main": "Menu principal", "lang": "Langue", "skip": "Aller au contenu"}

    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE['domain']}{url(lang, path)}">
<link rel="alternate" hreflang="en" href="{SITE['domain']}{url('en', path)}">
<link rel="alternate" hreflang="fr" href="{SITE['domain']}{url('fr', path)}">
<link rel="alternate" hreflang="x-default" href="{SITE['domain']}{url('en', path)}">
<meta property="og:title" content="{full}">
<meta property="og:url" content="{SITE['domain']}{url(lang, path)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{SITE['name']}">
<meta property="og:locale" content="{loc}">
<meta property="og:locale:alternate" content="{loc_alt}">
<meta property="og:image" content="{SITE['domain']}{img or ('/assets/img/og/default.jpg' if lang == 'en' else '/assets/img/og/default-fr.jpg')}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{full}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico?v=2" sizes="any">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png?v=2">
<link rel="preload" href="/assets/fonts/inter-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
{ld}<link rel="stylesheet" href="/assets/css/site.css?v={CSS_V}">
<noscript><style>@media (max-width:820px){{.burger{{display:none}}.nav{{display:flex}}}}</style></noscript>
</head>
<body id="top">
<a class="skip" href="#main">{labels['skip']}</a>
<header class="site-head"><div class="wrap">
<a class="brand" href="{url(lang)}">{SITE['name']}</a>
<button type="button" class="burger" id="navbtn" aria-expanded="false" aria-controls="nav" aria-label="Menu"><span></span><span></span><span></span></button>
<nav class="nav" id="nav" aria-label="{labels['main']}">{nav}<span class="lang" role="group" aria-label="{labels['lang']}">{toggle}</span></nav>
</div></header>
<main id="main" tabindex="-1">
"""


# Phone and tablet menu: the button opens and closes the list, Escape closes it,
# and it is closed again when the page comes back through the Back button.
NAV_JS = """<script>
(function(){var b=document.getElementById('navbtn');if(!b)return;
function set(o){b.setAttribute('aria-expanded',o?'true':'false')}
b.addEventListener('click',function(){set(b.getAttribute('aria-expanded')!=='true')});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&b.getAttribute('aria-expanded')==='true'){set(false);b.focus()}});
window.addEventListener('pageshow',function(){set(false)});
})();
</script>
"""


def foot(lang):
    links = "".join(f'<a href="{e(v)}" target="_blank" rel="noopener">{e(k)}{newtab(lang)}</a>' for k, v in SITE["links"].items())
    return f"""</main>
<footer class="site-foot"><div class="wrap">
<div><b>{SITE['name']}</b><div style="margin-top:8px"><a href="mailto:{SITE['email']}">{SITE['email']}</a> · {UI[lang]['footer_city']}</div></div>
<nav aria-label="{'Profiles' if lang == 'en' else 'Profils'}">{links}</nav>
</div></footer>
{NAV_JS}</body>
</html>
"""


def write(lang, path, doc):
    out = os.path.join(ROOT, "" if lang == "en" else "fr", path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    doc = fix_imgs(doc)
    doc = fix_tables(doc)
    doc = wrap_wide(doc, lang)
    if lang == "fr":
        doc = fr_headings(fr_page(doc))
    with open(out, "w", encoding="utf-8") as f:
        f.write(doc)


def wrap_wide(doc, lang):
    """On phones, let wide figures and tables scroll sideways instead of shrinking."""
    hint = "Swipe sideways to see the full figure." if lang == "en" else "Faites glisser latéralement pour voir toute la figure."
    sw = f'<p class="swipe">{hint}</p>'
    count = [0]

    def region(kind=None):
        count[0] += 1
        word = kind or "Figure"
        return f'tabindex="0" role="region" aria-label="{word} {count[0]}, ' + ("scrolls sideways" if lang == "en" else "défile latéralement") + '"'

    def svg(m):
        vb = re.search(r'viewBox="0 0 ([\d.]+)', m.group(0)[:400])
        if vb and float(vb.group(1)) >= 600:
            return f'<div class="scrollx" {region()}>{m.group(0)}</div>{sw}'
        return m.group(0)
    doc = re.sub(r'(?<=<div class="figure">)\s*<svg\b.*?</svg>', svg, doc, flags=re.S)
    doc = re.sub(r'<figure class="figure">\s*(<svg\b.*?</svg>)', lambda m: '<figure class="figure">' + svg(re.match(r'.*', m.group(1), re.S)), doc, flags=re.S)
    doc = re.sub(r'(<table class="ftable".*?</table>)', lambda m: f'<div class="scrollx" {region("Table" if lang == "en" else "Tableau")}>{m.group(1)}</div>{sw.replace("figure", "table").replace("toute la table", "tout le tableau")}', doc, flags=re.S)
    return doc


_DIMS = {}


def fix_imgs(doc):
    """Give local images width/height (prevents layout shift); load the hero image first."""
    from PIL import Image

    def dims(src):
        if src not in _DIMS:
            fp = os.path.join(ROOT, src.split("?")[0].lstrip("/"))
            _DIMS[src] = Image.open(fp).size if os.path.exists(fp) else None
        return _DIMS[src]

    def add(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        if src and src.group(1).startswith("/") and "width=" not in tag:
            d = dims(src.group(1))
            if d:
                tag = tag.replace("<img ", f'<img width="{d[0]}" height="{d[1]}" ', 1)
        return tag
    doc = re.sub(r"<img\b[^>]*>", add, doc)
    m = re.search(r'class="hero-img[^"]*">(?:\s*<figure[^>]*>)?\s*<img\b[^>]*>', doc)
    if m:
        tag = m.group(0)
        new = tag.replace(' loading="lazy"', "")
        if "fetchpriority" not in new:
            new = new.replace("<img ", '<img fetchpriority="high" ', 1)
        doc = doc.replace(tag, new, 1)
    return doc


def pub_row(p, lang, publisher=False):
    if publisher:
        label = "Publisher" if lang == "en" else "Éditeur"
        if "researchgate.net" in pub_link(p):
            label = "ResearchGate"
        sep = ": " if lang == "en" else NB + ": "
        tab = "opens in a new tab" if lang == "en" else "s’ouvre dans un nouvel onglet"
        return (f'<li class="row pubrow" data-kind="{p["kind"]}">'
                f'<a class="t" href="{url(lang, "research/" + p["slug"])}">{en(e(p["title"]), lang)}</a><span class="v">{en(e(venue(p, lang)), lang)}</span>'
                f'<span class="y">{year_label(p, lang)} · <a class="pub" href="{pub_link(p)}" target="_blank" rel="noopener" '
                f'aria-label="{label}{sep}{e(p["title"])} ({tab})">{label}&nbsp;↗</a></span></li>')
    return (f'<li><a class="row" href="{url(lang, "research/" + p["slug"])}" data-kind="{p["kind"]}">'
            f'<span class="t">{en(e(p["title"]), lang)}</span><span class="v">{en(e(venue(p, lang)), lang)}</span>'
            f'<span class="y">{year_label(p, lang)}</span></a></li>')


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
    for i, p in enumerate(featured()):
        load = 'fetchpriority="high"' if i == 0 else 'loading="lazy"'  # the first card is on the first phone screen
        cards += f"""<a class="card" href="{url(lang, 'research/' + p['slug'])}">
<img class="cardimg" src="{p['img']}" alt="" {load}>
<div class="kicker">{e(p['tag'][lang])} · {en(e(p['venue']), lang)},{NB}{p['year']}</div>
<h3>{e(p['q'][lang])}</h3>
<div class="mgr"><b>{t['for_managers']}</b> {e(p['mgr'][lang])}</div>
</a>"""
    rows = "".join(pub_row(p, lang) for p in others()[:5])
    body = f"""<div class="wrap">
<section class="hero">
<div>
<h1 class="hero-h1"><span class="s1">{e(t['hero_small'])}</span> <span class="big">{e(t['hero_big'])}</span></h1>
<p class="s2">{e(t['hero_p2'])}</p>
<p class="s3"><b>{SITE['name']}</b><span class="sep"> · </span>{e(t['hero_p3'])}</p>
</div>
<img class="portrait" src="/assets/img/portrait.webp" alt="{'Portrait of' if lang == 'en' else 'Portrait de'} Pierre-Yann Dolbec" width="720" height="720">
</section>
<h2 class="sr-only">{t['featured']}</h2>
<section class="cards">{cards}</section>
<h2>{t['more_research']}</h2>
<ul class="rows">{rows}</ul>
<a class="more" href="{url(lang, 'research')}">{t['all_research']}</a>
</div>"""
    write(lang, "", head(lang, SITE["name"], t["hero_small"] + " " + t["hero_big"].lower(), "") + body + foot(lang))


def about(lang):
    t = UI[lang]
    bg = "".join(f'<li class="row bg"><span class="y" style="text-align:left">{y}</span><span>{e(d[lang])}</span></li>'
                 for y, d in BACKGROUND)
    profiles = " · ".join(f'<a href="{e(SITE["links"][k])}" target="_blank" rel="noopener">{k}&nbsp;↗{newtab(lang)}</a>' for k in ("Google Scholar", "ORCID"))
    boards = ", ".join(BOARDS)
    title = dict(t["nav"])["about"]
    body = f"""<div class="wrap"><div class="about">
<div><img class="portrait" src="/assets/img/portrait.webp" alt="{'Portrait of' if lang == 'en' else 'Portrait de'} Pierre-Yann Dolbec" width="720" height="720">
<div class="facts"><b>{e(t['hero_p3'])}</b></div></div>
<div><h1 class="page" style="margin-top:0">{e(title)}</h1>
{"".join(f"<p>{e(x)}</p>" for x in ABOUT[lang])}
<h2>{t['background']}</h2>
<ul class="rows">{bg}</ul>
<p style="margin-top:40px"><a class="btn" href="/assets/Pierre-Yann_Dolbec_CV.pdf" target="_blank" rel="noopener">{t['cv']}{newtab(lang)}</a></p>
<p class="profile-links">{profiles}</p>
</div></div></div>"""
    write(lang, "about", head(lang, title, PAGE_DESC[lang]["about"], "about") + body + foot(lang))


def research(lang):
    t = UI[lang]
    feat = "".join(f"""<a class="card" href="{url(lang, 'research/' + p['slug'])}"><img class="cardimg" src="{p['img']}" alt="" loading="lazy">
<div class="kicker" style="margin-top:12px">{e(p['tag'][lang])}</div><h3>{e(p['q'][lang])}</h3></a>""" for p in featured())
    chips = "".join(f'<button type="button" class="chip{" on" if k == "all" else ""}" data-f="{k}" aria-pressed="{"true" if k == "all" else "false"}">{e(v)}</button>' for k, v in t["filters"])
    profiles = " · ".join([f'<a href="/assets/Pierre-Yann_Dolbec_CV.pdf" target="_blank" rel="noopener">CV (PDF)&nbsp;↗{newtab(lang)}</a>'] + [
        f'<a href="{e(SITE["links"][k])}" target="_blank" rel="noopener">{k}&nbsp;↗{newtab(lang)}</a>' for k in ("Google Scholar", "ORCID")])
    shown = "publications shown" if lang == "en" else "publications affichées"
    allp = sorted(PUBS, key=lambda p: -(p["year"] or 9999))
    rows = "".join(pub_row(p, lang, publisher=True) for p in allp)
    title = dict(t["nav"])["research"]
    body = f"""<div class="wrap">
<h1 class="page">{e(title)}</h1>
{"".join(f'<p class="intro">{e(x)}</p>' for x in RESEARCH_INTRO[lang])}
<p class="profile-links">{profiles}</p>
<h2>{t['featured']}</h2>
<div class="feat4">{feat}</div>
<h2 id="pubs-h">{t['all_pubs']}</h2>
<div id="filters" role="group" aria-labelledby="pubs-h" style="margin-bottom:18px">{chips}</div>
<p id="pubcount" class="sr-only" role="status" data-label="{shown}"></p>
<ul id="pubs" class="rows">{rows}</ul>
</div>
<script>
document.querySelectorAll('#filters .chip').forEach(function(b){{b.addEventListener('click',function(){{
document.querySelectorAll('#filters .chip').forEach(function(c){{c.classList.remove('on');c.setAttribute('aria-pressed','false')}});b.classList.add('on');b.setAttribute('aria-pressed','true');
var f=b.dataset.f,n=0;document.querySelectorAll('#pubs .row').forEach(function(r){{var s=(f==='all'||r.dataset.kind===f);r.style.display=s?'':'none';if(s)n++}});
var st=document.getElementById('pubcount');st.textContent=n+' '+st.dataset.label;
}})}});
</script>"""
    write(lang, "research", head(lang, title, PAGE_DESC[lang]["research"], "research") + body + foot(lang))


def media(lang):
    t = UI[lang]
    topics = "".join(f'<li class="chip tag">{e(x)}</li>' for x in TOPICS[lang])

    def headline(h, hl):
        return f"<span>{e(h)}</span>" if hl == lang else f'<span lang="{hl}">{e(h)}</span>'
    news = "".join(f'<li class="row news"><b>{e(o)}</b>{headline(h, (hl or ["en"])[0])}<span class="y">{d}</span></li>' for d, o, h, *hl in MEDIA)
    mc = MEDIA_CONTACT[lang]
    copied = "Copied" if lang == "en" else "Copié"

    def copy_btn(key):
        return (f'<button type="button" class="chip" id="bio-{key}-b" aria-labelledby="bio-{key}-b bio-{key}-h" data-done="{copied}" '
                f"onclick=\"navigator.clipboard.writeText(document.getElementById('bio-{key}').innerText);this.textContent=this.dataset.done;document.getElementById('bio-st').textContent=this.dataset.done\">{t['copy']}</button>")
    title = dict(t["nav"])["media"]
    body = f"""<div class="wrap">
<div class="media-top"><div><h1 class="page">{e(title)}</h1><p class="intro">{e(t['media_intro'])}</p></div>
<div class="panel"><div class="kicker">{t['media_requests']}</div><p style="font-weight:600;font-size:18px;margin:10px 0 4px"><a href="mailto:{SITE['email']}">{SITE['email']}</a></p><p style="margin:0 0 10px">{mc['phone']}</p><p style="font-size:14px;color:var(--muted);margin:0">{mc['relations']} · <a href="mailto:{mc['relations_email']}">{mc['relations_email']}</a></p></div></div>
<h2>{t['topics']}</h2>
<ul class="topics">{topics}</ul>
<h2>{t['bio']}</h2>
<div class="bios">
<div class="bio"><div class="kicker" id="bio-s-h">{t['short_bio']}</div><p id="bio-s">{e(BIOS[lang]['short'])}</p>{copy_btn('s')}</div>
<div class="bio"><div class="kicker" id="bio-l-h">{t['long_bio']}</div><p id="bio-l">{e(BIOS[lang]['long'])}</p>{copy_btn('l')}</div>
</div>
<span id="bio-st" class="sr-only" role="status"></span>
<h2>{t['in_news']}</h2>
<ul class="rows">{news}</ul>
</div>"""
    write(lang, "media", head(lang, title, PAGE_DESC[lang]["media"], "media") + body + foot(lang))


def teaching(lang):
    t = UI[lang]
    books = ""
    for bk in TEXTBOOKS:
        cover = (f'<img src="{e(bk["cover"])}" alt="{"Cover of" if lang == "en" else "Couverture de"} {e(bk["title"])}" loading="lazy" style="width:100%;height:auto;border:1px solid var(--line)">'
                 if bk["cover"] else '<div class="ph">[Cover]</div>')
        label = t["read_free"] if bk["action"] == "read" else t["download_pdf"]
        dl = ' download' if bk["action"] == "download" else ''
        missing = bk["link"].startswith("/") and not os.path.exists(os.path.join(ROOT, bk["link"].lstrip("/")))
        ext = f' target="_blank" rel="noopener"' if bk["action"] == "read" else ""
        button = "" if missing else f'<a class="btn o" href="{e(bk["link"])}"{dl}{ext}>{label}{"&nbsp;↗" + newtab(lang) if ext else ""}</a>'
        books += f"""<div class="book">{cover}<div><div class="kicker">{bk['year']}</div><h3 style="margin-top:6px">{en(e(bk['title']), lang)}</h3>
<p style="color:#333;font-size:16px">{e(bk['blurb'][lang])}</p>
{button}</div></div>"""
    levels = {} if lang == "en" else {"BComm": "B. Comm.", "MSc": "M. Sc.", "PhD": "Ph. D."}
    courses = "".join(f'<li class="row course"><span class="y" style="text-align:left">{c}</span><span>{en(e(n), lang)}</span><span class="v">{levels.get(lv, lv)}</span></li>' for c, n, lv in COURSES)
    title = dict(t["nav"])["teaching"]
    intro = "".join(f"<p>{e(x)}</p>" for x in TEACHING[lang])
    body = f"""<div class="wrap">
<h1 class="page">{e(title)}</h1>
<div class="page-intro">{intro}</div>
<h2>{t['textbooks']}</h2>
<div class="books">{books}</div>
<h2>{t['courses']}</h2>
<ul class="rows">{courses}</ul>
<h2>{t['cases']}</h2>
<div class="case"><img src="/assets/img/kolo-nafaso.webp" alt="{'Two women carrying basins of shea nuts on their heads' if lang == 'en' else 'Deux femmes portant sur la tête des bassines de noix de karité'}" loading="lazy" style="width:100%;height:auto;border:1px solid var(--line)"><div><div class="kicker">{CASE['venue']} · {CASE['year']}</div>
<h3 style="margin-top:8px">{en(e(CASE['title']), lang)}</h3><div style="font-size:15px;color:var(--muted)">{e(authors(CASE['authors'], lang))}</div>
<p style="margin-top:16px"><a class="btn o" href="https://publishing.insead.edu/case/aak-kolo-nafaso" target="_blank" rel="noopener">{t['view_case']}&nbsp;↗{newtab(lang)}</a></p></div></div>
</div>"""
    write(lang, "teaching", head(lang, title, PAGE_DESC[lang]["teaching"], "teaching") + body + foot(lang))


def article_ld(p, lang):
    """schema.org ScholarlyArticle describing the paper a research page presents."""
    names = [a.strip() for a in re.split(r",\s*(?:and\s+)?|\s+and\s+", p["authors"]) if a.strip()]
    me = {"@type": "Person", "@id": PERSON_ID, "name": SITE["name"], "url": SITE["domain"] + "/", "sameAs": list(SITE["links"].values())}
    chapter = p.get("kind") == "chapter"
    art = {
        "@context": "https://schema.org",
        "@type": "Chapter" if chapter else "ScholarlyArticle",
        "headline": p["title"], "name": p["title"],
        "author": [me if n == SITE["name"] else {"@type": "Person", "name": n} for n in names],
        "datePublished": str(p["year"]), "inLanguage": "en",
        "url": pub_link(p),
        "mainEntityOfPage": SITE["domain"] + url(lang, "research/" + p["slug"]),
    }
    det = p.get("details") or ""
    if chapter:
        book = re.match(r"(.*?)\s*\(([^)]+)\)$", p["venue"])
        art["isPartOf"] = ({"@type": "Book", "name": book.group(1), "publisher": {"@type": "Organization", "name": book.group(2)}}
                           if book else {"@type": "Book", "name": p["venue"]})
        if det:
            art["pagination"] = det
    else:
        part = {"@type": "Periodical", "name": p["venue"]}
        m = re.match(r"(\d+)(?:\((\d+)\))?,\s*(.+)$", det)
        if m:
            part = {"@type": "PublicationVolume", "volumeNumber": m.group(1), "isPartOf": part}
            if m.group(2):
                part = {"@type": "PublicationIssue", "issueNumber": m.group(2), "isPartOf": part}
            art["pagination"] = m.group(3)
        art["isPartOf"] = part
    if p.get("doi"):
        art["identifier"] = {"@type": "PropertyValue", "propertyID": "DOI", "value": p["doi"]}
        art["sameAs"] = "https://doi.org/" + p["doi"]
    return '<script type="application/ld+json">' + json.dumps(art, ensure_ascii=False) + "</script>\n"


def paper_desc(p, lang, frag_html):
    """Search description for a research page: who wrote it, where, then the standfirst."""
    names = [a.strip() for a in re.split(r",\s*(?:and\s+)?|\s+and\s+", p["authors"]) if a.strip()]
    j = " and " if lang == "en" else " et "
    if len(names) <= 3 or names[-1] == "Pierre-Yann Dolbec":
        who = j.join(names) if len(names) <= 2 else ", ".join(names[:-1]) + j + names[-1]
    else:
        upto = names[: names.index("Pierre-Yann Dolbec") + 1] if "Pierre-Yann Dolbec" in names else names[:1]
        who = ", ".join(upto) + (" and colleagues" if lang == "en" else " et coll.")
    m = re.search(r'<p class="standfirst">(.*?)</p>', frag_html, re.S)
    sf = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else p["title"]
    first = re.match(r"(.+?[.?!])(\s|$)", sf)
    return f"{first.group(1) if first else sf} {who}, {venue(p, lang)}, {p['year']}."


def add_toc(essay, lang):
    """Give each section heading an anchor and list the sections above the Abstract box."""
    heads = []

    def tag(m):
        heads.append(re.sub(r"<[^>]+>", "", m.group(1)).strip())
        return f'<h2 id="s{len(heads)}">{m.group(1)}</h2>'
    essay = re.sub(r"<h2>(.*?)</h2>", tag, essay, flags=re.S)
    if len(heads) < 3:
        return essay
    label = "In this article" if lang == "en" else "Dans cet article"
    items = "".join(f'<li><a href="#s{i}">{h}</a></li>' for i, h in enumerate(heads, 1))
    toc = f'<nav class="toc" aria-label="{label}"><div class="kicker">{label}</div><ol>{items}</ol></nav>\n'
    i = essay.find('<div class="inshort">')
    if i < 0:
        i = essay.find('<h2 id="s1">')
    return essay[:i] + toc + essay[i:]


def figure_text(essay, lang):
    """After each wide essay figure, repeat its labels as a list that only screen readers get.
    The drawing is exposed as one image, so its dates and numbers are otherwise unreachable."""
    intro = "Figure content as text:" if lang == "en" else "Contenu de la figure en texte :"

    def items(svg):
        out, prev = [], None
        for m in re.finditer(r"<text\b([^>]*)>(.*?)</text>", svg, re.S):
            text = re.sub(r"<tspan\b[^>]*\b(?:x|dy)=[^>]*>", " ", m.group(2))  # a tspan on a new line
            text = html.unescape(re.sub(r"<[^>]+>", "", text))
            text = re.sub(r"\s+", " ", text).strip()
            if not text:
                continue
            x = re.search(r'\bx="([\d.-]+)"', m.group(1))
            y = re.search(r'\by="([\d.-]+)"', m.group(1))
            pos = (float(x.group(1)), float(y.group(1))) if x and y else None
            style = re.sub(r'\b[xy]="[^"]*"', "", m.group(1)).strip()
            between = svg[prev[3]:m.start()] if prev else ""
            # a wrapped label continues on the next line: same x, same style, next line down
            if (prev and pos and prev[0] and prev[1] == style and "<g" not in between and "</g>" not in between
                    and abs(pos[0] - prev[0][0]) < 1 and 0 < pos[1] - prev[0][1] <= 22):
                out[-1] += " " + text
            else:
                out.append(text)
            prev = (pos, style, text, m.end())
        return out

    def add(m):
        vb = re.search(r'viewBox="0 0 ([\d.]+)', m.group(2)[:400])
        if not (vb and float(vb.group(1)) >= 600):
            return m.group(0)
        lis = "".join(f"<li>{e(t)}</li>" for t in items(m.group(2)))
        return f'{m.group(1)}{m.group(2)}<div class="sr-only"><p>{intro}</p><ul>{lis}</ul></div>'
    return re.sub(r'(<(?:div|figure) class="figure">\s*)(<svg\b.*?</svg>)', add, essay, flags=re.S)


def featured_page(p, lang, nxt):
    t = UI[lang]
    path = "research/" + p["slug"]
    frag = os.path.join(os.path.dirname(__file__), "essays", f"{p['slug']}.{lang}.html")
    if os.path.exists(frag):
        essay = add_toc(open(frag, encoding="utf-8").read(), lang)
        essay = figure_text(essay, lang)
        paper = f'<a href="{pub_link(p)}" target="_blank" rel="noopener">{t["read_paper"]}&nbsp;↗{newtab(lang)}</a>'
        essay = re.sub(r'(<div class="meta">.*?)(</div>)', lambda m: m.group(1) + " · " + paper + m.group(2), essay, count=1, flags=re.S)
        body = f"""<article class="essay"><div class="narrow essay-head">
<a class="more" style="margin:0 0 24px" href="{url(lang, 'research')}">{t['all_research_back']}</a>
<div class="kicker">{dict(t['nav'])['research']} · {e(p['tag'][lang])}</div>
<h1>{e(p['q'][lang])}</h1>
{essay}
<div class="narrow">
<div class="cite"><p>{citation(p, lang)} {'Figures: CC BY 4.0, Pierre-Yann Dolbec.' if lang == 'en' else 'Figures : CC BY 4.0, Pierre-Yann Dolbec.'}</p><a class="btn" href="{pub_link(p)}" target="_blank" rel="noopener">{t['read_paper']}&nbsp;↗{newtab(lang)}</a></div>
<p class="totop"><a href="#top">{'↑ Back to top' if lang == 'en' else '↑ Haut de page'}</a></p>
<div class="pager"><a href="{url(lang, 'research')}">{t['all_research_back']}</a>
<a href="{url(lang, 'research/' + nxt['slug'])}">{t['next']} {e(nxt['q'][lang])} →</a></div>
</div></article>"""
        write(lang, path, head(lang, p["q"][lang], paper_desc(p, lang, essay), path, "/assets/img/og/" + p["slug"] + ".jpg", ld=article_ld(p, lang)) + body + foot(lang))
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
    write(lang, path, head(lang, p["q"][lang], p["title"], path, "/assets/img/og/" + p["slug"] + ".jpg") + body + foot(lang))


def summary_page(p, lang, nxt=None):
    t = UI[lang]
    path = "research/" + p["slug"]
    kind = t[p["kind"]]
    frag = os.path.join(os.path.dirname(__file__), "summaries", f"{p['slug']}.{lang}.html")
    if os.path.exists(frag):
        html_ = open(frag, encoding="utf-8").read()
        html_, inshort = take_div(html_, "inshort")
        html_, mgr = take_div(html_, "mgrbox")
        html_, standfirst = take_tag(html_, "p", "standfirst")
        nxt_link = f'<a href="{url(lang, "research/" + nxt["slug"])}">{t["next"]} {en(e(nxt["title"]), lang)} →</a>' if nxt else ""
        if mgr and inshort:
            # on one-column layouts the managers box sits after the text: link to it from In short
            mgr = mgr.replace('<div class="mgrbox">', '<div class="mgrbox" id="managers">', 1)
            inshort = inshort[:inshort.rindex("</div>")] + f'<p class="jump"><a href="#managers">{t["managers_box"]}&nbsp;↓</a></p></div>'
        body = f"""<div class="wrap summary-page">
<a class="more" style="margin:48px 0 0" href="{url(lang, 'research')}">{t['all_research_back']}</a>
<header class="summary-head">
<div class="kicker" style="margin-top:28px">{kind} · {en(e(venue(p, lang)), lang)}, {year_label(p, lang)}</div>
<h1>{en(e(p['title']), lang)}</h1>
<div style="color:var(--muted)">{e(authors(p['authors'], lang))}</div>
{standfirst}
</header>
<div class="summary-grid">
{inshort}
<article class="essay summary-main">{html_}</article>
{mgr}
</div>
<div class="panel paper-cta"><div><div class="kicker">{t['the_paper']}</div><p>{citation(p, lang)}</p></div>
<a class="btn" href="{pub_link(p)}" target="_blank" rel="noopener">{'ResearchGate' if 'researchgate.net' in pub_link(p) else t['read_publisher']}&nbsp;↗{newtab(lang)}</a></div>
<div class="pager"><a href="{url(lang, 'research')}">{t['all_research_back']}</a>
{nxt_link}</div>
</div>"""
        write(lang, path, head(lang, p["title"] if lang == "en" else f"{t['summary']} : {p['title']}", paper_desc(p, lang, standfirst), path, ld=article_ld(p, lang)) + body + foot(lang))
        return
    body = f"""<div class="wrap"><div class="paper">
<div>
<a class="more" style="margin:48px 0 0" href="{url(lang, 'research')}">{t['all_research_back']}</a>
<div class="kicker" style="margin-top:28px">{kind} · {e(p['venue'])}, {year_label(p, lang)}</div>
<h1>{e(p['title'])}</h1>
<div style="color:var(--muted)">{e(p['authors'] if lang == 'en' else p['authors'].replace(' and ', ' et '))}</div>
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


def seo_files():
    """Write sitemap.xml (EN pages with FR alternates) and robots.txt."""
    paths = []
    for dirpath, _, files in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT).replace(os.sep, "/")
        if rel == ".":
            rel = ""
        if "index.html" not in files or rel.startswith(("fr", "_", ".", "assets")):
            continue
        paths.append(rel)
    entries = []
    for p in sorted(paths):
        alts = "".join(
            f'\n    <xhtml:link rel="alternate" hreflang="{h}" href="{SITE["domain"]}{url(l, p)}"/>'
            for h, l in (("en", "en"), ("fr", "fr"), ("x-default", "en")))
        for lang in LANGS:
            entries.append(f'  <url>\n    <loc>{SITE["domain"]}{url(lang, p)}</loc>{alts}\n  </url>')
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
                'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(entries) + "\n</urlset>\n")
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nDisallow: /_build/\n\nSitemap: {SITE['domain']}/sitemap.xml\n")


def not_found():
    """404.html at the site root: GitHub Pages serves it for any missing address."""
    doc = head("en", "Page not found", "This page does not exist.", "404")
    doc = re.sub(r'<link rel="(?:canonical|alternate)"[^>]*>\n', "", doc)
    doc = re.sub(r'<meta property="og:[^>]*>\n', "", doc)
    doc = doc.replace('<meta name="viewport"', '<meta name="robots" content="noindex">\n<meta name="viewport"', 1)
    doc = doc.replace('href="/fr/404/"', 'href="/fr/"')
    body = f"""<div class="wrap">
<h1 class="page">Page not found</h1>
<p class="intro">This page does not exist. Try the <a href="/">home page</a> or the <a href="/research/">research list</a>.</p>
<p class="intro" lang="fr">Cette page n’existe pas. Essayez la <a href="/fr/">page d’accueil</a> ou la <a href="/fr/research/">liste des travaux</a>.</p>
</div>"""
    with open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8") as f:
        f.write(doc + body + foot("en"))


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
        rest = others()
        for i, p in enumerate(rest):
            summary_page(p, lang, rest[(i + 1) % len(rest)])
    not_found()
    open(os.path.join(ROOT, ".nojekyll"), "w").close()
    seo_files()
    print("built", sum(len(fs) for _, _, fs in os.walk(ROOT) if "index.html" in fs))


if __name__ == "__main__":
    main()
