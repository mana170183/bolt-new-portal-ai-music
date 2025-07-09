import { Metadata } from 'next'
import '../index.css'

export const metadata: Metadata = {
  title: 'Portal AI Music - Generate AI Music Instantly',
  description: 'Create royalty-free AI music with Portal AI Music. Generate custom tracks for videos, podcasts, and content creation using advanced AI technology.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        {children}
      </body>
    </html>
  )
}
