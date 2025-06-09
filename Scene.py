import xml.etree.ElementTree as ET
from css_parser import CSSParser
from ui_element import UIEvents

class Scene(UIEvents):
    def __init__(self, app):
        self.app = app
        self.ctx = {}
        self.units = []
    
    def attach(self, units):
        self.units = units
        
    def execute(self, cmd):
        self.app.debuger.log(f'Command executed: <{cmd}>')

    def get_record(self):
        return self.ctx

    def notify(self, **kwargs):
        self.ctx.update(kwargs['ctx'])
        if (task:=kwargs.get("on_mouse_motion")):
            self.on_mouse_motion(*task)

    def on_mouse_press(self, x, y, button, modifiers):
        for unit in self.units:
            unit.on_mouse_press(x, y, button, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        for unit in self.units:
            unit.on_mouse_release(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        for unit in self.units:
            unit.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_enter(self, x, y):
        for unit in self.units:
            unit.on_mouse_enter(x, y)

    def on_mouse_leave(self, x, y):
        for unit in self.units:
            unit.on_mouse_leave(x, y)

    def on_mouse_motion(self, x, y, dx, dy):
        for unit in self.units:
            unit.on_mouse_motion(x, y, dx, dy)
            self.ctx.update({"on_mouse_motion": (x, y, dx, dy)})

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        for unit in self.units:
            unit.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_key_press(self, symbol, modifiers):
        for unit in self.units:
            unit.on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        for unit in self.units:
            unit.on_key_release(symbol, modifiers)

    def on_text(self, text):
        for unit in self.units:
            unit.on_text(text)

    def on_text_motion(self, motion):
        for unit in self.units:
            unit.on_text_motion(motion)

    def on_text_motion_select(self, motion):
        for unit in self.units:
            unit.on_text_motion_select(motion)

    def draw(self):
        for unit in self.units:
            unit.draw()

    def update(self, dt):
        for unit in self.units:
            unit.update(dt)


class SceneConstructor:
    def __init__(self, app):
        self.app = app
        self.root_ctx = {
            'vw': self.app.width,
            'vh': self.app.height,
            'x': '0',
            'y': '0',
            "rem": "1vh / 18",
            "em": "1rem"
        }
    
    def construct_scene(self, path, scene=Scene):
        self.units = []
        root = self.load_scene(path)
        self.create_element(root, self.root_ctx)
    
    def load_scene(self, path):
        tree = ET.parse(path)
        return tree.getroot()

    def create_element(self, element: ET.ElementTree, parent_properties):
        if (style:=element.get("style")):
            css_parser = CSSParser()
            css_parser.parse_file(style)
            css_parser.get_stylesheet()