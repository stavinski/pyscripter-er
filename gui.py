from javax.swing import JTabbedPane, JPanel, JButton, JLabel, SwingConstants
from javax.swing.event import ChangeListener
from java.awt import BorderLayout, Font
from uicomponents import TabComponent, TabComponentEditableTabMixin, TabComponentCloseableMixin
from models import Script


class ScriptTabbedPane(JTabbedPane):
    
    EMPTY_SCRIPT_TEXT  = '''<html><body>
<div style="font-size: 16pt;text-align:center">
You have no Python scripts created.<br/> Please use the add tab (+) button to create a new Python script.
</div></body></html>'''

    def __init__(self, extender, callbacks, helpers, scripts):
        super(ScriptTabbedPane, self).__init__()
        self.scripts = scripts
        self.extender = extender
        self.callbacks = callbacks
        self.helpers = helpers

        self.addChangeListener(ScriptTabbedPane.TabsStateChanged())
        self.create_add_tab()

    def create_add_tab(self):
        self.add_tab = JButton("+", actionPerformed=self.add_clicked)
        self.add_tab.font = Font('Monospaced', Font.PLAIN, 18)
        self.add_tab.contentAreaFilled = False
        self.add_tab.border = None
        
        self.emptyTab = JPanel(BorderLayout())
        self.emptyTab.add(JLabel(ScriptTabbedPane.EMPTY_SCRIPT_TEXT, SwingConstants.CENTER), BorderLayout.CENTER)

        self.addTab(None, self.emptyTab)
        self.setTabComponentAt(0, self.add_tab)

    def add_clicked(self, event):
        idx = self.tabCount - 1
        title = 'New Script {}'.format(idx + 1)
        script = Script(self.extender, self.callbacks, self.helpers, title, True, '')
        new_tab = ScriptTabComponent(script)
        new_panel = ScriptPanel(script)
        self.add(new_panel, idx)
        self.setTabComponentAt(idx, new_tab)
        self.selectedIndex = idx


    class TabsStateChanged(ChangeListener):
        
        def stateChanged(self, event):
            # prevents the add tab from being selected apart from when there are no other tabs created (i.e. starting from fresh)
            # instead the tab next the add tab is selected
            tabbed_pane = event.source
            if tabbed_pane.tabCount > 1 and tabbed_pane.selectedIndex == tabbed_pane.tabCount - 1:
                tabbed_pane.selectedIndex = tabbed_pane.tabCount - 2


class ScriptTabComponent(TabComponentEditableTabMixin, TabComponentCloseableMixin, TabComponent):
    
    def __init__(self, script):
        super(ScriptTabComponent, self).__init__()
        self.script = script
        self.setText(self.script.title)
        self.close_button.font = Font('Dialog', Font.PLAIN, 16)
    

class ScriptPanel(JPanel):

    def __init__(self, script):
        self.script = script


class Gui(object):
    
    def __init__(self, extender, callbacks, helpers, scripts):
        self.panel = JPanel()
        self.tabs = ScriptTabbedPane(extender, callbacks, helpers, scripts)
        layout = BorderLayout()
        self.panel.setLayout(layout)
        self.panel.add(self.tabs)

    def build(self):
        return self.panel