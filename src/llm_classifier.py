import requests
import re
import json
from src.logger import Logger
from src.config import load_config

logger = Logger()

OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Load config for classification fields, label threshold, and valid values
def get_classification_config():
    config = load_config()
    return (
        config.get('labels', []),
        config.get('label_threshold', 0.75),
        config.get('document_types_list', ['invoice', 'payslip', 'contract', 'other'])
    )

def llm_classifier(text, model):
    labels, label_threshold, document_types_list = get_classification_config()
    PROMPT_TEMPLATE = (
        "Given the following document text, extract these fields as JSON:\n"
        f"- document_type: one of {document_types_list}\n"
        "- date: the most likely date in the document (format: DD.MM.YYYY or similar)\n. Additional example: für Oktober 2022 -> 221001, Abnahme 09.02.2024 -> 240209, München den 07.06.2021 -> 210607 "
        "- company: the company or sender of the document (e.g., Amazon, BMW Group, Cariad, Tchibo, ...)\n"
        "- content_summary: Please also provide a short, human-readable content summary in german (max 3 words) describing the main topic or item of the document, e.g., iPhone purchase, tax return, salary statement\n"
        f"- labels: zero or more of these: {labels}. For each, provide a confidence between 0 and 1.\n"
        "Return a JSON object with:\n"
        "  document_type: ...\n"
        "  date: ...\n"
        "  company: ...\n"
        "  content_summary: ...\n"
        "  labels: a dict of label: confidence (0-1)\n"
        "Document text:\n"
        f"{text}\n"
        "Respond with only the JSON object, wrapped in a markdown code block."
    )
    payload = {
        "model": model,
        "prompt": PROMPT_TEMPLATE,
        "stream": False
    }
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        raw = data.get("response", "")
        # Extract JSON from markdown code block
        match = re.search(r"```json\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if not match:
            logger.log(f"Ollama response did not contain JSON code block: {raw}", level="error")
            return None
        json_str = match.group(1)
        result = json.loads(json_str)
        # Filter labels by threshold
        if 'labels' in result and isinstance(result['labels'], dict):
            result['labels'] = {k: v for k, v in result['labels'].items() if v >= label_threshold}
        return result
    except Exception as e:
        logger.log(f"LLM classification failed: {e}", level="error")
        return None
