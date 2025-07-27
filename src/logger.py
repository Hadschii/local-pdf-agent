import os
import csv
import logging
from datetime import datetime

class Logger:
    def __init__(self, log_dir="logs", reports_dir="reports"):
        os.makedirs(log_dir, exist_ok=True)
        os.makedirs(reports_dir, exist_ok=True)
        self.log_path = os.path.join(log_dir, "agent.log")
        logging.basicConfig(
            filename=self.log_path,
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    def log(self, message, level="info"):
        if level == "error":
            logging.error(message)
        elif level == "warning":
            logging.warning(message)
        else:
            logging.info(message)

    def create_report(self, records):
        """
        records: list of dicts with keys: original, new, category, timestamp, status, error
        """
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.reports_dir, f"report_{now}.csv")
        with open(report_path, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "original", "new", "category", "timestamp", "status", "error"
            ])
            writer.writeheader()
            for rec in records:
                writer.writerow(rec)
        self.log(f"Report created: {report_path}")
        return report_path
