from typing import Tuple, Optional, Dict, Any
from src.logger import Logger
from src.llm_classifier import llm_classifier

logger = Logger()

def classify_text(text: str, config) -> Tuple[Optional[str], Optional[list], Optional[str], Optional[str], Optional[str]]:
    """
    Returns (document_type, labels, date, company)
    - document_type: best match (str)
    - labels: list of assigned labels (list of str)
    - date: detected date string or None
    - company: detected company string or None
    """
    if getattr(config, 'llm_enabled', False):
        llm_result = llm_classifier(text, getattr(config, 'llm_model', 'gemma3n'))
        if llm_result:
            document_type = llm_result.get('document_type')
            label_confidences = llm_result.get('labels', {}) if 'labels' in llm_result else {}
            labels = list(label_confidences.keys())
            date = llm_result.get('date')
            company = llm_result.get('company')
            content_summary = llm_result.get('content_summary')
            logger.log(f"LLM classified as {document_type} with labels {labels}, confidences {label_confidences}, date {date}, company {company}, content_summary {content_summary}")
            return document_type, labels, date, company, content_summary
        else:
            logger.log("LLM failed to classify document", level="error")
            return None, [], None, None
    logger.log("LLM classification is disabled in config", level="warning")
    # TODO Fallback to default classification logic
    return None, [], None, None
