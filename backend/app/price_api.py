from typing import Any
import asyncio
import httpx
from .models import EstimateRow
from .config import settings

SERVICE_TO_CODE = {
    'Amazon EC2': 'AmazonEC2',
    'Amazon RDS': 'AmazonRDS',
    'Amazon S3': 'AmazonS3',
    'Amazon Lambda': 'AWSLambda',
    'Amazon DynamoDB': 'AmazonDynamoDB',
    'Amazon ElastiCache': 'AmazonElastiCache',
}

async def enrich_with_pricing(rows: list[EstimateRow], region: str) -> list[EstimateRow]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [fetch_row_price(client, row, region) for row in rows]
        return await asyncio.gather(*tasks)

async def fetch_row_price(client: httpx.AsyncClient, row: EstimateRow, region: str) -> EstimateRow:
    if not row.awsServiceName:
        return row

    service_code = SERVICE_TO_CODE.get(row.awsServiceName)
    if not service_code:
        return row

    params = {
        'ServiceCode': service_code,
        'FormatVersion': 'aws_v1',
        'RegionCode': region,
        'MaxResults': 100,
    }

    try:
        response = await client.get(settings.aws_pricelist_api_url, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception:
        return row

    price = parse_price_from_response(data)
    row.costPerMonth = round(price * row.quantity, 2)
    row.yearlyCost = round(row.costPerMonth * 12, 2)
    return row


def parse_price_from_response(data: Any) -> float:
    if not isinstance(data, dict):
        return 0.0

    if 'PriceList' in data:
        try:
            price_list = data['PriceList']
            if isinstance(price_list, list) and price_list:
                first_item = price_list[0]
                terms = first_item.get('terms', {})
                for term_block in terms.values():
                    if isinstance(term_block, dict):
                        for term in term_block.values():
                            price_dimensions = term.get('priceDimensions', {})
                            if isinstance(price_dimensions, dict):
                                for dim in price_dimensions.values():
                                    price_per_unit = dim.get('pricePerUnit', {}).get('USD')
                                    if price_per_unit:
                                        return float(price_per_unit)
        except Exception:
            return 0.0

    return 0.0
