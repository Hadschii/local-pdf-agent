import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.config import PDFConfig
from src.logger import Logger
from src.extractor import extract_text_from_pdf
from src.classifier import classify_text
from src.organizer import organize_file

class PDFIngestHandler(FileSystemEventHandler):
    def __init__(self, process_func, logger):
        super().__init__()
        self.process_func = process_func
        self.logger = logger

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.pdf'):
            self.logger.log(f"New PDF detected: {event.src_path}")
            self.process_func(event.src_path)

class PDFIngestor:
    def __init__(self, config_path="config/config.yaml"):
        self.config = PDFConfig(config_path)
        self.logger = Logger()
        self.input_folder = self.config.input_folder
        os.makedirs(self.input_folder, exist_ok=True)

    def process_pdf(self, file_path):
        self.logger.log(f"Processing PDF: {file_path}")
        text, method = extract_text_from_pdf(file_path)
        self.logger.log(f"Extraction method: {method}")
        if not text:
            self.logger.log(f"No text extracted from {file_path}", level="error")
            return
        document_type, labels, date, company, content_summary = classify_text(text, self.config)
        #if labels:
        #   self.logger.log(f"Assigned labels: {labels}")
        #if date:
        #    self.logger.log(f"Detected date: {date}")
        #if company:
        #    self.logger.log(f"Detected company: {company}")
        #if document_type:
        #    self.logger.log(f"Classified as: {document_type}")
        #else:
        #    self.logger.log(f"No document_type matched for {file_path}", level="warning")
        # Organize file (rename and move), pass all meta
        meta = {"date": date, "company": company, "content_summary": content_summary} if date or company else None
        new_path = organize_file(file_path, document_type, labels, meta=meta)
        if new_path:
            self.logger.log(f"File organized to: {new_path}")
        else:
            self.logger.log(f"File organization failed for {file_path}", level="error")

    def watch_folder(self):
        event_handler = PDFIngestHandler(self.process_pdf, self.logger)
        observer = Observer()
        observer.schedule(event_handler, self.input_folder, recursive=False)
        observer.start()
        self.logger.log(f"Started monitoring folder: {self.input_folder}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    def batch_process(self):
        pdfs = [f for f in os.listdir(self.input_folder) if f.lower().endswith('.pdf')]
        for pdf in pdfs:
            file_path = os.path.join(self.input_folder, pdf)
            self.process_pdf(file_path)
        self.logger.log(f"Batch processed {len(pdfs)} PDF(s) in {self.input_folder}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="PDF Agent Ingestor")
    parser.add_argument('--watch', action='store_true', help='Watch input folder for new PDFs')
    parser.add_argument('--batch', action='store_true', help='Process all PDFs in input folder')
    args = parser.parse_args()

    ingestor = PDFIngestor()
    if args.watch:
        ingestor.watch_folder()
    elif args.batch:
        ingestor.batch_process()
    else:
        parser.print_help()
