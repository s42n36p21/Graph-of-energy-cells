import time

import pyglet

import menu_scenes
from Debuger import Debuger
from Backgrounder import Backgrounder


class Game(pyglet.window.Window):
    '''Окно игри, обработка событий и хранение состояний и сцен'''

    DEBUG = False

    def __init__(self):
        super().__init__(fullscreen=True, caption="Graph of energy cells")
        
        self.debuger = Debuger(self)

        self.bg = Backgrounder(self.width, self.height)
        self.bg.config(type='radial', 
                       colors=[(32, 32, 32), (0, 0, 0)],
                       #colors=[(255,255,0), (0,0,255)]
                       )
        
        self.scene = menu_scenes.get_start_scene(self)
        
        pyglet.clock.schedule_interval(self.update, 1/60)

    def on_draw(self):
        '''Обновление и отрисовка окна'''
        self.clear()
        self.bg.draw()
        self.scene.draw()
        if self.DEBUG:
            self.debuger.draw()
        
    def on_mouse_press(self, x, y, button, modifiers):
        '''Нажатые клавишы мыши'''
        self.scene.on_mouse_press(x, y, button, modifiers)
        
    def on_mouse_motion(self, x, y, dx, dy):
        '''Движение мыши'''
        self.scene.on_mouse_motion(x, y, dx, dy)

    def update(self, dt):
        '''Обновление игры'''
        self.scene.update(dt)
        if self.DEBUG:
            self.debuger.debug(dt)

    def on_key_press(self, symbol, modifiers):
        self.scene.on_key_press(symbol, modifiers)

    def switch_scene(self, new_scene):
        data = self.scene.get_record()
        new_scene.notify(ctx={"prev_scene": self.scene}, **data)
        self.scene = new_scene


if __name__ == "__main__":
    app = Game()
    pyglet.app.run()