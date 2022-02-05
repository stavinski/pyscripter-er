from time import time
import traceback

DEFAULT_SCRIPT = '''from pyscripterer import BaseScript as Script

args = [extender, callbacks, helpers, toolFlag, messageIsRequest, messageInfo, macroItems]

script = Script(*args)
script.help()
'''

class ObservableCollection(object):
    
    ITEM_ADDED = 2
    ITEM_REMOVED = 1

    def __init__(self):
        self.listeners = []

    def add(self, obj):  # implemented by subclass
        pass

    def remove(self, obj):  # implemented by subclass
        pass

    def add_listener(self, listener):
        self.listeners.append(listener)

    def remove_listener(self, listener):
        self.listeners.remove(listener)

    def _fireChangedEvent(self, type, obj):
        for listener in self.listeners:
            listener.collection_changed(self, type, obj)


class ScriptCollection(ObservableCollection):
    
    def __init__(self):
        super(ScriptCollection, self).__init__()
        self.scripts = []

    def add(self, script):
        self.scripts.append(script)
        self._fireChangedEvent(ObservableCollection.ITEM_ADDED, script)

    def remove(self, script):
        self.scripts.remove(script)
        self._fireChangedEvent(ObservableCollection.ITEM_REMOVED, script)

    def to_dict(self):
        return {
            'created_at': int(time()),
            'scripts': [script.to_dict() for script in self.scripts] 
        }

    def __getitem__(self, index):
        return self.scripts[index]

    def __len__(self):
        return len(self.scripts)

    def __iter__(self):
        return self.scripts

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo, macroItems=[]):
        for script in self.scripts:
            script.processHttpMessage(toolFlag, messageIsRequest, messageInfo, macroItems)

    @classmethod
    def from_dict(cls, val, callbacks, helpers, extender):
        coll = ScriptCollection()
        for script in val['scripts']:
            coll.add(Script.from_dict(script, callbacks, helpers, extender))

        return coll

class Script(object):

    def __init__(self, extender, callbacks, helpers, title, enabled=True, content=DEFAULT_SCRIPT):
        self.title = title
        self.enabled = enabled
        self.callbacks = callbacks
        self.helpers = helpers
        self.extender = extender
        self.content = content

    def to_dict(self):
        fields = ['title', 'enabled', 'content']
        return { field: getattr(self, field) for field in fields}
        
    def compile(self, output):
        try:
            self.code = None
            output.text = ''
            self.code = compile(self.content, '<string>', 'exec')
        except:
            output.text = traceback.format_exc()

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo, macroItems=[]):
        if not self.enabled and self.code:
            return
        
        globals_ = {}
        locals_  = {'extender': self.extender,
                    'callbacks': self.callbacks,
                    'helpers': self.helpers,
                    'toolFlag': toolFlag,
                    'messageIsRequest': messageIsRequest,
                    'messageInfo': messageInfo,
                    'macroItems': macroItems
                    }
        
        exec(self.code, globals_, locals_)
    
    @classmethod
    def from_dict(cls, val, callbacks, helpers, extender):
        return Script(extender, 
            callbacks, 
            helpers, 
            val['title'], 
            val['enabled'], 
            val['content'])
