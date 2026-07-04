import type { Dispatch, SetStateAction } from 'react'
import type { EstimateRow } from '../types'

interface EstimateTableProps {
  rows: EstimateRow[]
  setRows: Dispatch<SetStateAction<EstimateRow[]>>
}

const awsServices = [
  {
    value: 'EC2',
    label: 'EC2',
    config:
      'instances, instance_type, os, tenancy, workload, pricing, storage_type, storage_gb, data_inbound_gb, data_outbound_gb, data_intra_region_gb, hours_per_month, hours_per_day',
  },
  {
    value: 'RDS MySQL',
    label: 'RDS MySQL',
    config: 'nodes, instance_type, storage_gb, storage_type, deployment, pricing',
  },
  {
    value: 'RDS PostgreSQL',
    label: 'RDS PostgreSQL',
    config: 'nodes, instance_type, storage_gb, storage_type, deployment, pricing',
  },
  {
    value: 'Aurora MySQL',
    label: 'Aurora MySQL',
    config: 'nodes, instance_type, storage_gb, engine, edition',
  },
  {
    value: 'Aurora PostgreSQL',
    label: 'Aurora PostgreSQL',
    config: 'nodes, instance_type, storage_gb, engine, edition',
  },
  {
    value: 'S3',
    label: 'S3',
    config: 'storage_gb, storage_class, put_requests, get_requests, data_returned_gb, data_outbound_gb',
  },
  {
    value: 'Lambda',
    label: 'Lambda',
    config: 'requests, duration_ms, memory_mb, arch, free_tier',
  },
  {
    value: 'DynamoDB',
    label: 'DynamoDB',
    config: 'mode, read_capacity, write_capacity, storage_gb',
  },
  {
    value: 'ElastiCache',
    label: 'ElastiCache / Redis / Memcached',
    config: 'engine, nodes, node_type, cache_size_gb, pricing',
  },
  {
    value: 'CloudFront',
    label: 'CloudFront',
    config: 'data_transfer_gb, https_requests, http_requests',
  },
  {
    value: 'API Gateway',
    label: 'API Gateway',
    config: 'http_requests_million, rest_requests_million, avg_size_kb',
  },
  {
    value: 'ALB',
    label: 'ALB (Application Load Balancer)',
    config: 'load_balancers, data_processed_gb, connections_per_min, requests_per_sec',
  },
  {
    value: 'NLB',
    label: 'NLB (Network Load Balancer)',
    config: 'load_balancers, data_processed_gb, connections_per_min',
  },
  {
    value: 'VPC',
    label: 'VPC',
    config: 'public_ips, idle_ips, vpc_endpoints, nat_gateways, nat_data_gb, vpn_connections, tgw_attachments, data_inbound_gb, data_outbound_gb, data_intra_region_gb',
  },
  {
    value: 'NAT Gateway',
    label: 'NAT Gateway',
    config: 'gateways, nat_data_gb',
  },
  {
    value: 'Transit Gateway',
    label: 'Transit Gateway',
    config: 'attachments, tgw_data_gb',
  },
  {
    value: 'AWS Data Transfer',
    label: 'AWS Data Transfer',
    config: 'data_inbound_gb, data_outbound_gb, data_intra_region_gb',
  },
  {
    value: 'SQS',
    label: 'SQS',
    config: 'requests_million, message_size_kb, fifo',
  },
  {
    value: 'SNS',
    label: 'SNS',
    config: 'notifications_million',
  },
  {
    value: 'SES',
    label: 'SES',
    config: 'emails_sent_thousand, emails_received_thousand',
  },
  {
    value: 'CloudWatch',
    label: 'CloudWatch',
    config: 'metrics, logs_gb, dashboards, alarms, log_insights_gb',
  },
  {
    value: 'CloudTrail',
    label: 'CloudTrail',
    config: 'events_million, write_trails, read_trails, s3_trails, lambda_trails',
  },
  {
    value: 'GuardDuty',
    label: 'GuardDuty',
    config: 's3_data_gb, management_events_million, s3_events, ec2_instances, ecs_instances',
  },
]

const serviceHints = [
  { pattern: /\b(ec2|instance|virtual machine|vm|compute)\b/, service: 'EC2' },
  { pattern: /\b(lambda|function|serverless)\b/, service: 'Lambda' },
  { pattern: /\b(s3|bucket|object storage|storage)\b/, service: 'S3' },
  { pattern: /\b(dynamo(db)?|no[- ]sql database)\b/, service: 'DynamoDB' },
  { pattern: /\b(redis|elasticache|memcached|cache)\b/, service: 'ElastiCache' },
  { pattern: /\b(rds|postgresql|postgres|mysql|database)\b/, service: 'RDS MySQL' },
  { pattern: /\b(aurora)\b/, service: 'Aurora MySQL' },
  { pattern: /\b(cloudfront|cdn)\b/, service: 'CloudFront' },
  { pattern: /\b(api gateway|api gateway|rest api|http api)\b/, service: 'API Gateway' },
  { pattern: /\b(alb|application load balancer|load balancer)\b/, service: 'ALB' },
  { pattern: /\b(nlb|network load balancer)\b/, service: 'NLB' },
  { pattern: /\b(nat gateway)\b/, service: 'NAT Gateway' },
  { pattern: /\b(vpc|subnet|route table|internet gateway|vpn)\b/, service: 'VPC' },
  { pattern: /\b(transit gateway|tgw)\b/, service: 'Transit Gateway' },
  { pattern: /\b(data transfer|data in|data out|bandwidth)\b/, service: 'AWS Data Transfer' },
  { pattern: /\b(sqs|queue)\b/, service: 'SQS' },
  { pattern: /\b(sns|notification|topic)\b/, service: 'SNS' },
  { pattern: /\b(ses|email service|email)\b/, service: 'SES' },
  { pattern: /\b(cloudwatch|monitoring|logs|metrics|alarms)\b/, service: 'CloudWatch' },
  { pattern: /\b(cloudtrail|audit|trail)\b/, service: 'CloudTrail' },
  { pattern: /\b(guardduty|security monitoring|threat detection)\b/, service: 'GuardDuty' },
]

const inferAwsServiceName = (componentName: string): string => {
  const normalized = componentName.trim().toLowerCase()
  if (!normalized) {
    return ''
  }

  for (const hint of serviceHints) {
    if (hint.pattern.test(normalized)) {
      return hint.service
    }
  }

  return ''
}

const defaultConfigHelp = 'Enter service config values using the supported pricing calculator keys.'

export default function EstimateTable({ rows, setRows }: EstimateTableProps) {
  const updateRow = (id: string, changes: Partial<EstimateRow>) => {
    setRows(prev => prev.map(row => (row.id === id ? { ...row, ...changes } : row)))
  }

  const deleteRow = (id: string) => {
    setRows(prev => prev.filter(row => row.id !== id))
  }

  const getConfigHelp = (serviceName: string) => {
    const service = awsServices.find(s => s.value === serviceName)
    return service?.config || defaultConfigHelp
  }

  return (
    <div className="estimate-table-wrapper">
      <table className="estimate-table">
        <thead>
          <tr>
            <th>Component / Function Name</th>
            <th>AWS Service Name</th>
            <th>Quantity</th>
            <th>Configuration</th>
            <th>Assumptions</th>
            <th>Cost Per Month (USD)</th>
            <th>Yearly Cost (USD)</th>
            <th>Remove</th>
          </tr>
        </thead>
        <tbody>
          {rows.map(row => (
            <tr key={row.id}>
              <td>
                <input
                  value={row.componentName}
                  onChange={e => {
                    const componentName = e.target.value
                    const inferredAwsServiceName = row.awsServiceName || inferAwsServiceName(componentName)
                    updateRow(row.id, {
                      componentName,
                      awsServiceName: inferredAwsServiceName,
                    })
                  }}
                  placeholder="Component name"
                />
              </td>
              <td>
                <select
                  value={row.awsServiceName}
                  onChange={e => updateRow(row.id, { awsServiceName: e.target.value })}
                >
                  <option value="">Select service</option>
                  {awsServices.map(service => (
                    <option key={service.value} value={service.value}>
                      {service.label}
                    </option>
                  ))}
                </select>
                {row.awsServiceName && row.awsServiceName === inferAwsServiceName(row.componentName) ? (
                  <div className="hint-text">Inferred service from component name.</div>
                ) : null}
              </td>
              <td>
                <input
                  type="number"
                  min={1}
                  value={row.quantity}
                  onChange={e => updateRow(row.id, { quantity: Number(e.target.value) || 1 })}
                />
              </td>
              <td>
                <input
                  value={row.configuration}
                  onChange={e => updateRow(row.id, { configuration: e.target.value })}
                  placeholder="e.g. instance_type=t3.medium, storage_gb=100, pricing=on-demand"
                />
                <div className="config-hint">
                  Use comma-separated key=value pairs. {getConfigHelp(row.awsServiceName)}
                </div>
              </td>
              <td>
                <input
                  value={row.assumptions}
                  onChange={e => updateRow(row.id, { assumptions: e.target.value })}
                  placeholder="Assumptions"
                />
              </td>
              <td>
                <input
                  value={row.costPerMonth}
                  onChange={e => updateRow(row.id, { costPerMonth: Number(e.target.value) || 0 })}
                  type="number"
                  min={0}
                />
              </td>
              <td>{(row.costPerMonth * 12).toFixed(2)}</td>
              <td>
                <button type="button" onClick={() => deleteRow(row.id)}>
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
