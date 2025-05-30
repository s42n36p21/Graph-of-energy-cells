import time
import pyglet


class FPS:
    def __init__(self, average_time=1.0):
        """
        Инициализация счетчика FPS.
        
        :param average_time: промежуток времени (в секундах) для усреднения FPS
        """
        self._frame_times = []  # Список временных меток кадров
        self.average_time = average_time
        self.current_fps = 0
    
    def update(self, dt):
        """Вызывается каждый кадр с временем, прошедшим с предыдущего кадра."""
        current_time = sum(self._frame_times) + dt if self._frame_times else dt
        self._frame_times.append(dt)
        
        # Удаляем кадры, которые выходят за пределы временного окна усреднения
        while current_time > self.average_time:
            current_time -= self._frame_times.pop(0)
        
        # Рассчитываем FPS как количество кадров в окне, деленное на длину окна
        if current_time > 0:
            self.current_fps = len(self._frame_times) / current_time
        else:
            self.current_fps = 0
    
    def get_fps(self):
        """Возвращает текущее среднее значение FPS (float)."""
        return self.current_fps

class Debuger:
    def __init__(self, app):
        self.app = app
        self._start_time = time.time()
        self.update_counter = 0
        self.fps = FPS()
        self.console = ''

        self.debug_text = pyglet.text.Label(
            text='',
            font_name='Arial',
            font_size=20,
            color=(255, 255, 255, 255),
            x=10,
            y=self.app.height - 10,
            anchor_x='left',
            anchor_y='top',
            multiline=True,  # Включаем многострочный режим
            width=self.app.width
        )
    def log(self, *msg, sep=' ', end='\n'):
        res = sep.join(msg) + '\n'
        self.console += res 
    
    def debug(self, dt):
        self.update_counter += 1
        self.fps.update(dt)

        fps = f"FPS: {int(self.fps.get_fps())}"
        time_elapsed = f"Run time: {round((time.time()-self._start_time), 3)}s"
        update_count = f"Updates: {self.update_counter}"
        scene_name = f"Scene: {self.app.scene.__class__.__name__}"
        objects_count = f"Objects: {len(self.app.scene.units)}"
        game_version = f"Version: 0.3-dev"

        self.debug_text.text = f"{fps}\n{time_elapsed}\n{update_count}\n{scene_name}\n{objects_count}\n{game_version}\n\n{self.console}"

    def draw(self):
        self.debug_text.draw()