import pyglet
import menu_scenes
import config
from Debuger import Debuger
from Background import Background


class Game(pyglet.window.Window):
    '''Окно игри, обработка событий и хранение состояний и сцен'''

    DEBUG = config.debug

    def __init__(self):
        super().__init__(fullscreen=True, caption="Graph of energy cells")
        
        self.debuger = Debuger(self)

        self.bg = Background(self)
        self.bg.config(config.background)
        
        self.scene = menu_scenes.get_start_scene(self)
        
        pyglet.clock.schedule_interval(self.update, 1/60)

    def switch_scene(self, new_scene):
        data = self.scene.get_record()
        new_scene.notify(ctx={"prev_scene": self.scene}, **data)
        self.scene = new_scene

    def on_draw(self):
        '''Обновление и отрисовка окна'''
        self.clear()
        self.bg.draw()
        self.scene.draw()
        
        if self.DEBUG:
            self.debuger.draw()

    def update(self, dt):
        '''Обновление игры'''
        self.scene.update(dt)
        
        if self.DEBUG:
            self.debuger.debug(dt)

    def on_mouse_press(self, x, y, button, modifiers):
        """Нажатие кнопки мыши"""
        self.scene.on_mouse_press(self, x, y, button, modifiers)
    
    def on_mouse_press(self, x, y, button, modifiers):
        """Нажатие кнопки мыши"""
        self.scene.on_mouse_press(self, x, y, button, modifiers)
    
    def on_mouse_release(self, x, y, button, modifiers):
        """Отпускание кнопки мыши"""
        self.scene.on_mouse_release(self, x, y, button, modifiers)
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Перемещение мыши с нажатой кнопкой"""
        self.scene.on_mouse_drag(self, x, y, dx, dy, buttons, modifiers)
    
    def on_mouse_enter(self, x, y):
        """Курсор мыши вошел в окно"""
        self.scene.on_mouse_enter(self, x, y)
    
    def on_mouse_leave(self, x, y):
        """Курсор мыши покинул окно"""
        self.scene.on_mouse_leave(self, x, y)
    
    def on_mouse_motion(self, x, y, dx, dy):
        """Перемещение мыши"""
        self.scene.on_mouse_motion(self, x, y, dx, dy)
    
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Прокрутка колесика мыши"""
        self.scene.on_mouse_scroll(self, x, y, scroll_x, scroll_y)
    
    def on_key_press(self, symbol, modifiers):
        """Нажатие клавиши"""
        self.scene.on_key_press(self, symbol, modifiers)
    
    def on_key_release(self, symbol, modifiers):
        """Отпускание клавиши"""
        self.scene.on_key_release(self, symbol, modifiers)
    
    def on_text(self, text):
        """Ввод текста (с учетом раскладки клавиатуры)"""
        self.scene.on_text(self, text)
    
    def on_text_motion(self, motion):
        """Движение текстового курсора"""
        self.scene.on_text_motion(self, motion)
    
    def on_text_motion_select(self, motion):
        """Движение текстового курсора с выделением"""
        self.scene.on_text_motion_select(self, motion)

if __name__ == "__main__":
    app = Game()
    pyglet.app.run()