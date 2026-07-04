from app.llm_client import _strip_code_fence, parse_estimate_rows, generate_prompt


def test_strip_code_fence_removes_markdown_fence():
    fenced = '```json\n[\n  {\n    "componentName": "EC2 Instance",\n    "awsServiceName": "EC2",\n    "quantity": 1,\n    "configuration": "t2.micro",\n    "assumptions": "running 24/7",\n    "costPerMonth": 0,\n    "yearlyCost": 0\n  }\n]\n```'
    assert _strip_code_fence(fenced) == '[\n  {\n    "componentName": "EC2 Instance",\n    "awsServiceName": "EC2",\n    "quantity": 1,\n    "configuration": "t2.micro",\n    "assumptions": "running 24/7",\n    "costPerMonth": 0,\n    "yearlyCost": 0\n  }\n]'


def test_parse_estimate_rows_can_handle_fenced_json():
    text = '```json\n[\n  {\n    "componentName": "EC2 Instance",\n    "awsServiceName": "EC2",\n    "quantity": 1,\n    "configuration": "t2.micro",\n    "assumptions": "running 24/7",\n    "costPerMonth": 0,\n    "yearlyCost": 0\n  }\n]\n```'
    rows = parse_estimate_rows(text)
    assert len(rows) == 1
    assert rows[0].awsServiceName == 'EC2'
    assert rows[0].configuration == 't2.micro'
    assert rows[0].costPerMonth == 0


def test_generate_prompt_requests_exact_types_and_json_only():
    prompt = generate_prompt('1 x t2.micro EC2 instance', 'ap-southeast-1')
    assert 'only a valid JSON array' in prompt
    assert 'Do not provide any explanation' in prompt
    assert 'exact instance types' in prompt
