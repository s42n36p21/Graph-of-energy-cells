from box_model import UIBox
import pyglet
import colorsys
from Background import Background
from Color import ColorMamager
from parsers import *

class UIEvents:
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

class UIElement(UIEvents):
    def __init__(self, element, properties, extra=None):
        self.box = UIBox(self, element, properties)

        id = get_param('id', element, properties)
        if id:
            self._id = id
        
        classes = get_param('class', element, properties)
        if classes:
            self._class = classes.split()
        
        bg = get_param('background', element, properties)
        if bg:
            self.bg = Background(self._box)
            self.bg.config(dict(
                type = get_param('background', element, properties, 'solid'),
                start_color = parse_color(get_param('start_color', element, properties)),
                stop_color = parse_color(get_param('stop_color', element, properties)),
                angle = get_param('angle', element, properties, 0)
            ))
            self.bg._sprite.x = self.box.bottom
            self.bg._sprite.y = self.box.left
        
    def move(self, dx, dy):
        if self.bg:
            self.bg._sprite.x += dx
            self.bg._sprite.y += dy

    def draw(self):
        if self.bg:
            self.bg.draw()

class TextUIELement(UIElement):
    def __init__(self, element, propertys, extra=None):
        super().__init__(element, propertys, extra)

        self.lable = pyglet.text.Label(
            text=get_param('text', element, propertys, ''),
            font_name=get_param('font', element, propertys),
            font_size=parse_expression(get_param('text', element, propertys, '1em')),
            color=parse_color(get_param('color', element, propertys, '#ffffff')),
            x=self._box._x,
            y=self._box._y,
            anchor_x=self._box._anchor_x,
            anchor_y=self._box._anchor_y,
        ) 

    def draw(self):
        super().draw()
        self.lable.draw()