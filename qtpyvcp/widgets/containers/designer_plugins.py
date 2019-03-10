from qtpyvcp.widgets.qtdesigner import _DesignerPlugin, _PluginExtension

from frame import VCPFrame
class VCPFramePlugin(_DesignerPlugin):
    def pluginClass(self):
        return VCPFrame
    def isContainer(self):
        return True

from embedded_ui import EmbeddedUI
class EmbeddedUIPlugin(_DesignerPlugin):
    def pluginClass(self):
        return EmbeddedUI
