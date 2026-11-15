import type { Metadata, Viewport } from 'next'
import './globals.css'
export const metadata: Metadata = { title: 'Football Intelligence | Süper Lig 2024/25', description: 'Historical Turkish Süper Lig standings, match results and team performance analytics.' }
export const viewport: Viewport = { themeColor: '#080f1c', colorScheme: 'dark' }
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html> }
