export type LLMProvider = 'local'

export interface EstimateRow {
  id: string
  componentName: string
  awsServiceName: string
  quantity: number
  configuration: string
  assumptions: string
  costPerMonth: number
  yearlyCost: number
}

export interface Estimate {
  rows: EstimateRow[]
}

export interface AnalyzeRequest {
  description: string
  region: string
}

export interface PricingRequest {
  rows: EstimateRow[]
  region: string
}

export interface CalculatorLinkRequest {
  description?: string
  rows: EstimateRow[]
  region: string
  estimate_name?: string
}

export interface CalculatorLinkResponse {
  url: string
  id?: string
  baked?: boolean
  warnings?: string[]
}
