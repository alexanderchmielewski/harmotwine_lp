#!/usr/bin/env python3
"""Build a dependency-free static Cloudflare Pages site from reviewed sources."""
from pathlib import Path
from html import escape
import json
import hashlib
import re
import shutil
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SRC, OUT = ROOT / 'src', ROOT / 'dist'
cfg = json.loads((ROOT / 'config.json').read_text())
url = cfg['url'].rstrip('/')
assert urlsplit(url).scheme == 'https' and urlsplit(url).netloc
assert re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', cfg['email'])
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
shutil.copytree(SRC / 'assets', OUT / 'assets')
shutil.copy2(SRC / 'style.css', OUT / 'style.css')
icon_version = hashlib.sha256((SRC / 'assets/app-icon.png').read_bytes()).hexdigest()[:12]
style_version = hashlib.sha256((SRC / 'style.css').read_bytes()).hexdigest()[:12]
# Version URLs so browsers replace cached assets after deployment.

stores = []
for key, label in [('appStoreUrl', 'App Store'), ('playStoreUrl', 'Google Play')]:
    link = cfg[key]
    if link:
        assert urlsplit(link).scheme == 'https'
        stores.append(f'<a class="button" href="{escape(link, quote=True)}">{label} ↗</a>')
    else:
        stores.append(f'<span class="store-pending"><small>COMING SOON TO</small>{label}</span>')
discord_url = cfg.get('discordUrl', '')
community = ''
community_nav = ''
if discord_url:
    invite = urlsplit(discord_url)
    assert invite.scheme == 'https' and invite.netloc in ('discord.gg', 'discord.com')
    assert invite.path.strip('/') and (invite.netloc == 'discord.gg' or invite.path.startswith('/invite/'))
    safe_invite = escape(discord_url, quote=True)
    community_nav = '<a href="/#community">Community</a>'
    community = f'''<section class="section wrap community" id="community"><div><p class="eyebrow">A little better, together</p><h2>Find your people.<br>Help shape the game.</h2><p class="section-intro">Join our quiet corner on Discord. Share an idea, support suggestions you'd love to see, ask for a hint or tell us what could feel better. New players and quiet observers are equally welcome.</p></div><div class="community-invite"><img src="/assets/brand-icon.png?v={icon_version}" width="72" height="72" alt=""><h3>The Harmotwine community</h3><p>Player ideas · Friendly help · Game updates</p><a class="button" href="{safe_invite}">Join us on Discord <span aria-hidden="true">↗</span></a><p class="note">Discord is optional. For private support, <a href="mailto:{escape(cfg['email'], quote=True)}">email us</a>.</p></div></section>'''
replacements = {'URL': escape(url, quote=True), 'EMAIL': escape(cfg['email'], quote=True),
                'HERO': (SRC / 'hero.svg').read_text(), 'STORES': ''.join(stores), 'COMMUNITY': community, 'DISCORD': escape(discord_url, quote=True)}
pages = [
    ('index.html', '', 'Harmotwine – Move light. Find your sound.', 'A quiet puzzle of light and sound. Discover 72 puzzles in six sound worlds. Coming soon to iOS and Android.', 'en'),
    ('privacy-en.html', 'privacy', 'Privacy policy · Harmotwine', 'Privacy information for the Harmotwine app and website.', 'en'),
    ('privacy.html', 'de/privacy', 'Datenschutzerklärung · Harmotwine', 'Datenschutz für Harmotwine: Spielstände, Werbung, Käufe, Website und deine Rechte.', 'de'),
    ('impressum.html', 'impressum', 'Legal notice · Harmotwine', 'Service provider and contact information for Harmotwine.', 'en'),
    ('support.html', 'support', 'Support · Harmotwine', 'Help with Harmotwine, purchases, progress and privacy.', 'en'),
    ('terms.html', 'terms', 'Use & purchases · Harmotwine', 'Information about free levels, optional videos and Harmotwine Pro.', 'en'),
]
for source, route, title, description, lang in pages:
    body = (SRC / source).read_text()
    for key, value in replacements.items():
        body = body.replace('{{' + key + '}}', value)
    assert '{{' not in body, source
    english = lang == 'en'
    links = [('Support', '/support'), ('Privacy policy' if english else 'Datenschutz', '/privacy' if english else '/de/privacy'), ('Use & purchases', '/terms'), ('Legal notice', '/impressum')]
    if discord_url:
        links.append(('Discord', discord_url))
    footer = ''.join(f'<a href="{escape(href, quote=True)}">{label}</a>' for label, href in links)
    canonical = url + ('/' + route if route else '/')
    main_class = 'wrap legal' if route else ''
    html = f'''<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="theme-color" content="#090e1d"><title>{escape(title)}</title><meta name="description" content="{escape(description, quote=True)}"><link rel="canonical" href="{canonical}"><meta property="og:type" content="website"><meta property="og:site_name" content="Harmotwine"><meta property="og:title" content="{escape(title, quote=True)}"><meta property="og:description" content="{escape(description, quote=True)}"><meta property="og:url" content="{canonical}"><meta property="og:image" content="{url}/assets/app-icon.png?v={icon_version}"><link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png?v={icon_version}"><link rel="apple-touch-icon" sizes="180x180" href="/assets/apple-touch-icon.png?v={icon_version}"><link rel="stylesheet" href="/style.css?v={style_version}"></head><body><a class="skip" href="#main">{'Skip to content' if english else 'Zum Inhalt'}</a><header><nav class="wrap" aria-label="{'Main navigation' if english else 'Hauptnavigation'}"><a class="brand" href="/"><img src="/assets/brand-icon.png?v={icon_version}" width="38" height="38" alt="">HARMOTWINE</a><div class="navlinks">{community_nav}<a class="desktop" href="/#discover">The game</a><a href="/support">Support</a><a href="/#download">{'Coming soon' if english else 'Demnächst'} ↗</a></div></nav></header><main id="main" class="{main_class}">{body}</main><footer><div class="wrap footer-row"><span>© 2026 Harmotwine · Alexander Linack</span><div class="footer-links">{footer}</div></div></footer></body></html>'''
    # Keep public support addresses usable with script-src 'none'.
    html = html.replace('<body>', '<body><!--email_off-->').replace('</body>', '<!--/email_off--></body>')
    dest = OUT / route / 'index.html'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html)
(OUT / '404.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Page not found · Harmotwine</title><link rel="stylesheet" href="/style.css"><main class="wrap legal"><h1>Nothing resonates here yet.</h1><p>We could not find this page.</p><a href="/">Back to the game</a> · <a href="/support">Support</a></main></html>')
(OUT / 'app-ads.txt').write_text('google.com, pub-3516300472749804, DIRECT, f08c47fec0942fa0\n')
(OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {url}/sitemap.xml\n')
(OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{url}/{route}</loc></url>' for _, route, *_ in pages) + '</urlset>')
(OUT / '_redirects').write_text('/datenschutz /de/privacy 301\n/en/privacy /privacy 301\n/imprint /impressum 301\n/legal /impressum 301\n/privacy.html /privacy 301\n/support.html /support 301\n/terms.html /terms 301\n/imprint.html /impressum 301\n')
(OUT / '_headers').write_text("""/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  X-Frame-Options: DENY
  Permissions-Policy: camera=(), microphone=(), geolocation=()
  Content-Security-Policy: default-src 'self'; script-src 'none'; style-src 'self'; img-src 'self'; font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'
  Strict-Transport-Security: max-age=31536000
/app-ads.txt
  Content-Type: text/plain; charset=utf-8
""")
print(f'Built {len(pages)} pages in {OUT}')
