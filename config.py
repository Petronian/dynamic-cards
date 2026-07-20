# This might be a bit shaky.
from typing import Any, Optional
from aqt.addons import AddonManager
from os.path import abspath, dirname, join

PLATFORMS = ["Mistral AI (Mistral)", "Gemini (Google)"]
MISTRAL_MODELS = [
    "mistral-small-latest",
    "mistral-medium-latest",
    "mistral-large-latest",
    "ministral-3b-latest",
    "ministral-8b-latest",
    "ministral-14b-latest",
    "open-mistral-nemo",
    "open-mixtral-8x7b",
    "open-mixtral-8x22b",
]
GEMINI_MODELS = [
    "gemini-flash-lite-latest",
    "gemini-flash-latest",
    "gemini-pro-latest",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite"
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]

MODELS = [MISTRAL_MODELS, GEMINI_MODELS]

class Config:

    def __init__(self, addon_manager: AddonManager, module_name: str, debug: bool = False):
        # Fixed init vars
        self._addon_manager = addon_manager
        self._module_name = module_name

        # Cache variables
        self.data = {}
        self.pause = False
        self.debug = debug

        # Settings variables
        self.settings = Settings(addon_manager=addon_manager, module_name=module_name, debug=debug)

class Settings:

    CACHE = join(dirname(abspath(__file__)), 'dynamic.db')
    
    def __init__(self, addon_manager: AddonManager, module_name: str, debug: bool = False):
        self.setattr_nowrite('_addon_manager', addon_manager)
        self.setattr_nowrite('_module_name', module_name)
        self._read_settings()
        if debug:
            print(f'Settings: Establishing CACHE at {self.CACHE}')

    # Any time a setting is changed, write it to the configuration file.
    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        self._write_settings()

    def setattr_nowrite(self, name: str, value: Any) -> None:
        self.__dict__[name] = value

    def fetch_config(self) -> Optional[dict]:
        return self._addon_manager.getConfig(self._module_name)

    # Don't call setattr unnecessarily.
    def _read_settings(self):
        config = self.fetch_config()

        # One-time migration for users updating the addon
        if "platform_configs" not in config:
            # Create default structures for the new per-platform settings
            default_configs = [
                {
                    "api_key": config.get("api_key", ""),
                    "model": config.get("model", "mistral-medium-latest"),
                    "context": config.get("context", "You are a helpful flashcard assistant. Rewrite the following text to be slightly different, while preserving the core meaning and any special formatting like cloze deletions (e.g., {{c1::text}}). Do not add any conversational text or markdown formatting."),
                    "max_renders": config.get("max_renders", 3),
                    "num_retries": config.get("num_retries", 3),
                    "retry_delay_seconds": config.get("retry_delay_seconds", 1.0),
                },
                {
                    "api_key": "",
                    "model": "gemini-flash-latest",
                    "context": "You are a helpful flashcard assistant. Rewrite the following text to be slightly different, while preserving the core meaning and any special formatting like cloze deletions (e.g., {{c1::text}}). Do not add any conversational text or markdown formatting.",
                    "max_renders": 3,
                    "num_retries": 3,
                    "retry_delay_seconds": 1.0,
                }
            ]
            # Preserve the user's current settings for their selected platform
            current_platform_index = config.get("platform_index", 0)
            # Overwrite the default for the user's previously active platform
            default_configs[current_platform_index]["api_key"] = config.get("api_key", "")
            default_configs[current_platform_index]["model"] = config.get("model", "mistral-small-latest")

            self.setattr_nowrite("platform_configs", default_configs)

        for key, value in config.items():
            self.setattr_nowrite(key, value)

    def _write_settings(self):
        config_keys = self.fetch_config().keys()
        # Filter out old, now-unused top-level keys
        migrated_keys = {"api_key", "model", "context", "max_renders", "num_retries", "retry_delay_seconds"}
        config_new = {k: getattr(self, k) for k in self.__dict__.keys() if not k.startswith('_') and k not in migrated_keys}
        self._addon_manager.writeConfig(self._module_name, config_new)