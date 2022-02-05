from javax.swing import JTabbedPane, JPanel, JButton, JLabel, SwingConstants, JOptionPane, GroupLayout, JCheckBox
from javax.swing.event import ChangeListener, DocumentListener
from javax.swing.LayoutStyle.ComponentPlacement import RELATED, UNRELATED
from java.awt import BorderLayout, Font
from uicomponents import BurpUI, TabComponent, TabComponentEditableTabMixin, TabComponentCloseableMixin, TabComponentCloseListener
from models import Script
from utils import bytearray_to_string


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
        script = Script(self.extender, self.callbacks, self.helpers, title, True, '# hello world')
        new_tab = ScriptTabComponent(script)
        new_tab.tabbed_pane = self
        new_tab.addCloseListener(ScriptTabbedPane.ScriptTabCloseCloseListener(self))
        new_panel = ScriptPanel(script, self.callbacks)
        self.add(new_panel, idx)
        self.setTabComponentAt(idx, new_tab)
        self.selectedIndex = idx


    class ScriptTabCloseCloseListener(TabComponentCloseListener):

        def __init__(self, tabbedpane):
            self.tabbed_pane = tabbedpane 

        def tabClose(self, event):
            result = JOptionPane.showConfirmDialog(None, 'Are you sure you want to close \'{}\' ?'.format(event.source.text), 
                                                "Close Tab", 
                                                JOptionPane.YES_NO_OPTION, 
                                                JOptionPane.QUESTION_MESSAGE)
            if result == JOptionPane.YES_OPTION:        
                idx = self.tabbed_pane.indexOfTabComponent(event.source)
                self.tabbed_pane.remove(idx)


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
        self.text = self.script.title
        self.close_button.font = Font('Dialog', Font.PLAIN, 16)
    

class ScriptPanel(JPanel, DocumentListener):

    def __init__(self, script, callbacks):
        self.script = script
        self.layout = GroupLayout(self)
        self.setLayout(self.layout)
        self.enabledCheckbox = JCheckBox('Enabled', self.script.enabled, itemStateChanged=self.enabled_changed)
        self.scriptLabel = JLabel('Script Content:')
        self.scriptEditor = callbacks.createTextEditor()
        self.scriptEditor.text = script.content
        self.scriptText = self.scriptEditor.component
        self.compileButton = JButton('Compile', actionPerformed=self.compile)
        self.outputLabel = JLabel('Output:')
        self.outputEditor = callbacks.createTextEditor()
        self.outputEditor.editable = False
        self.outputText = self.outputEditor.component
        self.clearOutputButton = JButton('Clear', actionPerformed=self.clear_output)

        self.layout.autoCreateGaps = True
        self.layout.autoCreateContainerGaps = True
        self.layout.setHorizontalGroup(self.layout.createParallelGroup()
                                            .addGroup(self.layout.createSequentialGroup()
                                                .addComponent(self.enabledCheckbox)
                                                .addPreferredGap(UNRELATED)
                                            )
                                            .addGroup(self.layout.createParallelGroup()
                                              .addComponent(self.scriptLabel)
                                              .addComponent(self.scriptText)
                                              .addComponent(self.compileButton)
                                              .addComponent(self.outputLabel)
                                              .addComponent(self.outputText)
                                              .addComponent(self.clearOutputButton)  
                                            )
                                        )

        self.layout.setVerticalGroup(self.layout.createSequentialGroup()
                                            .addGroup(self.layout.createParallelGroup()
                                                .addComponent(self.enabledCheckbox)
                                            )
                                            .addGroup(self.layout.createSequentialGroup()
                                                .addComponent(self.scriptLabel)
                                                .addComponent(self.scriptText)
                                                .addComponent(self.compileButton)
                                                .addComponent(self.outputLabel)
                                                .addComponent(self.outputText)  
                                                .addComponent(self.clearOutputButton) 
                                            )
                                        )

        BurpUI.get_textarea(self.scriptEditor).document.addDocumentListener(self)

    def enabled_changed(self, event):
        self.script.enabled = self.enabledCheckbox.isSelected()

    def clear_output(self, event):
        self.outputEditor.text = ''

    def compile(self, event):
        self.script.content = bytearray_to_string(self.scriptEditor.text)
        self.script.compile(self.outputEditor)

    def changedUpdate(self, event):
        pass

    def insertUpdate(self, event):
        self._can_compile(event)
    
    def removeUpdate(self, event):
        self._can_compile(event)

    def _can_compile(self, event):
        self.compileButton.enabled = event.document.length > 0


class GUI(object):
    
    def __init__(self, extender, callbacks, helpers, scripts):
        self.panel = JPanel()
        self.tabs = ScriptTabbedPane(extender, callbacks, helpers, scripts)
        layout = BorderLayout()
        self.panel.setLayout(layout)
        self.panel.add(self.tabs)

    def build(self):
        return self.panel