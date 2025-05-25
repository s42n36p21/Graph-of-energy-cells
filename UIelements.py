import re
from typing import Any, Dict, Tuple
import xml.etree.ElementTree as ET

import pyglet

class SceneEvents:
    def on_mouse_press(self, x, y, button, modifiers):
        """Нажатие кнопки мыши"""
    
    def on_mouse_release(self, x, y, button, modifiers):
        """Отпускание кнопки мыши"""
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Перемещение мыши с нажатой кнопкой"""
    
    def on_mouse_enter(self, x, y):
        """Курсор мыши вошел в окно"""
    
    def on_mouse_leave(self, x, y):
        """Курсор мыши покинул окно"""
    
    def on_mouse_motion(self, x, y, dx, dy):
        """Перемещение мыши"""
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Прокрутка колесика мыши"""
    
    def on_key_press(self, symbol, modifiers):
        """Нажатие клавиши"""
    
    def on_key_release(self, symbol, modifiers):
        """Отпускание клавиши"""
    
    def on_text(self, text):
        """Ввод текста (с учетом раскладки клавиатуры)"""
    
    def on_text_motion(self, motion):
        """Движение текстового курсора"""
    
    def on_text_motion_select(self, motion):
        """Движение текстового курсора с выделением"""
    
    def draw(self):
        """Отрисовка элемента на окне"""
    
    def update(self, dt):
        """Обновление элемента"""

class UIElement(SceneEvents):
    '''Базовый UIElement'''
    def __init__(self, element: ET.Element, extra: Dict=None, ctx: Dict=None):
        x = element.get('x', ctx.get('x', '0.5vw'))
        y = element.get('y', ctx.get('y', '0.5vh'))
        anchor_x = element.get('anchore_x', 'center')
        anchor_y = element.get('anchore_y', 'center')
        
        self._x = self._parse_expression(x, ctx)
        self._y = self._parse_expression(y, ctx)
        self._anchor_x = anchor_x
        self._anchor_y = anchor_y
        self._visible = True
    
    @staticmethod
    def _parse_color(color_hex: str) -> Tuple[int, int, int, int]:
        """Преобразует hex-цвет в tuple (R, G, B, A)"""
        color_hex = color_hex.lstrip('#')
        r = int(color_hex[0:2], 16)
        g = int(color_hex[2:4], 16)
        b = int(color_hex[4:6], 16)
        return (r, g, b, 255)  
    
    @staticmethod
    def _parse_expression(expression: str, ctx: Dict):
        def replace_units(match):
            value = match.group(1) or '1'
            unit = match.group(2)

            if unit == 'px':
                return value
            elif unit in ['vh','vw', 'em', 'rem', '%']:
                return f'{value}*{ctx[unit]}'
            else:
                return match.group(0)
    
        allowed_names = {
        'min': min,
        'max': max,
        'abs': abs,
        'round': round,
        }
    
        pattern = r'([\d.]*\.?\d+)(px|vw|vh|em|rem|%)'
        processed_expr = re.sub(pattern, replace_units, expression)
        
        return eval(processed_expr, {'__builtins__': None}, allowed_names)
    
    def is_visible(self):
        return self._visible
    
    def set_visible(self):
        self._visible = True
    
    def set_unvisible(self):
        self._visible = False
        
class TextUIElement(UIElement):
    """Простой однострочный текст, написанный на экране"""
    def __init__(self, element: ET.Element, extra: Dict=None, ctx: Dict=None):
        super().__init__(element, extra=extra, ctx=ctx)
        
        self.label = pyglet.text.Label(
            text=element.get('text', ''),
            font_name=element.get('font', ctx.get('font', )),
            font_size=self._parse_expression(element.get('size', ctx.get('size', '10')), ctx),
            color=self._parse_color(element.get('color', ctx.get('color', '#ffffff'))),
            x=self._x,
            y=self._y,
            anchor_x=self._anchor_x,
            anchor_y=self._anchor_y,
            weight=ctx.get('weight', ctx.get('weight', 'normal'))    
        )
    
    def draw(self):
        if self._visible:
            self.label.draw()

class ColorManager:
    def __init__(self, owner: 'ButtonUIElement', start_color, stop_color, step=15):
        self.start_color = start_color
        self.stop_color = stop_color
        self.step = step
        self.progress = 0
        self.owner = owner
        
    def update(self):
        if self.owner.is_hovered:
            d = 1
        else:
            d = -1
            
        self.progress = max(0, min(self.progress+d, self.step))
        
        dist = self.progress / self.step
        self.owner.label.color = tuple([int((1-dist)*st + sp*dist) for st, sp in zip(self.start_color, self.stop_color)])
    
class ButtonUIElement(TextUIElement):
    def __init__(self, element: ET.Element, extra: Dict=None, ctx: Dict=None):
        super().__init__(element, extra=extra, ctx=ctx)
        
        color = self._parse_color(element.get('color', ctx.get('color', '#ffffff')))
        hover_color = self._parse_color(element.get('hover_color', ctx.get('hover_color', '#ffffff')))
        
        self.is_hovered = False
        self.color_manager = ColorManager(self, color, hover_color)
        
        self.scene: 'Scene' = extra.get('scene')
        self.command = element.get('command')
        
    def check_hover(self, x: int, y: int) -> bool:
        left = self._x - (self.label.content_width * {'left': 0, 'center': 0.5, 'right': 1}[self._anchor_x])
        right = left + self.label.content_width
        bottom = self._y - (self.label.content_height * {'baseline': 0, 'center': 0.5, 'top': 1}[self._anchor_y])
        top = bottom + self.label.content_height
        
        self.is_hovered = (left <= x <= right) and (bottom <= y <= top)
        return self.is_hovered
    
    def on_mouse_motion(self, x, y, dx, dy):
        super().on_mouse_motion(x, y, dx, dy)
        
        self.check_hover(x, y)
        
        
    def on_mouse_press(self, x, y, button, modifiers):
        super().on_mouse_press(x, y, button, modifiers)
        if button == pyglet.window.mouse.LEFT and self.is_hovered:
            if self.command:
                self.scene.execute(self.command)
    
    def draw(self):
        self.color_manager.update()
        super().draw()

class Scene(SceneEvents):
    '''Сцена игры, на ней находяться все UI элементы'''
    def __init__(self, app):
        self.app = app

    def update(self, dt):
        for unit in self.units:
            unit.update(dt)
    
    def on_mouse_motion(self, x, y, dx, dy):
        for unit in self.units:
            unit.on_mouse_motion(x, y, dx, dy)
    
    def draw(self):
        for unit in self.units:
            unit.draw()
    
    def on_mouse_press(self, x, y, button, modifiers):
        for unit in self.units:
            unit.on_mouse_press(x, y, button, modifiers)
    
    def attach(self, units):
        self.units = units
        
    def execute(self, cmd):
        '''Исполнитель команд'''
        print(f'Была вызванна команда: <{cmd}>')

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
                
            self.create_unit_from_xml(child, ctx)
            
            if child.tag == 'list':
                for index, child_li in enumerate(child):
                    li_ctx = {**child_ctx, **child.attrib}
                    li_ctx['y'] = li_ctx['y'] + f'- {index}*({li_ctx['pady']})'
                    self.create_unit_from_xml(child_li, li_ctx)
                return
            
            self.create_units_from_xml(child, {**child_ctx, **child.attrib})
            
    def create_unit_from_xml(self, elem, ctx):
        child = elem
        if child.tag == 'text':
            self.units.append(TextUIElement(child, ctx=ctx))
    
        elif child.tag == 'button':
            self.units.append(ButtonUIElement(child, ctx=ctx, extra={'scene': self.scene}))
