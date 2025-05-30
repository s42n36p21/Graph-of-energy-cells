import json
import pyglet
from UIelements import *
from typing import Any, Dict, Tuple
import xml.etree.ElementTree as ET

class Scene(SceneEvents):
    '''Сцена игры, на ней находяться все UI элементы'''
    def __init__(self, app):
        self.app = app
        self.ctx = {}

    def update(self, dt):
        for unit in self.units:
            unit.update(dt)
    
    def on_mouse_motion(self, x, y, dx, dy):
        for unit in self.units:
            unit.on_mouse_motion(x, y, dx, dy)
            self.ctx.update({"on_mouse_motion": (x, y, dx, dy)})
    
    def draw(self):
        for unit in self.units:
            unit.draw()
    
    def on_mouse_press(self, x, y, button, modifiers):
        for unit in self.units:
            unit.on_mouse_press(x, y, button, modifiers)
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        for unit in self.units:
            unit.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
    
    def on_mouse_release(self, x, y, button, modifiers):
        for unit in self.units:
            unit.on_mouse_release(x, y, button, modifiers)

    def on_text(self, text):
        for unit in self.units:
            unit.on_text(text)

    
    def attach(self, units):
        self.units = units
        
    def execute(self, cmd):
        '''Исполнитель команд'''
        self.app.debuger.log(f'Была вызванна команда: <{cmd}>')

    def get_record(self):
        return self.ctx
    
    def on_key_press(self, symbol, modifiers):
        for unit in self.units:
            unit.on_key_press(symbol, modifiers)
            
    def on_key_release(self, symbol, modifiers):
        for unit in self.units:
            unit.on_key_release(symbol, modifiers)

    def notify(self, **kwargs):
        self.ctx.update(kwargs['ctx'])
        if (task:=kwargs.get("on_mouse_motion")):
            self.on_mouse_motion(*task)
    
   

class SceneConstructor:
    TYPE_OF_THE_SCENE_CONFIGURATION_FILE = 'xml'
    
    def __init__(self, window):
        self.window = window
    
    def construct_scene(self, path, scene=Scene):
        root = self.load(path)
        self.scene = scene(self.window)
        self.units = []
        self.create_units(root)
        self.scene.attach(self.units)
        return self.scene
    
    def load(self, path):
        if self.TYPE_OF_THE_SCENE_CONFIGURATION_FILE == 'xml':
            return self.load_from_xml(path)
    
    def load_from_xml(self, path):
        """Загружает описание меню из XML файла"""
        tree = ET.parse(path)
        return tree.getroot()

    def create_units(self, root):
        """Создание юнитов из сцены"""
        if self.TYPE_OF_THE_SCENE_CONFIGURATION_FILE == 'xml':
            self.create_units_from_xml(root)
            
    def create_units_from_xml(self, root, ctx=None):
        print(ctx)
        if ctx is None:
            ctx = {
                'vw': self.window.width,
                'vh': self.window.height
            }
        
        for child in root:
            child_ctx = ctx.copy()
            size = child.get('size')
            if size is not None:
                child_ctx['em'] = str(UIElement._parse_expression(size, child_ctx))
            
            if child.tag == 'link':
                if style:=child.get('style'):
                    ctx.update(self.load_style_from_json(style))
            self.create_unit_from_xml(child, child_ctx)
            
            if child.tag == 'list':
                for index, child_li in enumerate(child):
                    li_ctx = {**child_ctx, **child.attrib}
                    # Исправление синтаксиса для вычисления позиции
                    li_ctx['y'] = f"{li_ctx.get('y', '0.5vh')} - {index}*({li_ctx.get('pady', '0')})"
                    li_ctx['x'] = f"{li_ctx.get('x', '0.5vw')} + {index}*({li_ctx.get('padx', '0')})"
                    self.create_unit_from_xml(child_li, li_ctx)
                    self.create_units_from_xml(child_li, li_ctx)
                continue  # Продолжаем обработку после списка
            
            # Рекурсивный вызов для дочерних элементов
            if len(child) > 0:
                self.create_units_from_xml(child, {**ctx, **child_ctx, **child.attrib})
            
    def create_unit_from_xml(self, elem, ctx):
        extra = {'scene': self.scene}
        
        if elem.tag == 'text':
            self.units.append(TextUIElement(elem, ctx=ctx))
    
        elif elem.tag == 'button':
            self.units.append(ButtonUIElement(elem, ctx=ctx, extra=extra))

        # Новые элементы
        elif elem.tag == 'checkbutton':
            self.units.append(CheckButton(elem, ctx=ctx, extra=extra))
            
        elif elem.tag == 'entry':
            self.units.append(Entry(elem, ctx=ctx, extra=extra))
            
        elif elem.tag == 'rangeslider':
            self.units.append(RangeSlider(elem, ctx=ctx, extra=extra))
            
        elif elem.tag == 'selector_in_row':
            self.units.append(SelectorInRow(elem, ctx=ctx, extra=extra))
    
    def load_style_from_json(self, style):
        with open(style, 'r') as file:
            return json.load(file)