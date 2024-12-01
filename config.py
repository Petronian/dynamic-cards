# This might be a bit shaky.
from typing import Any, Optional
from aqt.addons import AddonManager

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
        self.settings = Settings(addon_manager=addon_manager, module_name=module_name)

class Settings:
    def __init__(self, addon_manager: AddonManager, module_name: str):
        self.setattr_nowrite('_addon_manager', addon_manager)
        self.setattr_nowrite('_module_name', module_name)
        self._read_settings()

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
        for k, v in config.items():
            self.setattr_nowrite(k, v)

    def _write_settings(self):
        config_keys = self.fetch_config().keys()
        config_new = {k: getattr(self, k) for k in config_keys}
        self._addon_manager.writeConfig(self._module_name, config_new)
        print('Successfully wrote to configuration file')