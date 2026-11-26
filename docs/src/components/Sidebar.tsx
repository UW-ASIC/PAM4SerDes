import { useEffect, useState } from 'react'
import { Section } from '../utils/contentLoader'

interface SidebarProps {
  sections: Section[]
  currentPath: string
  /** Phones only: whether the menu button has slid the sidebar in. */
  open: boolean
}

export function Sidebar({ sections, currentPath, open }: SidebarProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set())

  // Keep the section of the page being read open, also after a link or a reload.
  const currentSection = currentPath.split('/')[0]
  useEffect(() => {
    setExpandedSections(prev => new Set(prev).add(currentSection))
  }, [currentSection])

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev)
      if (next.has(sectionId)) {
        next.delete(sectionId)
      } else {
        next.add(sectionId)
      }
      return next
    })
  }

  return (
    <aside className={`sidebar ${open ? 'open' : ''}`}>
      <div className="sidebar-header">
        <h1 className="logo">
          {/* BASE_URL: the site is served from /PAM4SerDes/, not from the domain root */}
          <img src={`${import.meta.env.BASE_URL}logo.png`} alt="UWASIC Logo" />
          <span className="logo-text">UWASIC Docs</span>
        </h1>
      </div>

      <nav className="sidebar-nav">
        {sections.map(section => (
          <div key={section.id} className="nav-section">
            <button
              className="section-header"
              aria-expanded={expandedSections.has(section.id)}
              onClick={() => toggleSection(section.id)}
            >
              <span className={`chevron ${expandedSections.has(section.id) ? 'expanded' : ''}`}>
                ›
              </span>
              <span className="section-title">{section.title}</span>
            </button>

            {expandedSections.has(section.id) && (
              <ul className="page-list">
                {section.pages.map(page => (
                  <li key={page.path}>
                    <a
                      className={`page-link ${currentPath === page.path ? 'active' : ''}`}
                      href={`#/${page.path}`}
                    >
                      {page.metadata.title}
                    </a>
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}
      </nav>
    </aside>
  )
}
