import os
import sys
from src.config import PDFConfig
from src.ingestor import PDFIngestor

def ensure_dirs(config):
    for path in [config.input_folder, config.output_folder, config.report_folder, 'logs']:
        os.makedirs(path, exist_ok=True)
        print(f"Ensured folder: {os.path.abspath(path)}")

def main():
    config_path = os.path.join('config', 'config.yaml')
    config = PDFConfig(config_path)
    ensure_dirs(config)

    import argparse
    parser = argparse.ArgumentParser(description="PDF Agent Main Entry Point")
    parser.add_argument('--watch', action='store_true', help='Watch input folder for new PDFs')
    parser.add_argument('--batch', action='store_true', help='Process all PDFs in input folder')
    args = parser.parse_args()
    ingestor = PDFIngestor(config_path)
    if args.watch:
        ingestor.watch_folder()
    elif args.batch:
        ingestor.batch_process()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
