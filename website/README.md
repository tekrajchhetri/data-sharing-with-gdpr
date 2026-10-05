# Data Sharing with GDPR — companion website

The source for https://datasharingbook.org/. Every page is generated from one shared layout and one stylesheet, so the header, footer, typography, and spacing are consistent everywhere. The build needs only Python 3, with no packages. Fonts (Cormorant Garamond and Inter) load from Google Fonts, with system fallbacks.

## Layout

```
website/
├── build.py            Builds every page into _site/
├── check.py            Checks local links, assets, and #fragments in _site/
├── content/
│   ├── site.json       Chapters, resource cards, authors
│   └── pages/*.json    One file per companion page (guides, figures)
├── templates/
│   ├── layout.html     Shared <head>, header, and footer for every page
│   ├── home.html       Homepage copy
│   ├── chapters.html   Chapters index copy
│   └── authors.html    Author page copy
├── static/             Copied to _site/ unchanged
│   ├── assets/         site.css, guide.js, favicon.svg
│   └── ch2/            Images used by Chapter 2 pages
└── _site/              Generated output (git-ignored, never edit)
```

## Local preview

From the repository root:

```sh
python3 website/build.py
python3 website/check.py
python3 -m http.server 4186 --bind 127.0.0.1 --directory website/_site
```

Open http://127.0.0.1:4186. Rebuild after any edit and refresh. Stop the preview with Ctrl+C.

## Update content

- **Chapters**: edit `content/site.json`. Each chapter has a `title`, a URL `slug`, a `summary`, a `topics` outline, and `resources` links. Each chapter gets its own page at `chapters/NN-slug.html`, with previous/next links, and `chapters/index.html` lists them all. Chapters with no resources show “Forthcoming”; adding a link changes the label to “Resources available”. These labels refer to companion materials, not chapter publication.
- **Resource cards**: the top-level `resources` array in `content/site.json`. Each card appears on the homepage and on its chapter's page.
- **Authors**: the `authors` array in `content/site.json`, used by the homepage and `authors.html`.
- **Companion pages**: add a JSON file to `content/pages/` with a `path` such as `ch3/my_guide.html`. Two types exist:
  - `"type": "guide"`: sections of entries, each with `text` and optional `label`, `title`, `example`, and `reference`. The page gets a contents sidebar, keyword search, and print/PDF support. Example: `gdpr-framework.json`.
  - `"type": "figure"`: one image with alt text and a download button. Put the image under `static/` at the same folder as the page path. Example: `gdpr-principles.json`.

  Then link the page from its chapter's `resources`, and optionally add a card, in `content/site.json`.
- **Design**: `static/assets/site.css`. Colours, fonts, and spacing are tokens at the top.

The illustrated cover is an original CSS/SVG concept, labelled as such on the page. Replace it when the final cover is available. Author information was reviewed against linked primary sources on 5 October 2026.

## Deployment

`.github/workflows/pages.yml` builds the site and checks links on every pull request that touches `website/`. On a push to `master` it also deploys `website/_site` to GitHub Pages. It can also be run by hand from the Actions tab.

One-time setup:

1. In the repository's **Settings → Pages**, set **Source** to **GitHub Actions**.
2. Set **Custom domain** to `datasharingbook.org`. GitHub ignores `CNAME` files for Actions deployments, so this setting is required.
3. Configure the domain's apex DNS with your provider using GitHub's current instructions. The documented IPv4 A records are `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, and `185.199.111.153`. If using `www`, point its CNAME to `tekrajchhetri.github.io`.
4. Once DNS validation and certificate provisioning finish, enable **Enforce HTTPS**.

Official references:
- [GitHub Pages custom workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Managing a custom domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site)
