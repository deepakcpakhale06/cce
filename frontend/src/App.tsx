import { useEffect, useState } from 'react'
import { analyzeSetup, createAwsCalculatorLink, exportEstimate, fetchPrices } from './services/api'
import { CalculatorLinkRequest, Estimate, EstimateRow } from './types'
import EstimateTable from './components/EstimateTable'
import RegionSelector from './components/RegionSelector'

const defaultRegion = import.meta.env.VITE_DEFAULT_AWS_REGION ?? 'ap-southeast-1'

function App() {
  const [description, setDescription] = useState('')
  const [region, setRegion] = useState(defaultRegion)
  const [rows, setRows] = useState<EstimateRow[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setError(null)
  }, [description, region])

  const handleAnalyze = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await analyzeSetup({ description, region })
      setRows(result.rows)
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to analyze the setup.'
      setError(`Unable to analyze the setup. ${message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleCalculate = async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetchPrices({ rows, region })
      setRows(result.rows)
    } catch (err) {
      setError('Unable to fetch pricing data. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    setLoading(true)
    setError(null)
    try {
      const blob = await exportEstimate({ rows })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = 'aws-cost-estimate.xlsx'
      link.click()
      URL.revokeObjectURL(url)
    } catch (err) {
      setError('Unable to export the estimate. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleAddRow = () => {
    setRows(prev => [
      ...prev,
      {
        id: crypto.randomUUID(),
        componentName: '',
        awsServiceName: '',
        quantity: 1,
        configuration: '',
        assumptions: '',
        costPerMonth: 0,
        yearlyCost: 0,
      },
    ])
  }

  const totalMonthly = rows.reduce((sum, r) => sum + (Number(r.costPerMonth) || 0), 0)
  const totalYearly = rows.reduce((sum, r) => sum + (Number(r.yearlyCost) || (Number(r.costPerMonth || 0) * 12)), 0)
  const handleOpenAwsCalculator = async () => {
    setLoading(true)
    setError(null)

    try {
      const request: CalculatorLinkRequest = {
        description: description?.trim() || undefined,
        rows,
        region,
        estimate_name: 'AWS Cost Estimator',
      }
      const result = await createAwsCalculatorLink(request)
      if (!result?.url) {
        throw new Error('No link returned from the server.')
      }
      window.open(result.url, '_blank', 'noopener')
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Unable to generate the AWS calculator link.'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header>
        <h1>AWS Cost Estimator</h1>
        <p>Describe your target architecture, then analyze and calculate estimates.</p>
      </header>

      <section className="card">
        <label htmlFor="description">Target setup description</label>
        <textarea
          id="description"
          value={description}
          onChange={e => setDescription(e.target.value)}
          placeholder="E.g. A web app with a React frontend, Django backend, PostgreSQL database, and S3 storage"
          rows={6}
        />

        <div className="controls-row">
          <RegionSelector region={region} onChange={setRegion} />
          <div className="provider-fixed">
            <strong>LLM provider:</strong> Local
          </div>
        </div>

        <div className="action-buttons">
          <button type="button" onClick={handleAnalyze} disabled={loading || !description}>
            Analyze
          </button>
          <button type="button" onClick={handleCalculate} disabled={loading || rows.length === 0}>
            Calculate Pricing
          </button>
          <button type="button" onClick={handleExport} disabled={rows.length === 0 || loading}>
            Export Excel
          </button>
        </div>

        {error ? <p className="error-message">{error}</p> : null}
      </section>

      <section className="card">
        <div className="table-header">
          <h2>Estimate rows</h2>
          <button type="button" onClick={handleAddRow} className="secondary-button">
            Add row
          </button>
        </div>

        <EstimateTable rows={rows} setRows={setRows} />
        <div className="totals-row">
          <div>
            <strong>Total monthly:</strong> ${totalMonthly.toFixed(2)}
          </div>
          <div>
            <strong>Total yearly:</strong> ${totalYearly.toFixed(2)}
          </div>
          <div>
            <button type="button" onClick={handleOpenAwsCalculator} className="calculator-link" disabled={rows.length === 0 || loading}>
              Generate AWS Pricing Calculator link
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}

export default App
