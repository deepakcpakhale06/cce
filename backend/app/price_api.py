from aws_calc_mcp.core import create_estimate
from .models import EstimateRow

async def enrich_with_pricing(rows: list[EstimateRow], region: str) -> list[EstimateRow]:
    priced_rows: list[EstimateRow] = []
    for row in rows:
        priced_rows.append(await _compute_row_pricing(row, region))
    return priced_rows

async def _compute_row_pricing(row: EstimateRow, region: str) -> EstimateRow:
    if not row.awsServiceName:
        return row

    # Construct AWS Pricing Link instead of calling the estimator API
    pricing_link_url = _generate_pricing_link(row, region)

    # Set the link on the row object and clear cost fields
    row.pricingLinkUrl = pricing_link_url
    row.costPerMonth = None
    row.yearlyCost = None
        return row

def _build_pricing_prompt(row: EstimateRow, region: str) -> str:
    parts = []
    if row.quantity and row.quantity != 1:
        parts.append(str(row.quantity))

    if row.configuration:
        parts.append(str(row.configuration))

    if row.awsServiceName:
        parts.append(str(row.awsServiceName))

    if row.componentName and row.componentName not in row.awsServiceName and row.componentName not in row.configuration:
        parts.append(str(row.componentName))

    parts.append(f'in {region}')
    return ' '.join(parts)

def _generate_pricing_link(row: EstimateRow, region: str) -> str:
    """
    Generates a URL pointing to the AWS pricing page for the given service and configuration.
    This is a placeholder implementation as the exact URL structure depends on AWS documentation.
    """

    # Basic URL construction - replace with actual AWS URL logic if available
    service_name = row.awsServiceName.replace(" ", "-")
    config_summary = str(row.configuration).replace(" ", "-") if row.configuration else ""

    # Example pattern: https://aws.amazon.com/pricing/[SERVICE_NAME]/?region=[REGION]
    base_url = f"https://aws.amazon.com/pricing/{service_name}/?region={region}"

    if config_summary:
        # Append configuration detail if possible, though this is highly speculative
        return f"{base_url}#config={config_summary}"

    return base_url

