import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({ component: Home })

function Home() {
  return (
    <main>
      <h1>TanStack Start</h1>
      <p>React, Vite, Bun, and TanStack Start are ready.</p>
    </main>
  )
}
