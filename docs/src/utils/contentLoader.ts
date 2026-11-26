export interface PageMetadata {
  title: string
  order: number
}

export interface Page {
  id: string
  /** Route of the page: `<Section>/<Page>`, shown in the URL as `#/<Section>/<Page>`. */
  path: string
  metadata: PageMetadata
  content: string
  /** Repo-relative path of the Markdown file (project pages only). Relative links resolve against it. */
  source?: string
}

export interface Section {
  id: string
  title: string
  pages: Page[]
}

const REPO_URL = 'https://github.com/UW-ASIC/PAM4SerDes/blob/main/'

// ---------------------------------------------------------------------------
// Sources. Vite resolves these globs at build time; a glob that matches nothing
// (CHANGELOGS.md before it exists, an empty section folder) is simply empty.
// ---------------------------------------------------------------------------

// Template pages: docs/src/content/<Section>/<Page>.ts
const templateModules = import.meta.glob<{ metadata: PageMetadata; content: string }>(
  '../content/**/*.ts',
  { eager: true },
)

// Project pages: the Markdown files that live next to the design, plus the changelog.
const PROJECT_DOCS = 'analog/PAM4SerDes/docs/'
const projectMarkdown = import.meta.glob<string>(
  ['../../../analog/PAM4SerDes/docs/**/*.md', '../../../CHANGELOGS.md'],
  { eager: true, query: '?raw', import: 'default' },
)

// Pictures the Markdown pages can show, keyed by file name ("top.svg").
const imageModules = import.meta.glob<string>(
  '../../../analog/PAM4SerDes/docs/img/*.{svg,png,jpg,jpeg,gif,webp}',
  { eager: true, query: '?url', import: 'default' },
)
const images = new Map(
  Object.entries(imageModules).map(([file, url]) => [file.split('/').pop()!, url]),
)

// ---------------------------------------------------------------------------
// Project pages
// ---------------------------------------------------------------------------

// Sidebar order of the project sections. A docs folder not listed here still gets a
// section, after these.
const ROOT_SECTION = 'PAM4-SerDes'
const PROJECT_SECTIONS = [ROOT_SECTION, 'Biasing', 'Clocking', 'Transmitter', 'Receiver']
// Page order inside the root section; inside a section folder README.md comes first.
// Everything else follows alphabetically, and the changelog closes the root section.
const FIRST_PAGES = ['README', 'status']
const LAST_PAGE = 'CHANGELOGS'

const sectionTitle = (id: string) =>
  id.split('-').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')

/** Text of the first `# ` heading outside a code block, without inline markup. */
function firstHeading(markdown: string): string | undefined {
  const prose = markdown.replace(/^\s*```[\s\S]*?^\s*```/gm, '')
  return prose.match(/^# +(.+)$/m)?.[1].replace(/[`*]/g, '').trim()
}

function loadProjectPages(): Section[] {
  const sections = new Map<string, Section>()

  for (const [file, content] of Object.entries(projectMarkdown)) {
    // '../../../analog/PAM4SerDes/docs/Clocking/tx_pll.md' -> section 'Clocking', name 'tx_pll'
    // '../../../analog/PAM4SerDes/docs/status.md'          -> root section, name 'status'
    // '../../../CHANGELOGS.md'                             -> root section, name 'CHANGELOGS'
    const source = file.replace(/^(\.\.\/)+/, '')
    const parts = source.replace(PROJECT_DOCS, '').replace(/\.md$/, '').split('/')
    const sectionId = parts.length > 1 ? parts.shift()! : ROOT_SECTION
    const name = parts.join('/')
    const isReadme = name === 'README'
    const id = isReadme ? 'Overview' : name

    if (!sections.has(sectionId)) {
      sections.set(sectionId, { id: sectionId, title: sectionTitle(sectionId), pages: [] })
    }
    const first = FIRST_PAGES.indexOf(name)
    sections.get(sectionId)!.pages.push({
      id,
      path: `${sectionId}/${id}`,
      source,
      content,
      metadata: {
        title: isReadme ? 'Overview' : firstHeading(content) ?? name,
        order: first !== -1 ? first : name === LAST_PAGE ? FIRST_PAGES.length + 1 : FIRST_PAGES.length,
      },
    })
  }

  const rank = (id: string) => {
    const index = PROJECT_SECTIONS.indexOf(id)
    return index === -1 ? PROJECT_SECTIONS.length : index
  }
  sections.forEach(section => {
    section.pages.sort((a, b) => a.metadata.order - b.metadata.order || a.id.localeCompare(b.id))
  })
  return Array.from(sections.values()).sort((a, b) => rank(a.id) - rank(b.id) || a.id.localeCompare(b.id))
}

// ---------------------------------------------------------------------------
// Template pages
// ---------------------------------------------------------------------------

function loadTemplatePages(): Section[] {
  const sections = new Map<string, Section>()

  for (const [file, module] of Object.entries(templateModules)) {
    // Example: ../content/Getting-Started/Introduction.ts
    const match = file.match(/\/content\/([^/]+)\/([^/]+)\.ts$/)
    if (!match) continue
    const [, sectionId, pageId] = match

    if (!sections.has(sectionId)) {
      sections.set(sectionId, { id: sectionId, title: sectionTitle(sectionId), pages: [] })
    }
    sections.get(sectionId)!.pages.push({
      id: pageId,
      path: `${sectionId}/${pageId}`,
      metadata: module.metadata,
      content: module.content,
    })
  }

  sections.forEach(section => {
    section.pages.sort((a, b) => a.metadata.order - b.metadata.order)
  })
  return Array.from(sections.values()).sort((a, b) => {
    // Always put Getting-Started first, the others alphabetically
    if (a.id === 'Getting-Started') return -1
    if (b.id === 'Getting-Started') return 1
    return a.id.localeCompare(b.id)
  })
}

/** Every section of the site: the project's own pages first, then the template pages. */
export const sections: Section[] = [...loadProjectPages(), ...loadTemplatePages()]

const routeBySource = new Map(
  sections.flatMap(section => section.pages).flatMap(page => (page.source ? [[page.source, page.path] as const] : [])),
)

// ---------------------------------------------------------------------------
// Links and images inside a page
// ---------------------------------------------------------------------------

/**
 * Turns a Markdown link target into the href the site should use.
 *  - `https://...`, `mailto:...`       unchanged
 *  - `#heading`                        a heading of the same page
 *  - `/Section/Page`                   another page of the site (template pages)
 *  - `tx_pll.md`, `../Clocking/`       relative to the Markdown file: the page it names, if the
 *                                      site loaded one, otherwise the file on GitHub
 */
export function resolveLink(href: string, page: Page): string {
  if (/^[a-z][a-z0-9+.-]*:/i.test(href)) return href
  if (href.startsWith('#')) return `#/${page.path}${href}`
  if (href.startsWith('/')) return `#${href}`
  if (!page.source) return href

  const target = new URL(href, `http://repo/${page.source}`)
  const file = decodeURIComponent(target.pathname.slice(1))
  const route = routeBySource.get(file) ?? routeBySource.get(file.replace(/\/?$/, '/README.md'))
  return route ? `#/${route}${target.hash}` : `${REPO_URL}${file}${target.hash}`
}

/** URL of a picture. Files in `analog/PAM4SerDes/docs/img/` are found by file name alone. */
export function resolveImage(src: string): string | undefined {
  return /^https?:/i.test(src) ? src : images.get(src.split(/[/\\]/).pop()!)
}
