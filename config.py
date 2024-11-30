# This might be a bit shaky.

class Config:

    @property
    def data(self):
        return self._data
    @property
    def pause(self):
        return self._pause
    @property
    def exclude_note_types(self):
        return self._exclude_note_types
    @property
    def model(self):
        return self._model
    @property
    def context(self):
        return self._context
    @property
    def api_key(self):
        return self._api_key
    @property
    def max_renders(self):
        return self._max_renders
    @property
    def debug(self):
        return self._debug
    
    # Make @[property].setter functions to automatically save changes to disk where needed

    def __init__(self, config, debug = False):
        self._data = {}
        self._pause = False
        self._exclude_note_types = config.get('exclude_note_types', [])
        self._model = str(config['model'])
        self._context = str(config['context'])
        self._api_key = str(config['api_key'])
        self._max_renders = config.get('max_renders', 3)
        self._debug = debug