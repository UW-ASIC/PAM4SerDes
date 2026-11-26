export const metadata = {
  title: "Block Pages",
  order: 1
}

export const content = `
# Block Pages

The project's pages (the sections **PAM4 SerDes**, **Biasing**, **Clocking**, **Transmitter** and **Receiver**) are plain Markdown files in the repository, next to the design. GitHub shows the same files when you browse the repository, and the site reads them when it is built. There is one copy of each page.

## Where the Files Are

\`\`\`
analog/PAM4SerDes/docs/
  README.md             PAM4 SerDes > Overview
  img/                  diagrams and pictures
  Biasing/README.md     Biasing > Overview
  Biasing/<block>.md    one page per block
  Clocking/...
  Transmitter/...
  Receiver/...
CHANGELOGS.md           PAM4 SerDes > Changelogs
\`\`\`

## Edit a Block Page

1. Open the block's file, for example \`analog/PAM4SerDes/docs/Clocking/tx_pll.md\`
2. Write under the heading that fits: \`## Architecture\`, \`## Topology research\` or \`## Sizing research\`
3. Commit and push. When the change reaches \`main\`, the site is rebuilt and shows it a few minutes later

## Add a Block Page

1. Create \`analog/PAM4SerDes/docs/<Section>/<block>.md\`, named after the module
2. Start it like this:

   \`\`\`
   # block_name

   One or two sentences: what the block does.

   ## Architecture

   ## Topology research

   ## Sizing research
   \`\`\`

3. Add a link to it in the section's \`README.md\`, so it can also be found on GitHub

The page appears in the sidebar on the next deploy. Nothing in \`docs/\` has to change.

## What the Site Does With a File

- The first \`# \` heading is the page's name in the sidebar
- \`README.md\` is shown as **Overview** and comes first. The other pages follow in alphabetical order of their file names
- A new folder next to \`Clocking/\` becomes a new sidebar section
- The page's address comes from the folder and file name: \`Clocking/tx_pll.md\` is \`#/Clocking/tx_pll\`. Renaming the file changes the address
- Links to other \`.md\` pages stay inside the site. Links to other files, such as a \`.va\` model, open on GitHub
- Pictures go in \`analog/PAM4SerDes/docs/img/\`

See [Markdown Syntax](/Updating-Docs/Markdown-Syntax) for what can be written in a page.

## Change a Diagram

The five hand-drawn diagrams in \`analog/PAM4SerDes/docs/img/\` (\`top\`, \`biasing\`, \`clocking\`, \`transmitter\`, \`receiver\`) are generated. Do not edit them there.

1. Edit the plain drawing in \`docs/diagrams/src/<name>.svg\`: straight boxes, lines and text, on a grid
2. Run \`python3 docs/diagrams/sketch.py\` from the repository root. It redraws the file in \`img/\` in the hand-drawn style
3. Commit both the source and the regenerated file

A picture of your own, such as a schematic for a block page, goes straight into \`img/\` and needs none of this.

## Check Before Pushing

Look at the file on GitHub, or run the site locally. See [Build & Deploy](/Updating-Docs/Build-Deploy).
`
