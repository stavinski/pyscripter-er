import json
from models import ScriptCollection

class ScriptCollectionStore(object):

    _SAVE_NAME = 'script_store'

    def __init__(self, callbacks, helpers, extender):
        self.callbacks = callbacks
        self.helpers = helpers
        self.extender = extender

    def restore(self):
        json_string = self.callbacks.loadExtensionSetting(ScriptCollectionStore._SAVE_NAME)
        if json_string:
            print('restored scripts:')
            print(json_string)
            loaded = json.loads(json_string)
            return ScriptCollection.from_dict(loaded, self.callbacks, self.helpers, self.extender)
        
        return ScriptCollection()  # first time just return an empty collection

    def save(self, scripts):
        save = scripts.to_dict()
        json_string = json.dumps(save, indent=2)
        print('saving scripts:')
        print(json_string)
        self.callbacks.saveExtensionSetting(ScriptCollectionStore._SAVE_NAME, json_string)