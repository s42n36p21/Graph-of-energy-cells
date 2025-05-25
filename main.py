import pyglet

import Backgrounder
import UIelements

class MainMenu(UIelements.Scene):
    '''Сцена главного меню игры'''
    def execute(self, cmd):
        if cmd == 'exit_game':
            pyglet.app.exit()
            return
        return super().execute(cmd)

class Game(pyglet.window.Window):
    '''Окно игри, обработка событий и хранение состояний и сцен'''
    def __init__(self):
        super().__init__(fullscreen=True, caption="Graph of energy cells")
        
        self.bg = Backgrounder.Backgrounder(self.width, self.height)
        self.bg.config(type='radial', 
                       colors=[(32, 32, 32), (0, 0, 0)]
                       )
        
        self.scene = UIelements.SceneConstructor(self).construct_scene('main-menu.xml', MainMenu)
        
        pyglet.clock.schedule_interval(self.update, 1/60)

    def on_draw(self):
        '''Обновление и отрисовка окна'''
        self.clear()
        self.bg.draw()
        self.scene.draw()
        
    def on_mouse_press(self, x, y, button, modifiers):
        '''Нажатые клавишы мыши'''
        self.scene.on_mouse_press(x, y, button, modifiers)
        
    def on_mouse_motion(self, x, y, dx, dy):
        '''Движение мыши'''
        self.scene.on_mouse_motion(x, y, dx, dy)

    def update(self, dt):
        '''Обновление игры'''
        self.scene.update(dt)


if __name__ == "__main__":
    app = Game()
    pyglet.app.run()