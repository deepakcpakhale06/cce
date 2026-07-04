import type { AnalyzeRequest, CalculatorLinkRequest, CalculatorLinkResponse, Estimate, PricingRequest } from '../types'

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    const contentType = response.headers.get('content-type') ?? ''
    if (contentType.includes('application/json')) {
      const payload = await response.json().catch(() => null)
      const message = payload?.detail || payload?.error || payload?.message
      throw new Error(message || 'API request failed')
    }

    const text = await response.text()
    throw new Error(text || 'API request failed')
  }

  return response.json() as Promise<T>
}

export async function analyzeSetup(request: AnalyzeRequest): Promise<Estimate> {
  return post('/analyze', request)
}

export async function fetchPrices(request: PricingRequest): Promise<Estimate> {
  return post('/pricing', request)
}

export async function exportEstimate(request: Estimate): Promise<Blob> {
  const response = await fetch(`${baseUrl}/export`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'Export failed')
  }

  return response.blob()
}

export async function createAwsCalculatorLink(request: CalculatorLinkRequest): Promise<CalculatorLinkResponse> {
  const response = await fetch(`${baseUrl}/calculator-link`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const contentType = response.headers.get('content-type') ?? ''
    if (contentType.includes('application/json')) {
      const payload = await response.json().catch(() => null)
      const message = payload?.detail || payload?.error || payload?.message
      throw new Error(message || 'AWS calculator link generation failed')
    }

    const text = await response.text()
    throw new Error(text || 'AWS calculator link generation failed')
  }

  return response.json() as Promise<CalculatorLinkResponse>
}
