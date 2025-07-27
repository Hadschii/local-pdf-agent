import yaml
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class ConfigError(Exception):
    pass

class PDFConfig:
    def __init__(self, config_path="config/config.yaml"):
        self.config_path = config_path
        self.data = self._load_config()
        self._validate()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise ConfigError(f"Config file not found: {self.config_path}")
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _validate(self):
        required = ["input_folder", "output_folder", "report_folder"]
        for key in required:
            if key not in self.data:
                raise ConfigError(f"Missing required config key: {key}")

    @property
    def input_folder(self):
        return self.data["input_folder"]

    @property
    def output_folder(self):
        return self.data["output_folder"]

    @property
    def report_folder(self):
        return self.data["report_folder"]    

    @property
    def default_naming(self):
        return self.data.get("default_naming", "{date}_{category}_{company}_{content_summary}.pdf")

    @property
    def date_format(self):
        return self.data.get("date_format", "%y%m%d")

    @property
    def language(self):
        return self.data.get("language", "de")

    @property
    def llm_enabled(self):
        return self.data.get("llm_enabled", False)

    @property
    def llm_model(self):
        return self.data.get("llm_model", "gemma3n")
