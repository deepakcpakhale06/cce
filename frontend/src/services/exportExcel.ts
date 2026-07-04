import type { EstimateRow } from '../types'

export function exportEstimateToExcel(rows: EstimateRow[]) {
  const headers = [
    'Component/Function Name',
    'AWS Service Name',
    'Quantity',
    'Configuration',
    'Assumptions',
    'Cost Per Month (USD)',
    'Yearly Cost (USD)',
  ]

  const lines = [headers.join('\t')]
  lines.push(
    ...rows.map(row =>
      [
        row.componentName,
        row.awsServiceName,
        row.quantity,
        row.configuration,
        row.assumptions,
        row.costPerMonth.toFixed(2),
        (row.costPerMonth * 12).toFixed(2),
      ].join('\t'),
    ),
  )

  const blob = new Blob([lines.join('\n')], { type: 'text/tab-separated-values;charset=utf-8' })
  const fileName = 'aws-cost-estimate.tsv'
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = fileName
  link.click()
  URL.revokeObjectURL(link.href)
}
