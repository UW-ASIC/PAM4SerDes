# UWASIC Docs

The documentation website: Vite + React + TypeScript, built with bun, deployed to
GitHub Pages at <https://uw-asic.github.io/PAM4SerDes/>.

## Where the pages come from

| Sidebar sections | Source | Format |
|---|---|---|
| PAM4 SerDes, Biasing, Clocking, Transmitter, Receiver | `../analog/PAM4SerDes/docs/**/*.md` and `../CHANGELOGS.md` | Markdown, the same files GitHub shows |
| Getting Started, Environment, Flows, TinyTapeout, Updating Docs | `src/content/<Section>/<Page>.ts` | Markdown inside a TypeScript string |

The site reads both at build time. To add or edit a block page, edit the `.md` file under
`analog/PAM4SerDes/docs/<Section>/`; nothing in this folder has to change. The site's own
"Updating Docs" section explains the details.

## Structure

```
docs/
├── src/
│   ├── content/              # Template pages, one folder per sidebar section
│   ├── components/           # Sidebar, MarkdownRenderer (hand-written, no Markdown library)
│   ├── utils/contentLoader.ts  # Finds the pages and pictures, resolves links
│   ├── App.tsx               # Layout and hash routing (#/Section/Page)
│   └── main.tsx              # Entry point
├── diagrams/                 # Sources of the five diagrams, and sketch.py, which redraws
│                             #   them hand-drawn into analog/PAM4SerDes/docs/img/
├── styles/                   # All CSS
├── public/                   # Copied as is (logo)
├── index.html                # HTML template
├── vite.config.ts            # Vite configuration (base path /PAM4SerDes/)
├── tsconfig.json             # TypeScript config
└── package.json              # Dependencies
```

## Quick Start

```bash
cd docs/
bun install        # only if node_modules is missing or package.json changed
bun run dev        # http://localhost:5173/PAM4SerDes/
bun run check      # checks the Markdown renderer against a few known cases
```

## Adding a template page

Create `src/content/Section-Name/Page-Name.ts`:

```typescript
export const metadata = {
  title: "Page Title",
  order: 1,
};

export const content = `
# Your Content Here

In markdown format.
`;
```

## Deploy

Push to `main`. The workflow `.github/workflows/deploy-docs.yaml` builds the site and
deploys it to GitHub Pages when `docs/**`, `analog/PAM4SerDes/docs/**` or `CHANGELOGS.md`
changed. One-time setup: repository Settings → Pages → Source: **GitHub Actions**.
