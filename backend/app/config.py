from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / '.env')

class Settings:
    anthropic_api_key: str | None = os.getenv('ANTHROPIC_API_KEY')
    gemini_api_key: str | None = os.getenv('GEMINI_API_KEY')
    openai_api_key: str | None = os.getenv('OPENAI_API_KEY')
    local_llm_url: str | None = os.getenv('LOCAL_LLM_URL')
    local_llm_model: str = os.getenv('LOCAL_LLM_MODEL', 'local')
    llm_provider: str = os.getenv('LLM_PROVIDER', 'anthropic')
    aws_pricelist_api_url: str = os.getenv('AWS_PRICELIST_API_URL', 'https://api.pricing.us-east-1.amazonaws.com')
    default_aws_region: str = os.getenv('DEFAULT_AWS_REGION', 'ap-southeast-1')

settings = Settings()
