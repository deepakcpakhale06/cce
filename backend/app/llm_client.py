import json
import os
from typing import Any

import httpx

from .config import settings
from .models import EstimateRow

async def analyze_description(
    description: str,
    region: str,
    provider: str,
    provider_key: str | None = None,
) -> list[EstimateRow]:
    if provider == 'anthropic':
        return await analyze_with_anthropic(description, region, provider_key)
    if provider == 'gemini':
        return await analyze_with_gemini(description, region, provider_key)
    if provider == 'openai':
        return await analyze_with_openai(description, region, provider_key)
    if provider == 'local':
        return await analyze_with_local(description, region)
    raise RuntimeError(f'LLM provider "{provider}" is not configured or supported.')

async def analyze_with_anthropic(
    description: str,
    region: str,
    provider_key: str | None = None,
) -> list[EstimateRow]:
    api_key = provider_key or settings.anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise RuntimeError('Anthropic API key not configured')

    import anthropic

    client = anthropic.Client(api_key)
    prompt = generate_prompt(description, region)

    response = client.completions.create(
        model='claude-3.5-mini',
        prompt=prompt,
        max_tokens_to_sample=600,
        stop_sequences=['\n\n'],
    )
    text = response.completion
    return parse_estimate_rows(text)

async def analyze_with_gemini(description: str, region: str, provider_key: str | None = None) -> list[EstimateRow]:
    api_key = provider_key or settings.gemini_api_key or os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise RuntimeError('Gemini API key not configured')

    prompt = generate_prompt(description, region)
    payload = {
        'contents': [
            {
                'parts': [
                    {'text': prompt},
                ],
            },
        ],
    }
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key,
    }
    params = {}

    urls = [
        'https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent',
    ]

    last_error: Exception | None = None
    async with httpx.AsyncClient(timeout=60.0) as client:
        for url in urls:
            try:
                response = await client.post(url, json=payload, headers=headers, params=params)
                response.raise_for_status()
                body = response.json()
                text = extract_gemini_text(body)
                if not text:
                    print(f'Gemini response contained no text for url={url}; body={body}')
                if text:
                    return parse_estimate_rows(text)
            except httpx.ReadTimeout as exc:
                raise RuntimeError(
                    'Gemini request timed out. Please try again or check your network connection.',
                ) from exc
            except httpx.RequestError as exc:
                raise RuntimeError(
                    f'Gemini request failed: {exc}. Please verify your network connection and key.',
                ) from exc
            except httpx.HTTPStatusError as exc:
                last_error = exc
                status = exc.response.status_code
                body_text = exc.response.text
                message = None
                try:
                    detail = exc.response.json()
                    message = detail.get('error', {}).get('message') if isinstance(detail, dict) else None
                except ValueError:
                    message = None

                if status == 404:
                    continue
                if status in {401, 403}:
                    raise RuntimeError(
                        'Gemini authentication failed. Please verify your Gemini API key and that it is valid for Gemini.',
                    ) from exc
                if status == 400 and message:
                    raise RuntimeError(
                        f'Gemini request failed: {message} (status 400). Please verify your Gemini API key and request settings.',
                    ) from exc
                raise RuntimeError(
                    f'Gemini request failed: {message or exc} (status {status}). Request body: {body_text}',
                ) from exc

    if last_error and isinstance(last_error, httpx.HTTPStatusError) and last_error.response.status_code == 404:
        raise RuntimeError(
            'Gemini key or selected endpoint is invalid. Please verify your Gemini credentials or choose a different provider.',
        )

    raise RuntimeError(
        'Gemini request failed for all tested endpoints' + (f': {last_error}' if last_error else ''),
    )

async def analyze_with_local(
    description: str,
    region: str,
) -> list[EstimateRow]:
    url = settings.local_llm_url or os.getenv('LOCAL_LLM_URL')
    model = settings.local_llm_model
    if not url:
        raise RuntimeError(
            'Local model endpoint not configured. Set LOCAL_LLM_URL to a running local inference API.',
        )

    prompt = generate_prompt(description, region)
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': 'You are an AWS cost estimation assistant.'},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.2,
        'max_tokens': 600,
    }
    headers = {
        'Content-Type': 'application/json',
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                raise RuntimeError('Local model authentication failed. Please verify your local server settings.') from exc
            raise RuntimeError(f'Local model request failed: {exc}') from exc

        body = response.json()

    text = ''
    if isinstance(body, dict):
        choices = body.get('choices', [])
        if choices and isinstance(choices, list):
            message = choices[0].get('message', {})
            text = message.get('content', '')

    return parse_estimate_rows(text)


async def analyze_with_openai(
    description: str,
    region: str,
    provider_key: str | None = None,
) -> list[EstimateRow]:
    api_key = provider_key or settings.openai_api_key or os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OpenAI API key not configured')

    url = 'https://api.openai.com/v1/chat/completions'
    prompt = generate_prompt(description, region)
    payload = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': 'You are an AWS cost estimation assistant.'},
            {'role': 'user', 'content': prompt},
        ],
        'temperature': 0.2,
        'max_tokens': 600,
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 401:
                raise RuntimeError('OpenAI authentication failed. Please verify your OpenAI key.') from exc
            raise RuntimeError(f'OpenAI request failed: {exc}') from exc

        body = response.json()

    text = ''
    if isinstance(body, dict):
        choices = body.get('choices', [])
        if choices and isinstance(choices, list):
            message = choices[0].get('message', {})
            text = message.get('content', '')

    return parse_estimate_rows(text)


def generate_prompt(description: str, region: str) -> str:
    return (
        'You are an AWS cost estimation assistant. '
        'Based on this infrastructure description, return only a valid JSON array with up to 5 components. '
        'Each item must include componentName, awsServiceName, quantity, configuration, assumptions, costPerMonth, and yearlyCost. '
        f'Description: "{description}" Region: {region}. '
        'If you cannot infer exact pricing, set costPerMonth and yearlyCost to 0.'
    )


def extract_gemini_text(body: Any) -> str:
    if not isinstance(body, dict):
        return ''

    if 'candidates' in body and isinstance(body['candidates'], list) and body['candidates']:
        first = body['candidates'][0]
        content = first.get('content') or first.get('message', {}).get('content')
        if isinstance(content, list) and content:
            for item in content:
                if isinstance(item, dict) and 'text' in item:
                    return item['text']
            if isinstance(content[0], dict) and 'text' in content[0]:
                return content[0]['text']
        # newer responses may include a dict with 'parts' containing text
        if isinstance(content, dict):
            parts = content.get('parts') or content.get('message', {}).get('parts')
            if isinstance(parts, list) and parts:
                first_part = parts[0]
                if isinstance(first_part, dict) and 'text' in first_part:
                    return first_part['text']
                if isinstance(first_part, str):
                    return first_part
        if isinstance(content, str):
            return content

    # older Gemini response formats may include top-level text field
    if 'text' in body and isinstance(body['text'], str):
        return body['text']

    return ''


def parse_estimate_rows(text: str) -> list[EstimateRow]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return [EstimateRow(
            id='1',
            componentName='Application server',
            awsServiceName='Amazon EC2',
            quantity=1,
            configuration='t3.medium',
            assumptions='Default fallback estimate',
            costPerMonth=0,
            yearlyCost=0,
        )]

    rows = []
    for index, item in enumerate(payload if isinstance(payload, list) else []):
        rows.append(EstimateRow(
            id=str(item.get('id', index + 1)),
            componentName=item.get('componentName', ''),
            awsServiceName=item.get('awsServiceName', ''),
            quantity=int(item.get('quantity', 1)),
            configuration=item.get('configuration', ''),
            assumptions=item.get('assumptions', ''),
            costPerMonth=float(item.get('costPerMonth', 0) or 0),
            yearlyCost=float(item.get('yearlyCost', 0) or 0),
        ))
    return rows
