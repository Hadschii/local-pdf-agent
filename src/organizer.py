import os
import re
import shutil
from datetime import datetime
from src.logger import Logger
from src.config import load_config

logger = Logger()

def sanitize_filename(filename, max_length=120):
    # Remove or replace unsupported characters
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    # Optionally, remove other problematic unicode chars
    filename = filename.replace('\n', '').replace('\r', '')
    # Truncate if too long
    if len(filename) > max_length:
        base, ext = os.path.splitext(filename)
        filename = base[:max_length - len(ext)] + ext
    return filename

def organize_file(file_path, document_type, labels, meta=None):
    """
    Rename and move the file based on document_type, labels, and config. meta should include date, company, content, etc.
    Returns new file path.
    """
    config = load_config()
    doc_types_cfg = config.get('document_types', {})
    if not document_type or document_type not in doc_types_cfg:
        logger.log(f"No valid document_type for {file_path}, skipping organization.", level="warning")
        return None
    doc_cfg = doc_types_cfg[document_type]
    # Prepare metadata for naming
    # Use detected date if provided, else fallback to now
    if meta and meta.get('date'):
        try:
            if '.' in meta['date']:
                dt = datetime.strptime(meta['date'], "%d.%m.%Y")
            elif '-' in meta['date']:
                dt = datetime.strptime(meta['date'], "%Y-%m-%d")
            else:
                dt = datetime.now()
            date_str = dt.strftime(config.get('date_format', '%y%m%d'))
        except Exception:
            dt = datetime.now()
            date_str = dt.strftime(config.get('date_format', '%y%m%d'))
    else:
        dt = datetime.now()
        date_str = dt.strftime(config.get('date_format', '%y%m%d'))
    company = meta.get('company', 'unknown') if meta else 'unknown'
    content_summary = meta.get('content_summary', 'other') if meta else 'other'
    year = dt.strftime('%Y')
    # --- Label override resolution ---
    naming = doc_cfg.get('naming', config.get('default_naming'))
    folder = doc_cfg.get('folder', '')
    label_overrides = doc_cfg.get('label_overrides', {})
    # Try multi-label overrides first (keys as tuples/lists)
    matched_override = None
    if label_overrides:
        # Sort keys by number of labels descending (most specific first)
        for key in sorted(label_overrides.keys(), key=lambda k: -len(k.split(',')) if ',' in k else -1):
            key_labels = [lbl.strip() for lbl in key.split(',')] if ',' in key else [key]
            if all(l in labels for l in key_labels) and len(key_labels) == len(labels):
                matched_override = label_overrides[key]
                break
        # If not found, try single label matches
        if not matched_override:
            for key in label_overrides:
                if key in labels:
                    matched_override = label_overrides[key]
                    break
    if matched_override:
        naming = matched_override.get('naming', naming)
        folder = matched_override.get('folder', folder)
    folder = folder.format(year=year, company=company)
    out_dir = os.path.join(config.get('output_folder', './output'), folder)
    os.makedirs(out_dir, exist_ok=True)
    # Build fields dict for formatting
    fields = {
        'date': date_str,
        'category': document_type.lower(),
        'company': company,
        'content_summary': content_summary
    }
    filename = naming.format(**fields)
    filename = filename.replace(' ', '_')
    filename = sanitize_filename(filename)
    new_path = os.path.join(out_dir, filename)
    # Handle duplicates
    base, ext = os.path.splitext(new_path)
    counter = 1
    while os.path.exists(new_path):
        new_path = f"{base}_{counter}{ext}"
        counter += 1
    # Move file
    try:
        shutil.move(file_path, new_path)
        logger.log(f"Moved and renamed file to {new_path}")
        logger.log(f"Fields: document_type={document_type}, labels={labels}, date={date_str}, company={company}, content_summary={content_summary}, folder={folder}, filename={filename}")
        return new_path
    except Exception as e:
        logger.log(f"Failed to move file {file_path} to {new_path}: {e}", level="error")
        return None
