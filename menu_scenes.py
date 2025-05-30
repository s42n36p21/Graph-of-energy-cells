import pyglet 

from Scene import Scene, SceneConstructor

PATH = 'menu_scene/'
development_scene = 'dev'
TEST_SCENE = None


class MainMenu(Scene):
    '''Сцена главного меню игры'''
    def execute(self, cmd):
        if cmd == 'exit_game':
            pyglet.app.exit()
            return
        elif cmd == 'start_game':
            scene = SceneConstructor(self.app).construct_scene(f'{PATH}select-on-game-menu.xml', SelectOnGameMenu)
            self.app.switch_scene(scene)
            return
        elif cmd == 'open_settings':
            scene = SceneConstructor(self.app).construct_scene(f'{PATH}settings.xml', InfoMenu)
            self.app.switch_scene(scene)     
            return 
        elif cmd == "open_info":
            scene = SceneConstructor(self.app).construct_scene(f'{PATH}info-menu.xml', InfoMenu)
            self.app.switch_scene(scene)
            return
        elif cmd == 'run_tests':
            scene = SceneConstructor(self.app).construct_scene(f'{PATH}tester-menu.xml', TesterMenu)
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

class SelectOnGameMenu(EscapeIsExit, WithCancel, Scene):
    '''Выбор в пункте меню играть'''
    def execute(self, cmd):
        return super().execute(cmd)

class SettingsMenu(EscapeIsExit, WithCancel, Scene):
    '''Основное меню настроек'''
    def execute(self, cmd):
        return super().execute(cmd)

class InfoMenu(EscapeIsExit, WithCancel, Scene):
    """Меню из раздела информации"""
    def execute(self, cmd):
        return super().execute(cmd)
    
class DevMenu(InfoMenu):
     def execute(self, command):
        if command == "show_values":
            values = [
                f"CheckButton: {self.units[0].get()}",
                f"Entry: '{self.units[1].get()}'",
                f"Slider: {self.units[2].get()}",
                f"Selector: {self.units[3].get()})"
            ]
            self.app.debuger.log("\n".join(values))

class TesterMenu(EscapeIsExit, WithCancel, Scene):
    '''Меню тестов приложений'''
    def execute(self, cmd):
        if cmd == 'hello':
            self.app.debuger.log('Привет, пидор')
            return
        elif cmd == 'temp-dev-scene':
            scene = SceneConstructor(self.app).construct_scene(f'{PATH}dev.xml', DevMenu)
            self.app.switch_scene(scene)
            return
        elif cmd=="debug-mod":
            self.app.DEBUG = not self.app.DEBUG
            return

        return super().execute(cmd)

def get_start_scene(app) -> Scene:
    return SceneConstructor(app).construct_scene(f'{PATH}main-menu.xml', MainMenu)