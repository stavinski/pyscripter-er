from models import ScriptCollection

class ScriptCollectionStore(object):

    _SAVE_NAME = 'script_store'

    def __init__(self, callbacks):
        self.callbacks = callbacks

    def restore(self):
        # convert from json into collection
        # self.callbacks.loadExtensionSetting(ScriptStore._SAVE_NAME)
        return ScriptCollection()

    def save(self, scripts):
        # convert from collection in to json
        # self.callbacks.saveExtensionSetting(ScriptStore._SAVE_NAME, scripts)
        pass