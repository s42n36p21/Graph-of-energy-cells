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
        anchor_x = element.get('anchor_x', ctx.get('anchor_x', 'center'))
        anchor_y = element.get('anchor_y', ctx.get('anchor_y', 'center'))
        
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

        self.color = self._parse_color(element.get('color', ctx.get('color', '#ffffff')))

        self.label = pyglet.text.Label(
            text=element.get('text', ''),
            font_name=element.get('font', ctx.get('font', )),
            font_size=self._parse_expression(element.get('size', ctx.get('size', '10')), ctx),
            color=self.color,
            x=self._x,
            y=self._y,
            anchor_x=self._anchor_x,
            anchor_y=self._anchor_y,
            weight=element.get('weight', ctx.get('weight', 'normal'))    
        )
        if not element.get('text', ''):
            self.label.text = ' '
            self.label.text = ''

    def draw(self):
        if self._visible:
            self.label.draw()

class ColorManager:
    def __init__(self, owner: 'ButtonUIElement', start_color, stop_color, step=15, disable_color=None, active=True, check_hover=None):
        self.start_color = start_color
        self.stop_color = stop_color
        self.step = step
        self.progress = 0
        self.owner = owner
        
        if check_hover is None:
            self.check_hover = lambda: self.owner.is_hovered
        else:
            self.check_hover = check_hover

        self.disable_color = disable_color
        self.active = True
    
    def update(self):
        if not self.active:
            self.owner.label.color = self.disable_color
            return
        if self.check_hover():
            d = 1
        else:
            d = -1
            
        self.progress = max(0, min(self.progress+d, self.step))
        
        dist = self.progress / self.step
        try:
            self.owner.label.color = tuple([int((1-dist)*st + sp*dist) for st, sp in zip(self.start_color, self.stop_color)])
        except: pass
        return tuple([int((1-dist)*st + sp*dist) for st, sp in zip(self.start_color, self.stop_color)])
    def set_active(self, active):
        self.active = active

    
class ButtonUIElement(TextUIElement):
    def __init__(self, element: ET.Element, extra: Dict=None, ctx: Dict=None):
        super().__init__(element, extra=extra, ctx=ctx)
        
        color = self._parse_color(element.get('color', ctx.get('color', '#ffffff')))
        hover_color = self._parse_color(element.get('hover_color', ctx.get('hover_color', '#ffffff')))
        disable_color=self._parse_color(element.get('disable_color', ctx.get('disable_color', '#404040')))

        self.is_hovered = False
        self.color_manager = ColorManager(self, color, hover_color, disable_color=disable_color)
        
        self.scene = extra.get('scene')
        self.command = element.get('command')

        if element.get('active', ctx.get(element.get('active', 'True'))) == "False":
            self.color_manager.set_active(False)
        
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

class OutlinedRectangle:
    def __init__(self, x, y, width, height, border=1, 
                 color=(0, 0, 0, 0), border_color=(255, 255, 255, 255),
                 batch=None):

        
        # Создаем 4 линии для контура прямоугольника
        d = border/2
        self.lines = [
            # Нижняя линия
            pyglet.shapes.Line(x-d, y, x + width+d, y, border, border_color, batch=batch),
            # Правая линия
            pyglet.shapes.Line(x + width, y, x + width, y + height, border, border_color, batch=batch),
            # Верхняя линия
            pyglet.shapes.Line(x+d + width, y + height, x-d, y + height, border, border_color, batch=batch),
            # Левая линия
            pyglet.shapes.Line(x, y + height, x, y, border, border_color, batch=batch)
        ]
        self.color = border_color
    @property
    def color(self):
        return self.color
    @color.setter
    def color(self, color):
        for line in self.lines:
            line.color = color
    
    def draw(self):
        """Метод для отрисовки прямоугольника"""
        for line in self.lines:
            line.draw()

class CheckButton(UIElement):
    """Флажок с галочкой внутри"""
    def __init__(self, element: ET.Element, extra: Dict=None, ctx: Dict=None):
        super().__init__(element, extra=extra, ctx=ctx)
        
        self.size = self._parse_expression(element.get('size', ctx.get('size', '20px')), ctx)
        self.frame_color = self._parse_color(element.get('frame_color', ctx.get('frame_color', '#ffffff')))
        self.color = self._parse_color(element.get('color', ctx.get('color', '#ffffff')))
        self.checked = False
        hover_color = self._parse_color(element.get('hover_color', ctx.get('hover_color', '#ffffff')))
        self.frame_color_manager = ColorManager(self, self.frame_color, hover_color)
        
        self.batch = pyglet.graphics.Batch()
        self.vertices = []
        self.check_vertices = []
        
    def _create_shape(self):
        half = self.size / 2
        x = self._x - {'left': 0, 'center': half, 'right': self.size}[self._anchor_x]
        y = self._y - {'bottom': 0, 'center': half, 'top': self.size}[self._anchor_y]
        
        # Прямоугольник
        self.vertices = OutlinedRectangle(
            x, y, self.size, self.size, 1.5*self.size/10, color=(0,0,0,0), 
            border_color=self.frame_color, batch=self.batch
        )
        
        size = self.size
         
        dy = size / 10
        abs_x = self._x - size//2
        abs_y = self._y - size//2
        x1, y1 =  abs_x + size / 5, abs_y + 3*size / 5 - dy
        x2, y2 =  abs_x + 2*size / 5, abs_y + 2*size / 5 - dy
        x3, y3 =  abs_x + 4*size / 5, abs_y + 4*size / 5 - dy
        
        # Галочка (скрыта по умолчанию)
        d = dy/4*(2**.5)
            
        self.check_vertices = [
            pyglet.shapes.Line(x1,y1,x2+d,y2-d,
                                dy, color=self.color, batch=self.batch),
            pyglet.shapes.Line(x2,y2,x3,y3,
                                dy, color=self.color, batch=self.batch)
        ]
        
        for line in self.check_vertices:
            line.visible = self.checked
    
    def on_mouse_motion(self, x, y, dx, dy):
        half = self.size / 2
        btn_x = self._x - {'left': 0, 'center': half, 'right': self.size}[self._anchor_x]
        btn_y = self._y - {'bottom': 0, 'center': half, 'top': self.size}[self._anchor_y]
    
        self.is_hovered = (btn_x <= x <= btn_x + self.size and 
            btn_y <= y <= btn_y + self.size)
    
    def on_mouse_press(self, x, y, button, modifiers):
        
        if self.is_hovered:
            self.checked = not self.checked
            for line in self.check_vertices:
                line.visible = self.checked
            return True
        return False
    
    def get(self):
        return self.checked
    
    def draw(self):
        if not self.vertices:
            self._create_shape()
        self.vertices.color = self.frame_color_manager.update()
        self.batch.draw()

class Entry(TextUIElement):
    """Поле ввода текста с улучшенным управлением"""
    def __init__(self, element: ET.Element, extra: Dict=None, ctx: Dict=None):
        super().__init__(element, extra=extra, ctx=ctx)
        
        self.maxlen = int(element.get('maxlen', ctx.get('maxlen', '32')))
        self.hover_color = self._parse_color(
            element.get('hover_color', ctx.get('hover_color', '#00ff00'))
        )
        self.frame_color = self._parse_color(
            element.get('frame_color', ctx.get('frame_color', '#666666'))
        )
        
        self.active = False
        self.cursor_visible = True
        self.cursor_blink = 0.5
        self.cursor_timer = 0
        self.cursor_pos = len(self.label.text)
        
        # Для обработки зажатых клавиш
        self.key_repeat_delay = 0.5  # Задержка перед повтором
        self.key_repeat_interval = 0.05  # Интервал повтора
        self.key_repeat_timer = 0
        self.key_held = None  # Какая клавиша зажата
        
        # Линия будет растягиваться под максимальный текст
        self.line_width = self._calculate_max_line_width()
        self.line = pyglet.shapes.Line(
            self._x - self.line_width/2, 
            self._y - self.label.content_height/2,
            self._x + self.line_width/2,
            self._y - self.label.content_height/2,
            2, color=self.frame_color
        )
        self._update_cursor()
        
    def _calculate_max_line_width(self):
        """Вычисляет ширину линии для максимально возможного текста"""
        test_label = pyglet.text.Label(
            'W' * self.maxlen,  # 'W' - обычно самый широкий символ
            font_name=self.label.font_name,
            font_size=self.label.font_size,
            x=self._x,
            y=self._y,
            anchor_x='center',
            anchor_y='center'
        )
        return test_label.content_width
        
    def on_mouse_press(self, x, y, button, modifiers):
        
        # Активируем при клике в области элемента (учитываем высоту текста)
        text_height = self.label.font_size/2
        text_half_width = self.line_width/2
        
        
        self.active = (
            abs(x - self._x) < text_half_width and 
            abs(y - self._y) < text_height
        )
     
        
        if self.active:
            rel_x = x - (self._x - self.label.content_width/2)
            self.cursor_pos = min(len(self.label.text), max(0, int(rel_x / (self.label.content_width / max(1, len(self.label.text))))))
            self._update_cursor()
            
        self.line.color = self.hover_color if self.active else self.frame_color
        return self.active
    
    def on_text(self, text):
        if not self.active:
            return
            
        current = self.label.text
        
        if text == '\r':  # Enter
            self.active = False
            self.line.color = self.frame_color
        elif text == '\x08':  # Backspace
            self._handle_backspace()
        elif len(current) < self.maxlen and text.isprintable():
            self.label.text = current[:self.cursor_pos] + text + current[self.cursor_pos:]
            self.cursor_pos += 1
            
        self._update_cursor()
        
    def _handle_backspace(self):
        """Обработка backspace с возможностью зажатия"""
        if self.cursor_pos > 0:
            current = self.label.text
            self.label.text = current[:self.cursor_pos-1] + current[self.cursor_pos:]
            self.cursor_pos -= 1
            return True
        return False
        
    def _handle_delete(self):
        """Обработка delete с возможностью зажатия"""
        if self.cursor_pos < len(self.label.text):
            current = self.label.text
            self.label.text = current[:self.cursor_pos] + current[self.cursor_pos+1:]
            return True
        return False
        
    def on_key_press(self, symbol, modifiers):
        if not self.active:
            return
            
        # Запоминаем нажатую клавишу для повторения
        if symbol in (pyglet.window.key.BACKSPACE, pyglet.window.key.DELETE,
                     pyglet.window.key.LEFT, pyglet.window.key.RIGHT):
            self.key_held = symbol
            self.key_repeat_timer = self.key_repeat_delay
            
        # Обработка однократного нажатия
        if symbol == pyglet.window.key.LEFT:
            self.cursor_pos = max(0, self.cursor_pos - 1)
        elif symbol == pyglet.window.key.RIGHT:
            self.cursor_pos = min(len(self.label.text), self.cursor_pos + 1)
        elif symbol == pyglet.window.key.HOME:
            self.cursor_pos = 0
        elif symbol == pyglet.window.key.END:
            self.cursor_pos = len(self.label.text)
        elif symbol == pyglet.window.key.DELETE:
            self._handle_delete()
        elif symbol == pyglet.window.key.BACKSPACE:
            self._handle_backspace()
            
        self._update_cursor()
        
    def on_key_release(self, symbol, modifiers):
        # Сбрасываем зажатую клавишу
        if symbol == self.key_held:
            self.key_held = None
            
    def _update_cursor(self):
        # Вычисляем позицию курсора на основе текущего текста и позиции
        if len(self.label.text) == 0:
            text_before_cursor = ""
        else:
            text_before_cursor = self.label.text[:self.cursor_pos]
            
        # Создаем временный label для измерения ширины текста до курсора
        temp_label = pyglet.text.Label(
            text_before_cursor,
            font_name=self.label.font_name,
            font_size=self.label.font_size,
            x=self._x - self.label.content_width/2,
            y=self._y,
            anchor_x='left',
            anchor_y='center'
        )
        
        self.cursor_x = self._x - self.label.content_width/2 + temp_label.content_width
        self.cursor_y = self._y
        self.cursor_timer = 0
        self.cursor_visible = True
    def update(self, dt):
        if not self.active:
            return
            
        # Обновление мигания курсора
        self.cursor_timer += dt
        if self.cursor_timer >= self.cursor_blink:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible
            
        # Обработка зажатых клавиш
        if self.key_held is not None:
            self.key_repeat_timer -= dt
            if self.key_repeat_timer <= 0:
                self.key_repeat_timer = self.key_repeat_interval
                
                if self.key_held == pyglet.window.key.BACKSPACE:
                    if not self._handle_backspace():
                        self.key_held = None
                elif self.key_held == pyglet.window.key.DELETE:
                    if not self._handle_delete():
                        self.key_held = None
                elif self.key_held == pyglet.window.key.LEFT:
                    if self.cursor_pos > 0:
                        self.cursor_pos -= 1
                    else:
                        self.key_held = None
                elif self.key_held == pyglet.window.key.RIGHT:
                    if self.cursor_pos < len(self.label.text):
                        self.cursor_pos += 1
                    else:
                        self.key_held = None
                
                self._update_cursor()
                
    def draw(self):
        super().draw()
        self.line.draw()
        
        if self.active and self.cursor_visible:
            pyglet.shapes.Line(
                self.cursor_x, self._y - self.label.content_height/2,
                self.cursor_x, self._y + self.label.content_height/2,
                2, color=self.color
            ).draw()
    
    def get(self):
        return self.label.text

class RangeSlider(UIElement):
    """Ползунок для выбора значений"""
    def __init__(self, element: ET.Element, extra: Dict=None, ctx: Dict=None):
        super().__init__(element, extra=extra, ctx=ctx)
        
        self.width = self._parse_expression(element.get('width', ctx.get('width', '200px')), ctx)
        self.height = self._parse_expression(element.get('height', ctx.get('height', '5px')), ctx)
        self.thumb_radius = self._parse_expression(
            element.get('thumb_radius', ctx.get('thumb_radius', '10px')), ctx
        )
        
        self.frame_color = self._parse_color(
            element.get('frame_color', ctx.get('frame_color', '#666666'))
        )
        self.color = self._parse_color(element.get('color', ctx.get('color', '#ffffff')))
        self.hover_color = self._parse_color(
            element.get('hover_color', ctx.get('hover_color', '#00ff00'))
        )
        
        self.color_manager = ColorManager(self, self.color, self.hover_color)
        
        self.value = 0.5  # 0.0-1.0
        self.dragging = False
        self.is_hovered = False
        
    def on_mouse_press(self, x, y, button, modifiers):
        thumb_x = self._x - self.width/2 + self.value * self.width
        distance = ((x - thumb_x) ** 2 + (y - self._y) ** 2) ** 0.5
        if distance <= self.thumb_radius:
            self.dragging = True
            return True
        return False
    
    def on_mouse_release(self, x, y, button, modifiers):
        self.dragging = False
        return False
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.dragging:
            relative_x = max(0, min(x - (self._x - self.width/2), self.width))
            self.value = relative_x / self.width
            return True
        return False
    
    def on_mouse_motion(self, x, y, dx, dy):
        thumb_x = self._x - self.width/2 + self.value * self.width
        self.is_hovered = ((x - thumb_x) ** 2 + (y - self._y) ** 2) ** 0.5 <= self.thumb_radius
        
    def get(self):
        return self.value
    
    def draw(self):
        # Линия слайдера
        pyglet.shapes.Line(
            self._x - self.width/2, self._y,
            self._x + self.width/2, self._y,
            self.height, color=self.frame_color
        ).draw()
        
        pyglet.shapes.Circle(
            self._x - self.width/2, self._y, self.height/2,
            color=self.frame_color
        ).draw()
        
        pyglet.shapes.Circle(
            self._x + self.width/2, self._y, self.height/2,
            color=self.frame_color
        ).draw()
        
        # Ползунок
        thumb_x = self._x - self.width/2 + self.value * self.width
        color = self.color_manager.update()
        
        pyglet.shapes.Circle(
            thumb_x, self._y, self.thumb_radius,
            color=color
        ).draw()
        
        


class SelectorInRow(UIElement):
    """Переключатель опций"""
    def __init__(self, element: ET.Element, extra: Dict=None, ctx: Dict=None):
        super().__init__(element, extra=extra, ctx=ctx)
        
        self.options = element.get('options', '').split('|')
        self.index = int(element.get('default', ctx.get('default', '0')))
        self.color = self._parse_color(element.get('color', ctx.get('color', '#ffffff')))
        self.hover_color = self._parse_color(
            element.get('hover_color', ctx.get('hover_color', '#00ff00'))
        )
        
        self.max_width = self._get_max_width(element, ctx)
        self.arrow_size = self._parse_expression(
            element.get('arrow_size', ctx.get('arrow_size', '1em')), ctx
        )
        
        self.left_hover = False
        self.right_hover = False
        self.color_right = ColorManager(self,self.color,self.hover_color, check_hover=lambda: self.right_hover)
        self.color_left = ColorManager(self,self.color,self.hover_color, check_hover=lambda: self.left_hover)
        
        self.label = pyglet.text.Label(
            text=self.options[self.index],
            font_name=element.get('font', ctx.get('font', 'Arial')),
            font_size=self._parse_expression(element.get('size', ctx.get('size', '20')), ctx),
            color=self.color,
            x=self._x,
            y=self._y,
            anchor_x='center',
            anchor_y='center'
        )
    
    def _get_max_width(self, element, ctx):
        temp_lable = pyglet.text.Label(
            text=self.options[self.index],
            font_name=element.get('font', ctx.get('font', 'Arial')),
            font_size=self._parse_expression(element.get('size', ctx.get('size', '20')), ctx),
            color=self.color,
            x=self._x,
            y=self._y,
            anchor_x='center',
            anchor_y='center'
        )
        max_width = 0
        for text in self.options:
            temp_lable.text = text
            max_width = max(max_width, temp_lable._content_width)
        return max_width
    
    def on_mouse_press(self, x, y, button, modifiers):
        if self.left_hover:
            self.index = (self.index - 1) % len(self.options)
            self.label.text = self.options[self.index]
            return True
            
        if self.right_hover:
            self.index = (self.index + 1) % len(self.options)
            self.label.text = self.options[self.index]
            return True
            
        return False
    
    def on_mouse_motion(self, x, y, dx, dy):
        # Проверка левой стрелки
        left_triangle = [
            (self._x - self.label.font_size- self.max_width/2 - self.arrow_size, self._y),
            (self._x - self.label.font_size- self.max_width/2, self._y + self.arrow_size/2),
            (self._x - self.label.font_size- self.max_width/2, self._y - self.arrow_size/2)
        ]
        self.left_hover = self._point_in_triangle((x, y), left_triangle)
        
        # Проверка правой стрелки
        right_triangle = [
            (self._x + self.label.font_size + self.max_width/2 + self.arrow_size, self._y),
            (self._x + self.label.font_size + self.max_width/2, self._y + self.arrow_size/2),
            (self._x + self.label.font_size + self.max_width/2, self._y - self.arrow_size/2)
        ]
        self.right_hover = self._point_in_triangle((x, y), right_triangle)
    
    def _point_in_triangle(self, point, triangle):
        """Проверяет, находится ли точка внутри треугольника"""
        x, y = point
        x1, y1 = triangle[0]
        x2, y2 = triangle[1]
        x3, y3 = triangle[2]
        
        # Вычисляем площади
        area = 0.5 * abs((x2-x1)*(y3-y1) - (x3-x1)*(y2-y1))
        area1 = 0.5 * abs((x1-x)*(y2-y) - (x2-x)*(y1-y))
        area2 = 0.5 * abs((x2-x)*(y3-y) - (x3-x)*(y2-y))
        area3 = 0.5 * abs((x3-x)*(y1-y) - (x1-x)*(y3-y))
        
        return abs(area - (area1 + area2 + area3)) < 0.1
    
    def get(self):
        return (self.index, self.options[self.index])
    
    def draw(self):
        # Левая стрелка
        left_color = self.hover_color if self.left_hover else self.color

        left_arrow = pyglet.shapes.Triangle(
            x=self._x  - self.label.font_size- self.max_width/2- self.arrow_size, y=self._y,
            x2=self._x - self.label.font_size - self.max_width/2, y2=self._y + self.arrow_size/2,
            x3=self._x - self.label.font_size - self.max_width/2, y3=self._y - self.arrow_size/2,
            color=self.color_left.update()
        )
        left_arrow.draw()

        # Правая стрелка
        right_color = self.hover_color if self.right_hover else self.color
        right_arrow = pyglet.shapes.Triangle(
            x=self._x  + self.label.font_size+ self.max_width/2 + self.arrow_size, y=self._y,
            x2=self._x + self.label.font_size +self.max_width/2, y2=self._y - self.arrow_size/2,
            x3=self._x + self.label.font_size +self.max_width/2, y3=self._y + self.arrow_size/2,
            color=self.color_right.update()
        )
        right_arrow.draw()
        
        self.label.color=self.color
        self.label.draw()