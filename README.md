# Thundo portfolio

Thando Mcube’s static HTML, CSS and JavaScript portfolio for WordPress/front-end developer opportunities and freelance website work.

## Local preview

From this project folder, run:

```sh
python3 -m http.server 4173 --bind 127.0.0.1
```

Open <http://127.0.0.1:4173/>. Refresh after editing files. Stop the preview with `Ctrl+C`.

There is no framework, dependency installation or build step. The original project had no configured lint command or test suite. The portfolio is ready to publish as a static site. The connected GitHub repository is `thando-developer-works/thundo.co.za`, with `main` as its primary branch. Production publishing must be requested separately from local editing.

## What changed

| Files | Purpose |
| --- | --- |
| `index.html` | Developer introduction, selected projects and clear work, CV and contact routes. |
| `portfolio.html` | Three projects with accurate technologies and status. |
| `lhcc.html`, `interstellar-sports.html`, `woocommerce.html` | New project pages; WooCommerce is explicitly in progress. |
| `about.html`, `services.html` | Skills tied to actual projects and focused freelance services. |
| `contact.html`, `resume.html` | Direct contact details and the intentional Request CV flow. |
| `portfolio-details.html`, `service-details.html`, `starter-page.html` | Existing routes retained with truthful content in place of template examples. |
| `assets/css/site.css` | Shared responsive styling that retains Thundo’s navy/blue identity; focus indicators and reduced-motion support. |
| `scripts/check_site.py` | Dependency-free static checks for local assets, links, metadata, landmarks and headings. |
| `assets/js/site.js` | Small progressive enhancement for mobile navigation; content and navigation remain available without JavaScript. |
| `assets/img/projects/lhcc.png`, `assets/img/projects/interstellar.png` | Actual public-page screenshots captured on 9 November 2026. |

The screenshots show [Lighthouse Community Centre](https://lhcc.org.za) and [Interstellar Sports](https://www.interstellarsports.co.za). They are historical snapshots, not live embeds. The WooCommerce visual is a clearly labelled work-in-progress treatment, not a screenshot of a finished store.

## Contact and CV decisions

“Request CV” is intentional, as requested by the user. It opens an email to `info@thundo.co.za` with a CV-request subject; it does not promise a downloadable file that is absent from the project.

The contact page uses visible email, telephone and professional-profile links. Direct email replaces the previous unverified submission form. Email links depend on the visitor’s configured email application; the address remains visible for copying. No message delivery or form backend is implemented by the local preview.

## Validation

Run the repeatable local checks from this folder:

```sh
python3 scripts/check_site.py .
node --check assets/js/site.js
```

The dependency-free static checker passed all 12 HTML pages and 210 local references, checking local targets and fragments, IDs, one H1/main landmark per page, metadata and image alt attributes. JavaScript syntax also passed:

```sh
node --check assets/js/site.js
```

These checks do not establish external-link availability, email delivery or complete accessibility conformance. Browser checks passed at 320px for all 12 pages and at 768px/1440px for the main pages and a representative project page, with no horizontal overflow or broken images. The homepage was also visually reviewed at 390px. Keyboard menu opening, Escape with focus restoration, navigation to the portfolio, and CV-link access in a 667 × 320 landscape viewport passed. No browser errors or warnings were observed. Reduced-motion support is implemented in CSS; this is not a full accessibility certification or a performance audit.

The earlier template assets and attribution files remain in the repository. Updated pages load `site.css` and `site.js`; they no longer depend on the old template animation and form scripts.
