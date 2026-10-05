"""Build the book website into website/_site/. No dependencies.

All pages share one layout (header, footer, stylesheet), so the site stays consistent:
- content/site.json      chapters (one page each under chapters/), resource cards, authors
- content/pages/*.json   companion pages ("guide" or "figure" type), one file per page
- templates/             shared layout and page copy
- static/                stylesheet, scripts, images; copied to the output as-is
"""
import hashlib
import shutil
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / '_site'
TEMPLATES = ROOT / 'templates'
data = json.loads((ROOT / 'content/site.json').read_text())

# Start from a clean output folder so removed pages never linger.
shutil.rmtree(SITE, ignore_errors=True)
shutil.copytree(ROOT / 'static', SITE)


def e(value):
    return escape(str(value), quote=True)


def fill(template, **values):
    for key, val in values.items():
        template = template.replace('{{' + key + '}}', str(val))
    return template


def is_external(url):
    return url.startswith(('http:', 'https:', '//'))


MARK = ('<svg class="brand-mark" viewBox="0 0 40 40" fill="none" aria-hidden="true">'
        '<circle cx="20" cy="20" r="19.25" fill="#14231f"/>'
        '<path d="M10 13.5c3.6-.9 7 0 10 2.2 3-2.2 6.4-3.1 10-2.2v13c-3.6-.9-7 0-10 2.2-3-2.2-6.4-3.1-10-2.2z" stroke="#c6a66c" stroke-width="1.2" stroke-linejoin="round"/>'
        '<path d="M20 15.7v13" stroke="#c6a66c" stroke-width="1.2"/></svg>')
NAV = [('The book', 'index.html', 'home'), ('Chapters', 'chapters/index.html', 'chapters'),
       ('Resources', 'index.html#resources', 'resource'), ('Authors', 'authors.html', 'authors')]


def render(path, title, description, body, section=None, scripts=''):
    """Wrap a page body in the shared layout and write it to book_site/<path>."""
    root = '../' * path.count('/')
    nav = ''.join(f'<a href="{root}{href}"{" aria-current=page" if key and key == section else ""}>{label}</a>'
                  for label, href, key in NAV)
    page = fill((TEMPLATES / 'layout.html').read_text(), TITLE=e(title), DESCRIPTION=e(description),
                CANONICAL='' if path == 'index.html' else path, ROOT=root, MARK=MARK, NAV=nav,
                BODY=body, SCRIPTS=scripts)
    # Version local stylesheets and scripts by content so browsers never reuse stale files.
    def version(match):
        attr, url = match.groups()
        if is_external(url):
            return match.group(0)
        digest = hashlib.sha256((SITE / path).parent.joinpath(url).resolve().read_bytes()).hexdigest()[:10]
        return f'{attr}="{url}?v={digest}"'
    page = re.sub(r'(href|src)="([^"?#]+\.(?:css|js))"', version, page)
    (SITE / path).parent.mkdir(parents=True, exist_ok=True)
    (SITE / path).write_text(page)
    print(f'Built _site/{path}')


def link(item, root=''):
    url = item['url'] if is_external(item['url']) else root + item['url']
    mark = '↗' if is_external(item['url']) else '→'
    return f'<a href="{e(url)}">{e(item["label"])} <span aria-hidden="true">{mark}</span></a>'


CHAPTERS = data['chapters']


def chapter_url(n, root=''):
    return f'{root}chapters/{n:02}-{CHAPTERS[n - 1]["slug"]}.html'


def chapter_rows(root=''):
    """The chapter list shared by the homepage and the chapters index."""
    rows = ''
    for n, ch in enumerate(CHAPTERS, 1):
        live = bool(ch['resources'])
        rows += (f'<a class="chapter-row" href="{chapter_url(n, root)}"><span class="chapter-num">{n:02}</span>'
                 f'<span class="chapter-text"><span class="chapter-title">{e(ch["title"])}</span><span class="chapter-sum">{e(ch["summary"])}</span></span>'
                 f'<span class="status{" live" if live else ""}">{"Resources available" if live else "Forthcoming"}</span>'
                 f'<span class="row-arrow" aria-hidden="true">→</span></a>')
    return rows


def resource_cards(items, root=''):
    cards = ''
    for n, r in enumerate(items, 1):
        external = is_external(r['url'])
        url = r['url'] if external else root + r['url']
        cards += (f'<a class="card" href="{e(url)}"><div class="card-meta"><span class="card-type">Chapter {e(r["chapter"])} · {e(r["type"])}</span>'
                  f'<span class="card-num" aria-hidden="true">{n:02}</span></div><h3 class="h3">{e(r["title"])}</h3><p>{e(r["description"])}</p>'
                  f'<div class="card-foot"><span>{e(r["action"])}</span><span aria-hidden="true">{"↗" if external else "→"}</span></div></a>')
    return cards


# ---------- Homepage ----------
authors = ''.join(f'<a class="author-card" href="authors.html#{e(a["id"])}"><span class="monogram" aria-hidden="true">{e(a["initials"])}</span>'
                  f'<h3>{e(a["name"])}</h3><p>{e(a["affiliation"])}</p></a>' for a in data['authors'])

render('index.html', 'Data Sharing with GDPR: The Book & Companion Resources',
       'The companion website for Data Sharing with GDPR: a guide to building secure, ethical, and legally compliant systems. '
       'Explore the chapter outline, authors, and available resources.',
       fill((TEMPLATES / 'home.html').read_text(), CHAPTERS=chapter_rows(), RESOURCES=resource_cards(data['resources']), AUTHORS=authors), 'home')

# ---------- Authors ----------
profiles = ''
for a in data['authors']:
    bio = ''.join(f'<p>{e(p)}</p>' for p in a['bio'])
    tags = ''.join(f'<span class="tag">{e(t)}</span>' for t in a['topics'])
    sources = ''.join(f'<a class="arrow-link" href="{e(s["url"])}">{e(s["label"])} <span aria-hidden="true">↗</span></a>' for s in a['sources'])
    profiles += (f'<article class="profile" id="{e(a["id"])}" aria-labelledby="name-{e(a["id"])}">'
                 f'<div><span class="monogram" aria-hidden="true">{e(a["initials"])}</span><h2 id="name-{e(a["id"])}">{e(a["name"])}</h2>'
                 f'<p class="profile-role">{e(a["role"])}</p><p class="profile-aff">{e(a["affiliation"])}</p></div>'
                 f'<div class="profile-bio">{bio}<div class="profile-meta"><div><span class="small-caps">Research areas</span><div class="tags">{tags}</div></div>'
                 f'<div class="sources">{sources}</div></div></div></article>')
institutions = {part.strip() for a in data['authors'] for part in a['affiliation'].split('·')}
render('authors.html', 'The Authors · Data Sharing with GDPR',
       'Meet the five authors of Data Sharing with GDPR: research backgrounds, affiliations, and links to personal and institutional profiles.',
       fill((TEMPLATES / 'authors.html').read_text(), PROFILES=profiles, COUNT=len(data['authors']), INSTITUTIONS=len(institutions)), 'authors')

# ---------- Chapters ----------
live_count = sum(bool(c['resources']) for c in CHAPTERS)
render('chapters/index.html', 'Chapters · Data Sharing with GDPR',
       'The nine chapters of Data Sharing with GDPR, from privacy fundamentals to secure, interoperable data sharing systems.',
       fill((TEMPLATES / 'chapters.html').read_text(), CHAPTERS=chapter_rows('../'), COUNT=len(CHAPTERS), LIVE=live_count), 'chapters')

for n, ch in enumerate(CHAPTERS, 1):
    num = f'{n:02}'
    cards = [r for r in data['resources'] if r['chapter'] == num]
    carded = {r['url'] for r in cards}
    extra = [r for r in ch['resources'] if r['url'] not in carded]
    if cards or extra:
        resources = f'<div class="card-grid">{resource_cards(cards, "../")}</div>' if cards else ''
        if extra:
            resources += f'<div class="chapter-links">{"".join(link(r, "../") for r in extra)}</div>'
    else:
        resources = ('<div class="empty-panel"><span class="pulse" aria-hidden="true"></span><div><strong>Companion materials are forthcoming.</strong>'
                     '<p>Guides, notebooks, and examples for this chapter will appear here as the book develops.</p></div></div>')
    topics = ''.join(f'<li><span>{i:02}</span>{e(t)}</li>' for i, t in enumerate(ch['topics'], 1))
    prev_link = (f'<a class="pager-link" href="{chapter_url(n - 1, "../").removeprefix("../chapters/")}"><span class="small-caps">← Chapter {n - 1:02}</span>'
                 f'<b>{e(CHAPTERS[n - 2]["title"])}</b></a>' if n > 1 else '<span></span>')
    next_link = (f'<a class="pager-link next" href="{chapter_url(n + 1, "../").removeprefix("../chapters/")}"><span class="small-caps">Chapter {n + 1:02} →</span>'
                 f'<b>{e(CHAPTERS[n]["title"])}</b></a>' if n < len(CHAPTERS) else '<span></span>')
    status = 'Resources available' if ch['resources'] else 'Forthcoming'
    body = (f'<section class="page-hero"><div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="../index.html">The book</a>'
            f'<span aria-hidden="true">/</span><a href="index.html">Chapters</a><span aria-hidden="true">/</span><span>Chapter {num}</span></nav>'
            f'<div class="page-hero-grid"><div><span class="eyebrow">Chapter {num} of {len(CHAPTERS):02}</span>'
            f'<h1 class="page-title">{e(ch["title"])}</h1><p class="lede">{e(ch["summary"])}</p></div>'
            f'<div class="page-facts"><div><span class="small-caps">Companion materials</span><b>{status}</b></div>'
            f'<div><span class="small-caps">Resources</span><b>{len(ch["resources"]) or "—"}</b></div></div></div></div></section>'
            f'<section class="section section-flush chapter-top"><div class="wrap chapter-layout"><div><span class="eyebrow">In this chapter</span>'
            f'<h2 class="h2 chapter-h2">What it <em>covers</em></h2><p class="footnote small-caps">Full chapter text is not published on this site.</p></div>'
            f'<ol class="topic-list">{topics}</ol></div></section>'
            f'<section class="section section-flush"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Companion materials</span>'
            f'<h2 class="h2">Resources for <em>chapter {n}</em></h2></div></div>{resources}</div></section>'
            f'<div class="wrap"><nav class="pager" aria-label="Chapter navigation">{prev_link}{next_link}</nav></div>')
    render(f'chapters/{num}-{ch["slug"]}.html', f'Chapter {n}: {ch["title"]} · Data Sharing with GDPR', ch['summary'], body, 'chapters')

# ---------- Companion pages ----------
SEARCH_ICON = ('<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><circle cx="7" cy="7" r="5.25" stroke="currentColor" stroke-width="1.3"/>'
               '<path d="m11 11 3.5 3.5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/></svg>')


def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')


def page_hero(p, root, facts='', actions=''):
    n = int(p['chapter'])
    url = chapter_url(n, root)
    return (f'<section class="page-hero"><div class="wrap"><nav class="crumbs" aria-label="Breadcrumb"><a href="{root}index.html">The book</a>'
            f'<span aria-hidden="true">/</span><a href="{url}">Chapter {e(p["chapter"])}</a><span aria-hidden="true">/</span><span>{e(p["title"])}</span></nav>'
            f'<div class="page-hero-grid"><div><span class="eyebrow">Chapter {e(p["chapter"])} · {e(p["kicker"])}</span>'
            f'<h1 class="page-title">{e(p["title"])}</h1><p class="lede">{e(p["lede"])}</p>{actions}</div>'
            f'<div class="page-facts"><div><span class="small-caps">Chapter {e(p["chapter"])}</span><a class="fact-link" href="{url}">{e(CHAPTERS[n - 1]["title"])}</a></div>{facts}</div></div></div></section>')


def guide(p, root):
    toc, body = '', ''
    for i, s in enumerate(p['sections'], 1):
        sid = slug(s['title'])
        toc += f'<li><a href="#{sid}">{e(s["title"])}</a></li>'
        compact = all('label' in it and 'example' not in it for it in s['items'])
        items = ''
        for it in s['items']:
            items += '<div class="g-item">'
            if it.get('label'): items += f'<div class="g-label">{e(it["label"])}</div>'
            if it.get('title'): items += f'<h3>{e(it["title"])}</h3>'
            items += f'<p>{e(it["text"])}</p>'
            if it.get('example'): items += f'<div class="example"><b>Example</b>{e(it["example"])}</div>'
            if it.get('reference'): items += f'<span class="ref">{e(it["reference"])}</span>'
            items += '</div>'
        body += (f'<section class="g-section" id="{sid}" aria-labelledby="{sid}-h"><div class="g-head"><span class="g-num">{i:02}</span>'
                 f'<h2 id="{sid}-h">{e(s["title"])}</h2></div><div class="g-items{" compact" if compact else ""}">{items}</div></section>')
    entries = sum(len(s['items']) for s in p['sections'])
    facts = f'<div><span class="small-caps">Contents</span><b>{len(p["sections"])} sections · {entries} entries</b></div>'
    actions = ('<div class="actions"><button class="button ghost" type="button" onclick="window.print()">Print or save as PDF</button></div>')
    return (page_hero(p, root, facts, actions) +
            f'<div class="wrap guide"><aside class="guide-aside"><div class="search">{SEARCH_ICON}'
            f'<input id="guide-search" type="search" placeholder="{e(p.get("search", "Search this guide…"))}" aria-label="Search this guide" aria-describedby="search-count"></div>'
            f'<p id="search-count" class="small-caps" aria-live="polite"></p>'
            f'<nav class="toc" aria-label="Contents"><span class="small-caps">Contents</span><ol>{toc}</ol></nav></aside>'
            f'<div class="guide-main">{body}<p id="no-results" class="no-results" hidden>No entries match your search.</p></div></div>')


def figure(p, root):
    actions = f'<div class="actions"><a class="button ghost" href="{e(p["image"])}" download>{e(p["download"])} <span aria-hidden="true">↓</span></a></div>'
    return (page_hero(p, root, '', actions) +
            f'<div class="wrap figure-wrap"><figure class="figure"><img src="{e(p["image"])}" alt="{e(p["alt"])}">'
            f'<figcaption>{e(p["title"])} · Chapter {e(p["chapter"])} companion figure</figcaption></figure></div>')


for source in sorted((ROOT / 'content/pages').glob('*.json')):
    p = json.loads(source.read_text())
    root = '../' * p['path'].count('/')
    if p['type'] == 'guide':
        render(p['path'], f'{p["title"]} · Data Sharing with GDPR', p['lede'], guide(p, root), 'resource',
               f'<script src="{root}assets/guide.js" defer></script>')
    elif p['type'] == 'figure':
        render(p['path'], f'{p["title"]} · Data Sharing with GDPR', p['lede'], figure(p, root), 'resource')
    else:
        raise SystemExit(f'{source.name}: unknown page type {p["type"]!r}')
