from fastapi.testclient import TestClient
from app.main import app
from app.models import EstimateRow

client = TestClient(app)

def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_analyze_returns_priced_rows(monkeypatch):
    async def fake_analyze_description(description, region, provider, provider_key=None):
        return [
            EstimateRow(
                id='1',
                componentName='EC2 Instance',
                awsServiceName='EC2',
                quantity=1,
                configuration='t2.micro',
                assumptions='On-demand',
                costPerMonth=0,
                yearlyCost=0,
            )
        ]

    async def fake_enrich_with_pricing(rows, region):
        rows[0].costPerMonth = 50.0
        rows[0].yearlyCost = 600.0
        return rows

    monkeypatch.setattr('app.main.analyze_description', fake_analyze_description)
    monkeypatch.setattr('app.main.enrich_with_pricing', fake_enrich_with_pricing)

    response = client.post('/analyze', json={'description': '1 x t2.micro EC2 instance', 'region': 'ap-southeast-1'})
    assert response.status_code == 200
    row = response.json()['rows'][0]
    assert row['costPerMonth'] == 50.0
    assert row['yearlyCost'] == 600.0
