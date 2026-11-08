# Harmotwine landing page

English landing page for [Harmotwine](https://harmotwine.app), hosted on Cloudflare Pages. Static HTML and CSS, with a small Python build script. No JavaScript, analytics, third-party fonts or runtime dependencies.

## Local development

Requires Python 3. Node.js/npm is optional for the convenience commands.

```sh
python3 scripts/build.py
python3 -m http.server 4173 --directory dist
```

Open http://localhost:4173. Rebuild after editing source files.

- `src/`: page content, styles, illustrations and app icon assets.
- `scripts/build.py`: generates pages, redirects, security headers, sitemap and `app-ads.txt`.
- `config.json`: public domain, support address, Discord invite and store URLs.
- `dist/`: generated output, excluded from Git.

Empty store URLs show “Coming soon”. Add the actual App Store and Google Play URLs to `config.json` after release. `discordUrl` controls the community section and links. Icons and styles use content-versioned URLs to refresh browser caches.

## Cloudflare Pages

Production: https://harmotwine.app

Pages project: `harmotwine-lp`

Production branch: `main`

Build command: `python3 scripts/build.py`

Build output directory: `dist`

Project root: repository root

Cloudflare Pages is connected directly to `alexanderchmielewski/harmotwine_lp`. Every push to `main` automatically builds and deploys production. Other branches receive preview deployments; pull requests receive preview links.

The Pages fallback URL is https://harmotwine-lp.pages.dev. The custom domain `harmotwine.app` is active on this Git-connected project. The former `harmotwine` Direct Upload project has been removed. Rollbacks use previous successful deployments in `harmotwine-lp`.

Push changes to `main` to publish. For an exceptional manual deployment with an authenticated Wrangler installation:

```sh
python3 scripts/build.py
wrangler pages deploy dist --project-name harmotwine-lp --branch main
```

`npm run build`, `npm run preview` and `npm run deploy` provide equivalent shortcuts. Keep Cloudflare credentials out of this repository.

## Store and community URLs

| Purpose | URL |
| --- | --- |
| Marketing website | https://harmotwine.app/ |
| Support | https://harmotwine.app/support/ |
| Privacy policy | https://harmotwine.app/privacy/ |
| German privacy policy | https://harmotwine.app/de/privacy/ |
| Legal notice | https://harmotwine.app/impressum/ |
| Use and purchases | https://harmotwine.app/terms/ |
| AdMob app-ads.txt | https://harmotwine.app/app-ads.txt |
| Discord | https://discord.gg/MahSE8jMY |

## Content maintenance

The legal and support pages reflect the reviewed app configuration on 8 November 2026: local progress, no Harmotwine account, Google UMP consent checks, optional non-personalized rewarded test ads, one-time Pro purchase and disabled Firebase Analytics. Review these pages and store disclosures whenever the app's data processing, advertising, purchases or service providers change. Provider details were confirmed by the owner. These pages do not replace legal review or release-build verification.

The Discord community is optional. Its invite has no expiry, allows unlimited uses and opens `start-here`. The privacy pages describe community participation; private support uses `support@harmotwine.app`.

The Outfit font license is included in `src/assets/OFL-Outfit.txt`. The app icon and gameplay image are Harmotwine assets. `.gdignore` keeps this standalone website out of Godot imports when checked out inside the game workspace.

## Verification

Build the site and check generated links and assets before deployment. After deployment, verify the public pages, Discord invite, email links and narrow-screen layout. The build preserves plain support email links so Cloudflare email obfuscation does not conflict with the script-free security policy.
