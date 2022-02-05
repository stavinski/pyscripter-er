from burp import IBurpExtender, ISessionHandlingAction, IExtensionStateListener, IHttpListener, ITab, IBurpExtenderCallbacks
from scriptstore import ScriptCollectionStore
from gui import GUI

import traceback

IBurpExtenderCallbacks.TOOL_MACRO = 0

class BurpExtender(IBurpExtender, ISessionHandlingAction, IExtensionStateListener, IHttpListener, ITab):

    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.helpers
        self.script_store = ScriptCollectionStore(callbacks, self.helpers, self)
        self.scripts = self.script_store.restore()
        self.gui = GUI(self, self.callbacks, self.helpers, self.scripts)
        
        callbacks.setExtensionName("Python Scripter (modified)")
        callbacks.registerSessionHandlingAction(self)
        callbacks.registerExtensionStateListener(self)
        callbacks.registerHttpListener(self)
        callbacks.customizeUiComponent(self.getUiComponent())
        callbacks.addSuiteTab(self)

    def getActionName(self):
        return 'Send to Python Scripter'

    def extensionUnloaded(self):
        try:
            self.script_store.save(self.scripts)    
        except Exception:
            traceback.print_exc(file=self.callbacks.getStderr())
        return

    def performAction(self, currentRequest, macroItems):
        self.processHttpMessage(self.callbacks.TOOL_MACRO, 1, currentRequest, macroItems)
        return

    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo, macroItems=[]):
        try:
            self.scripts.processHttpMessage(toolFlag, messageIsRequest, messageInfo, macroItems)
        except Exception:
            traceback.print_exc(file=self.callbacks.getStderr())
        return

    def getTabCaption(self):
        return 'Scripts'

    def getUiComponent(self):
        return self.gui.build()
