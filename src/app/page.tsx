import dynamic from 'next/dynamic'

// Disable SSR for the App component to prevent Prisma initialization during build
const App = dynamic(() => import('../App'), {
  ssr: false,
  loading: () => <div className="min-h-screen flex items-center justify-center">Loading...</div>
})

export default function HomePage() {
  return <App />
}
