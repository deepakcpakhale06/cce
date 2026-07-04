import re

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .models import AnalyzeRequest, CalculatorLinkRequest, Estimate, EstimateRow, PricingRequest
from .llm_client import analyze_description
from .price_api import enrich_with_pricing
from .exporter import streaming_excel_response
from aws_calc_mcp.core import create_estimate

app = FastAPI(title='AWS Cost Estimator Backend')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post('/analyze', response_model=Estimate)
async def analyze(request: AnalyzeRequest):
    if request.region != 'ap-southeast-1':
        raise HTTPException(status_code=400, detail='Only region ap-southeast-1 is supported.')
    try:
        rows = await analyze_description(
            request.description,
            request.region,
            'local',
            None,
        )
        rows = await enrich_with_pricing(rows, request.region)
        return Estimate(rows=rows)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.post('/pricing', response_model=Estimate)
async def pricing(request: PricingRequest):
    if request.region != 'ap-southeast-1':
        raise HTTPException(status_code=400, detail='Only region ap-southeast-1 is supported.')
    try:
        rows = await enrich_with_pricing(request.rows, request.region)
        return Estimate(rows=rows)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

def _parse_config_value(value: str):
    value = value.strip()
    if not value:
        return value
    lowered = value.lower()
    if lowered in ('true', 'yes', 'on'):
        return True
    if lowered in ('false', 'no', 'off'):
        return False
    try:
        if '.' in value:
            return float(value)
        return int(value)
    except ValueError:
        return value


def _parse_config_string(config_text: str) -> dict:
    config: dict = {}
    if not config_text:
        return config

    fragments = [frag.strip() for frag in config_text.replace(';', ',').split(',') if frag.strip()]
    for fragment in fragments:
        if '=' in fragment:
            key, raw_value = fragment.split('=', 1)
        elif ':' in fragment:
            key, raw_value = fragment.split(':', 1)
        else:
            continue
        key = key.strip()
        value = _parse_config_value(raw_value)
        if key:
            config[key] = value
    return config


def _quantity_key_for_service(service_name: str) -> str | None:
    mapping = {
        'ec2': 'instances',
        'rds mysql': 'nodes',
        'rds postgresql': 'nodes',
        'aurora mysql': 'nodes',
        'aurora postgresql': 'nodes',
        'elasticache': 'nodes',
        'alb': 'load_balancers',
        'nlb': 'load_balancers',
        'nat gateway': 'gateways',
        'transit gateway': 'attachments',
    }
    return mapping.get(service_name.lower())


def _normalize_service_name(service_name: str) -> str:
    name = service_name.strip()
    normalized = name.lower()
    mapping = {
        'ec2': 'EC2',
        'amazon ec2': 'EC2',
        'amazon elastic compute cloud': 'EC2',
        'amazon elastic compute cloud (ec2)': 'EC2',
        'ebs': 'EBS',
        'amazon ebs': 'EBS',
        'amazon elastic block store': 'EBS',
        's3': 'S3',
        'amazon s3': 'S3',
        'amazon simple storage service': 'S3',
        'lambda': 'Lambda',
        'amazon lambda': 'Lambda',
        'dynamodb': 'DynamoDB',
        'amazon dynamodb': 'DynamoDB',
        'rds mysql': 'RDS MySQL',
        'amazon rds mysql': 'RDS MySQL',
        'rds postgresql': 'RDS PostgreSQL',
        'amazon rds postgresql': 'RDS PostgreSQL',
        'aurora mysql': 'Aurora MySQL',
        'aurora postgresql': 'Aurora PostgreSQL',
        'amazon aurora mysql': 'Aurora MySQL',
        'amazon aurora postgresql': 'Aurora PostgreSQL',
        'elasticache': 'ElastiCache',
        'amazon elasticache': 'ElastiCache',
        'cloudfront': 'CloudFront',
        'amazon cloudfront': 'CloudFront',
        'api gateway': 'API Gateway',
        'amazon api gateway': 'API Gateway',
        'alb': 'ALB',
        'application load balancer': 'ALB',
        'nlb': 'NLB',
        'network load balancer': 'NLB',
        'vpc': 'VPC',
        'nat gateway': 'NAT Gateway',
        'transit gateway': 'Transit Gateway',
        'aws data transfer': 'AWS Data Transfer',
        'sqs': 'SQS',
        'sns': 'SNS',
        'ses': 'SES',
        'cloudwatch': 'CloudWatch',
        'cloudtrail': 'CloudTrail',
        'guardduty': 'GuardDuty',
    }
    if normalized in mapping:
        return mapping[normalized]

    # Fallback for service strings containing known keywords.
    if 'ec2' in normalized or 'elastic compute' in normalized:
        return 'EC2'
    if 'elastic block store' in normalized or normalized == 'ebs':
        return 'EBS'
    if 'simple storage' in normalized or normalized == 's3':
        return 'S3'
    if 'lambda' in normalized:
        return 'Lambda'
    if 'dynamodb' in normalized:
        return 'DynamoDB'
    if 'aurora' in normalized and 'postgres' in normalized:
        return 'Aurora PostgreSQL'
    if 'aurora' in normalized and 'mysql' in normalized:
        return 'Aurora MySQL'
    if 'rds' in normalized and 'mysql' in normalized:
        return 'RDS MySQL'
    if 'rds' in normalized and 'postgre' in normalized:
        return 'RDS PostgreSQL'
    if 'elasticache' in normalized or 'redis' in normalized or 'memcached' in normalized:
        return 'ElastiCache'
    if 'cloudfront' in normalized:
        return 'CloudFront'
    if 'api gateway' in normalized or 'apigateway' in normalized:
        return 'API Gateway'
    if 'alb' in normalized or 'application load balancer' in normalized:
        return 'ALB'
    if 'nlb' in normalized or 'network load balancer' in normalized:
        return 'NLB'
    if 'vpc' in normalized:
        return 'VPC'
    if 'nat gateway' in normalized:
        return 'NAT Gateway'
    if 'transit gateway' in normalized:
        return 'Transit Gateway'
    if 'aws data transfer' in normalized or 'data transfer' in normalized:
        return 'AWS Data Transfer'
    if 'sqs' in normalized:
        return 'SQS'
    if 'sns' in normalized:
        return 'SNS'
    if 'ses' in normalized:
        return 'SES'
    if 'cloudwatch' in normalized:
        return 'CloudWatch'
    if 'cloudtrail' in normalized:
        return 'CloudTrail'
    if 'guardduty' in normalized:
        return 'GuardDuty'

    return name


def _rows_to_services(rows: list[EstimateRow], region: str) -> list[dict]:
    services: list[dict] = []
    for row in rows:
        raw_service_name = row.awsServiceName.strip() if row.awsServiceName else row.componentName.strip()
        if not raw_service_name:
            continue

        service_name = _normalize_service_name(raw_service_name)
        config = _build_service_config(service_name, row)

        services.append({
            'service': service_name,
            'region': region,
            'description': row.componentName.strip() or None,
            'config': config,
        })
    return services


def _build_service_config(service_name: str, row: EstimateRow) -> dict:
    config = _parse_config_string(row.configuration)
    if not isinstance(config, dict):
        config = {}

    raw = row.configuration or ''
    lowered = raw.lower()

    if service_name == 'EC2':
        if 'instance_type' not in config:
            match = re.search(r'\b(?:t[2345]\.\w+|m[2345]\.\w+|c[2345]\.\w+|r[34]\.\w+|db\.\w+)\b', lowered)
            if match:
                config['instance_type'] = match.group(0)
        if 'storage_type' not in config and 'gp2' in lowered:
            config['storage_type'] = 'gp2'
        if 'storage_gb' not in config:
            storage_match = re.search(r'(\d+)\s*gb', lowered)
            if storage_match:
                config['storage_gb'] = int(storage_match.group(1))
    elif service_name == 'EBS':
        if 'storage_type' not in config:
            for t in ('gp3', 'gp2', 'io1', 'io2', 'st1', 'sc1'):
                if t in lowered:
                    config['storage_type'] = t
                    break
        if 'storage_gb' not in config:
            storage_match = re.search(r'(\d+)\s*gb', lowered)
            if storage_match:
                config['storage_gb'] = int(storage_match.group(1))
        if 'volumes' not in config and row.quantity:
            config['volumes'] = row.quantity
    elif service_name == 'S3':
        if 'storage_gb' not in config:
            storage_match = re.search(r'(\d+)\s*gb', lowered)
            if storage_match:
                config['storage_gb'] = int(storage_match.group(1))
        if 'storage_class' not in config and 'glacier' in lowered:
            config['storage_class'] = 'glacier'
    elif service_name in {'RDS MySQL', 'RDS PostgreSQL', 'Aurora MySQL', 'Aurora PostgreSQL'}:
        if 'instance_type' not in config:
            match = re.search(r'\bdb\.\w+\b', lowered)
            if match:
                config['instance_type'] = match.group(0)
        if 'nodes' not in config and row.quantity:
            config['nodes'] = row.quantity
    elif service_name == 'Lambda':
        if 'requests' not in config and row.quantity:
            config['requests'] = row.quantity

    quantity_key = _quantity_key_for_service(service_name)
    if row.quantity and quantity_key and quantity_key not in config:
        config[quantity_key] = row.quantity

    return config


@app.post('/export')
def export_estimate(request: Estimate):
    return streaming_excel_response(request.rows)

@app.post('/calculator-link')
async def calculator_link(request: CalculatorLinkRequest):
    if request.region != 'ap-southeast-1':
        raise HTTPException(status_code=400, detail='Only region ap-southeast-1 is supported.')

    services = _rows_to_services(request.rows, request.region)
    prompt = request.description.strip() if request.description and request.description.strip() else None

    if not services and not prompt:
        raise HTTPException(
            status_code=400,
            detail='Provide a description or estimate rows to generate an AWS calculator link.',
        )

    try:
        result = await create_estimate(
            estimate_name=request.estimate_name,
            groups=None,
            services=services or None,
            prompt=prompt if not services else None,
            compute_costs=True,
            group=True,
            region=request.region,
        )
        if not result.get('ok'):
            raise RuntimeError(result.get('error') or 'Failed to create the AWS calculator link.')
        return {
            'url': result['url'],
            'id': result.get('id'),
            'baked': result.get('baked', False),
            'warnings': result.get('warnings', []),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

@app.get('/health')
def health():
    return {'status': 'ok', 'backend': 'ready', 'region': settings.default_aws_region}
