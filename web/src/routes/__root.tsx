import type { ReactNode } from 'react'
import '../index.css'
import { HeadContent, Outlet, Scripts, createRootRoute } from '@tanstack/react-router'

export const Route = createRootRoute({
  head: () => ({
    meta: [
      { charSet: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { title: 'Campus Compass | Student Dashboard' },
      { name: 'description', content: 'A clear view of your courses, assignments, scores, activities, and campus announcements.' },
    ],
  }),
  component: RootDocument,
})

function RootDocument() {
  return (
    <Document>
      <Outlet />
    </Document>
  )
}

function Document({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  )
}
