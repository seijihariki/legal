# Legal pages — seijihariki apps

Static privacy policy and terms of service for the personal apps and services operated by
Victor Seiji Hariki. Served with GitHub Pages.

- `index.html` — landing page linking both documents
- `privacy.html` — privacy policy (Google OAuth consent screen: application privacy policy link)
- `terms.html` — terms of service (Google OAuth consent screen: terms of service link)
- `style.css` — shared styling, light and dark

## Public URLs

Canonical (custom domain via Cloudflare DNS-only CNAME → `seijihariki.github.io`):

```
https://legal.seijihariki.com/
https://legal.seijihariki.com/privacy.html
https://legal.seijihariki.com/terms.html
```

GitHub default hostnames still work as an alias:

```
https://seijihariki.github.io/legal/
https://seijihariki.github.io/legal/privacy.html
https://seijihariki.github.io/legal/terms.html
```

The `CNAME` file pins the custom domain. DNS: Cloudflare zone `seijihariki.com`,
`legal` CNAME → `seijihariki.github.io`, **DNS only** (not proxied) so GitHub Pages
terminates TLS with its own Let's Encrypt certificate.

## Editing

Edit the HTML directly, update the `Last updated` line in the changed page, commit and push.
GitHub Pages redeploys automatically on push to `main`. No build step.

Content must stay honest about what the Services are: personal, self-hosted, invitation-only,
non-commercial, no advertising and no data resale.
