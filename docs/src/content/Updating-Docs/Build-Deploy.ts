export const metadata = {
  title: "Build & Deploy",
  order: 4
}

export const content = `
# Build & Deploy

## Local Development

\`\`\`bash
cd docs/
bun run dev
\`\`\`

Visit \`http://localhost:5173/PAM4SerDes/\` to see your changes live. This works for the Markdown pages in \`analog/PAM4SerDes/docs/\` too.

Run \`bun install\` first if \`docs/node_modules\` is missing or \`package.json\` changed.

## Build for Production

\`\`\`bash
cd docs/
bun run build
\`\`\`

Checks the types, then writes the site to \`docs/dist/\`. Use it to check that the site builds. The deploy makes its own build and does not use this copy, so there is no need to commit \`docs/dist/\`.

## Deploy to GitHub Pages

### Setup (One Time)

1. Go to the GitHub repo **Settings** → **Pages**
2. Under **Build and deployment**, set **Source** to **GitHub Actions**

There is no branch or folder to choose. Until this is set, the workflow fails at its deploy step.

### Auto-Deploy

A push to \`main\` starts the workflow when it changes any of:

- \`docs/**\` (the site)
- \`analog/PAM4SerDes/docs/**\` (the block pages and diagrams)
- \`CHANGELOGS.md\`

It can also be started by hand: **Actions** → **Deploy Docs** → **Run workflow**.

The workflow:

1. Checks out the repository and installs bun
2. Runs \`bun install\` and \`bun run build\` in \`docs/\`
3. Uploads \`docs/dist\` as a Pages artifact
4. Deploys that artifact to GitHub Pages

Nothing is committed back to the repository.

The site: \`https://uw-asic.github.io/PAM4SerDes/\`

## Workflow File

Located at \`.github/workflows/deploy-docs.yaml\`

## Site Address

The site is served under the repository name, so \`base\` in \`docs/vite.config.ts\` is \`/PAM4SerDes/\`. If the repository is renamed, change it to match, or the page loads blank.

Each page has its own address, for example \`https://uw-asic.github.io/PAM4SerDes/#/Clocking/tx_pll\`. Copy it from the address bar to link to a page.

## Troubleshooting

**Build fails?**
- Run \`bun run build\` locally first
- Check syntax in the \`.ts\` files
- Check the GitHub Actions logs

**Deploy step fails?**
- Check that Pages is set to **GitHub Actions** (see Setup)

**Blank page, or the logo is missing?**
- Check that \`base\` in \`docs/vite.config.ts\` matches the repository name

**Pages not updating?**
- Wait 1-2 minutes after the push
- Check that the workflow ran in the **Actions** tab: it only starts for the paths listed above
- Clear browser cache
`
