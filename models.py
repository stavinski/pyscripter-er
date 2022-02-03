

from select import select
import traceback


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

    def __getitem__(self, index):
        return self.scripts[index]

    def __len__(self):
        return len(self.scripts)

    def __iter__(self):
        return self.scripts

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo, macroItems=[]):
        # will pass onto inner list of Script instances
        pass


class Script(object):

    def __init__(self, extender, callbacks, helpers, title, enabled, content):
        self.title = title
        self.enabled = enabled
        self.content = content
        self.callbacks = callbacks
        self.helpers = helpers
        self.extender = extender

    def compile(self, output):
        try:
            output.text = ''
            compile(self.content, '<string>', 'exec')
        except:
            output.text = traceback.format_exc()

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo, macroItems=[]):
        if not self.enabled:
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
        
        exec(self.script, globals_, locals_)