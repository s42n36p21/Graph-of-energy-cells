import pyglet 

import UIelements

PATH = 'menu_scene/'

class MainMenu(UIelements.Scene):
    '''Сцена главного меню игры'''
    def execute(self, cmd):
        if cmd == 'exit_game':
            pyglet.app.exit()
            return
        elif cmd == 'run_tests':
            scene = UIelements.SceneConstructor(self.app).construct_scene(f'{PATH}tester-menu.xml', TesterMenu)
            self.app.switch_scene(scene)
            return
        return super().execute(cmd)

class TesterMenu(UIelements.Scene):
    '''Меню тестов приложений'''
    def execute(self, cmd):
        if cmd == 'hello':
            print('Привет, пидор')
            return
        elif cmd == 'temp-dev-scene':
            scene = UIelements.SceneConstructor(self.app).construct_scene(f'{PATH}tester-menu.xml', TesterMenu)
            self.app.switch_scene(scene)
            return
        elif cmd=="debug-mod":
            self.app.DEBUG = not self.app.DEBUG
            return

        return super().execute(cmd)
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            self.app.switch_scene(get_start_scene(self.app))
    
def get_start_scene(app) -> UIelements.Scene:
    return UIelements.SceneConstructor(app).construct_scene(f'{PATH}main-menu.xml', MainMenu)