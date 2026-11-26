import { useEffect, useState, useSyncExternalStore } from 'react'
import { Sidebar } from './components/Sidebar'
import { MarkdownRenderer } from './components/MarkdownRenderer'
import { sections } from './utils/contentLoader'

// The current page lives in the URL hash, `#/<Section>/<Page>` with an optional
// `#heading` after it, so a page can be linked, reloaded and reached with back/forward
// on GitHub Pages without any server configuration. Every link is a plain <a href="#/...">.
const pages = sections.flatMap(section => section.pages)

const subscribeToHash = (onChange: () => void) => {
  window.addEventListener('hashchange', onChange)
  return () => window.removeEventListener('hashchange', onChange)
}

// A hash someone typed by hand may not be valid percent-encoding.
const decode = (text: string) => {
  try {
    return decodeURIComponent(text)
  } catch {
    return text
  }
}

function App() {
  const hash = useSyncExternalStore(subscribeToHash, () => window.location.hash)
  const [path = '', heading = ''] = decode(hash).replace(/^#\/?/, '').split('#')
  // No hash: the first page, which is the project overview.
  const currentPage = path ? pages.find(page => page.path === path) : pages[0]

  // The sidebar is off-screen on phones until the menu button opens it.
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    setMenuOpen(false)
    const target = heading && document.getElementById(heading)
    if (!target) {
      window.scrollTo(0, 0)
      return
    }
    // A picture above the heading pushes it down when it finishes loading: scroll again then.
    const scroll = () => target.scrollIntoView()
    const loading = Array.from(document.images).filter(image => !image.complete)
    scroll()
    loading.forEach(image => image.addEventListener('load', scroll))
    return () => loading.forEach(image => image.removeEventListener('load', scroll))
  }, [path, heading])

  return (
    <div className="app">
      <button
        className="menu-toggle"
        aria-label="Toggle navigation"
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen(open => !open)}
      >
        ☰
      </button>

      <Sidebar sections={sections} currentPath={currentPage?.path ?? ''} open={menuOpen} />

      <main className="content">
        {currentPage ? (
          <article className="article">
            <MarkdownRenderer page={currentPage} />
          </article>
        ) : (
          <div className="empty-state">
            <p>Page not found. Select a page from the sidebar.</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App
