import pyglet 

import UIelements

PATH = 'menu_scene/'
development_scene = 'dev'
TEST_SCENE = None


class MainMenu(UIelements.Scene):
    '''Сцена главного меню игры'''
    def execute(self, cmd):
        if cmd == 'exit_game':
            pyglet.app.exit()
            return
        elif cmd == 'start_game':
            scene = UIelements.SceneConstructor(self.app).construct_scene(f'{PATH}select-on-game-menu.xml', SelectOnGameMenu)
            self.app.switch_scene(scene)
            return
        elif cmd == 'open_settings':
            scene = UIelements.SceneConstructor(self.app).construct_scene(f'{PATH}settings.xml', InfoMenu)
            self.app.switch_scene(scene)     
        elif cmd == "open_info":
            scene = UIelements.SceneConstructor(self.app).construct_scene(f'{PATH}info-menu.xml', InfoMenu)
            self.app.switch_scene(scene)
            return
        elif cmd == 'run_tests':
            scene = UIelements.SceneConstructor(self.app).construct_scene(f'{PATH}tester-menu.xml', TesterMenu)
            self.app.switch_scene(scene)
            return
        return super().execute(cmd)

class EscapeIsExit:
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
           self.app.switch_scene(get_start_scene(self.app))
        
        return super().on_key_press(symbol, modifiers)
  
class WithCancel:
    def execute(self, cmd):
        if cmd == "cancel":
            scene = self.ctx["prev_scene"]
            self.app.switch_scene(scene)
            return
        return super().execute(cmd)

class SelectOnGameMenu(EscapeIsExit, WithCancel, UIelements.Scene):
    '''Выбор в пункте меню играть'''
    def execute(self, cmd):
        return super().execute(cmd)

class SettingsMenu(EscapeIsExit, WithCancel, UIelements.Scene):
    '''Основное меню настроек'''
    def execute(self, cmd):
        return super().execute(cmd)

class InfoMenu(EscapeIsExit, WithCancel, UIelements.Scene):
    """Меню из раздела информации"""
    def execute(self, cmd):
        return super().execute(cmd)
    

class TesterMenu(EscapeIsExit, WithCancel, UIelements.Scene):
    '''Меню тестов приложений'''
    def execute(self, cmd):
        if cmd == 'hello':
            print('Привет, пидор')
            return
        elif cmd == 'temp-dev-scene':
            scene = TEST_SCENE
            self.app.switch_scene(scene)
            return
        elif cmd=="debug-mod":
            self.app.DEBUG = not self.app.DEBUG
            return

        return super().execute(cmd)

def get_start_scene(app) -> UIelements.Scene:
    return UIelements.SceneConstructor(app).construct_scene(f'{PATH}main-menu.xml', MainMenu)