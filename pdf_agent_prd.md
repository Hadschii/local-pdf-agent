# Product Requirements Document (PRD): Local AI Document Processing Agent

## 1. Purpose

Design and implement a **local AI-powered agent** for offline, automatic PDF document processing, categorization, and organization on **macOS**. The system will guarantee **privacy** and efficiency for users scanning documents via their mobile devices and uploading them to a specific folder.

## 2. Scope

- Operates entirely offline (no online inference or data transfer).
- Runs on **macOS** (Monterey or later).
- Accepts scanned PDF files placed into a designated "input" folder.

## 3. Functional Requirements

### 3.1 Input

- Accept PDF files, including both **digitally generated** and **scanned (OCR needed)** documents.
- File ingestion is triggered:
    - Automatically when a new file is dropped into the folder (real-time).
    - Batch processing weekly (scheduled automation).
    - Optionally, manually (on demand).

### 3.2 Document Understanding

- Extract text from PDFs using multiple strategies:
    - Native PDF extraction for text-based files.
    - OCR for image-based scanned files.

### 3.3 Classification

- Assign each document a **document_type** (e.g., invoice, payslip, contract, other) using a local LLM.
- Extract key fields for each document:
    - `document_type` (from a configurable list)
    - `date` (format: DD.MM.YYYY or similar)
    - `company` (e.g., Amazon, BMW Group)
- Detect and assign zero or more **labels** (e.g., car, medical, tax, work, etc.) to each document, based on LLM output and a configurable confidence threshold.
- All document types, labels, and thresholds are defined in a YAML config file.
- The LLM is prompted and parsed according to the config, and only labels above the threshold are assigned.

### 3.4 File Organization

- **Rename files** using extracted fields and a template-driven naming scheme, defined per document_type and optionally per label or label combination.
- **Move files** to folders based on document_type, with label-specific or multi-label-specific overrides (e.g., invoices with both "medical" and "tax" labels).
- All folder and naming rules are defined in the config file.
- Duplicate file names are handled gracefully.

### 3.5 Reporting & Logging

- Record all actions: original filename, new filename, document_type, labels, date, company, timestamp, success/failure.
- Generate regular summary reports for each batch/process run with:
    - Total files processed
    - Document_type and label breakdown
    - Sample activities
- Store reports in a dedicated "reports" folder.

### 3.6 Automation

- Monitor the input folder in real time and process files as they appear.
- Schedule batch runs automatically (macOS `cron` or `launchd`).
- Allow for manual triggers as needed.

### 3.7 Error Handling

- Graceful handling of:
    - Corrupt or unsupported files.
    - Classification failures (flag for manual review).
- Maintain error logs and optionally notify the user (e.g., via summary report).

## 4. Non-Functional Requirements

- **Performance**: Process and classify each PDF within 1–2 minutes, including OCR.
- **Usability**: Clear logs, actionable error messages, config files for customization.
- **Extensibility**: Modular Python codebase and configuration-driven document_types/labels/rules.
- **Security & Privacy**:
    - All processing is strictly local.
    - No data leaves the machine.
- The system supports German language for tagging files (e.g. bill -> rechnung)

## 5. Technology & Tools

| Component            | Suggested Tool/Library               |
|----------------------|--------------------------------------|
| PDF extraction       | pypdf, pymupdf                       |
| OCR                  | pytesseract, pdf2image, Pillow       |
| LLM Integration      | Ollama (llama3.3, qwen2, deepseek)   |
| Workflow orchestration | LangChain                           |
| File system monitoring | watchdog                            |
| Automation           | cron, launchd                        |
| Reporting            | pandas, native Python                |
| Configuration        | YAML files                           |

## 6. System Architecture Overview

- Python-based modular application with separate modules for:
    - PDF processing (OCR/extraction)
    - Document classification (LLM-based, config-driven)
    - File organization and renaming (config-driven, label/document_type aware)
    - Monitoring and scheduling
    - Reporting and logging
    - Error handling

- Configurable via YAML:
    - Document types
    - Labels
    - Naming conventions
    - Folder structure
    - Label overrides (single or multi-label, using comma-separated keys)
    - Confidence threshold
    - Fields to extract

## 7. Configuration & Customization

- **Document Types**: Defined in YAML config, with default folder/naming and label-specific overrides.
- **Labels**: Configurable list of possible labels, with a global confidence threshold.
- **Label Overrides**: Folder/naming rules can be overridden for specific labels or label combinations (using comma-separated keys).
- **Fields**: The set of fields to extract (document_type, date, company, etc.) is defined in the config.
- **No more keyword/category logic**: All classification and organization is LLM- and config-driven.

## 8. Security & Privacy Principles

- **No internet dependency**: All processing is local.
- **Data remains fully private** by design.
- **No external API calls for document analysis**.

## 9. Acceptance Criteria

- New PDFs placed in the input folder are processed, classified (document_type, labels, date, company), renamed, and moved in real time or on a scheduled batch.
- System correctly extracts text from both text-based and scanned PDFs.
- Classification accuracy above 90% on a representative sample.
- Generated reports summarize all key actions and are stored for user review.
- User can easily update or add new document_types, labels, naming schemes, and destination folders without programming.
- All document types, labels, and overrides are fully configurable in YAML.
- The system logs all detected fields, assigned labels, and final folder/naming decisions for each document.
- No legacy keyword/category logic remains in the codebase.

## 10. Examples

- A PDF containing a car insurance invoice (document_type: invoice, labels: car) is named and moved according to the `invoice` type, but with the `car` label override (e.g., `rechnung_kfz` in the filename and a special subfolder).
- A PDF with both "medical" and "tax" labels (document_type: invoice, labels: medical, tax) uses the multi-label override for folder and naming.
- All such rules are defined in the YAML config, using comma-separated keys for multi-label overrides.

## 11. Future Enhancements

- Train custom document classifiers for higher accuracy.
- Integrate document encryption for highly sensitive data.
- Friendly GUI for configuration.
- Plug-in system for custom processing steps or outputs.

