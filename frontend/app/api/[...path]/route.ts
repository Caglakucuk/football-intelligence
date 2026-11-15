import { NextRequest, NextResponse } from 'next/server'

type Context = { params: Promise<{ path: string[] }> }
export async function GET(request: NextRequest, { params }: Context) {
  const { path } = await params
  const origin = process.env.API_BASE_URL?.replace(/\/$/, '')
  if (!origin) return NextResponse.json({ error: 'API_BASE_URL is not configured.' }, { status: 503 })
  try {
    const upstream = await fetch(`${origin}/${path.map(encodeURIComponent).join('/')}${request.nextUrl.search}`, { cache: 'no-store', headers: { accept: 'application/json' }, signal: AbortSignal.timeout(12000) })
    const body = await upstream.text()
    return new NextResponse(body, { status: upstream.status, headers: { 'content-type': upstream.headers.get('content-type') ?? 'application/json' } })
  } catch {
    return NextResponse.json({ error: 'Could not connect to the football data service. Check that the FastAPI backend is available.' }, { status: 502 })
  }
}
