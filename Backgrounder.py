import numpy as np
from PIL import Image
import pyglet


class Backgrounder:
    '''Создание и получение текстуры для фонов с различными градиентами'''
    def __init__(self, width, height):
        self.width, self.height = width, height
        self._conf = {
            'type': 'solid',
            'colors': [(0, 0, 0)]
        }
        self._render()
        self._make_sprite()
     
    def config(self, conf=None, **kwargs):
        if conf is None:
            conf = {}
        self._conf.update({**kwargs, **conf})
        self._render()
        self._make_sprite()
        
    def _render(self):
        '''Создание текстуры в зависимости от типа градиента'''
        width, height = self.width, self.height
        bg_type = self._conf['type']
        colors = self._conf['colors']
        
        x = y = None
        if bg_type != 'solid':
            x = np.arange(width)
            y = np.arange(height)
            x, y = np.meshgrid(x, y)
            center_x, center_y = width // 2, height // 2
        
        match bg_type:
            case 'solid':
                color = colors[0]
                img_array = np.full((height, width, 3), color, dtype=np.uint8)
            
            case 'linear':
                start_color, end_color = colors[:2]
                angle = self._conf.get('angle', 0)
                theta = np.radians(angle)
                
                x_norm = (x - center_x) / (width / 2)
                y_norm = (y - center_y) / (height / 2)
                proj = x_norm * np.cos(theta) + y_norm * np.sin(theta)
                dist = (proj + 1) / 2
                
                noise = np.random.uniform(-0.02, 0.02, dist.shape)
                dist = np.clip(dist + noise, 0, 1)
                
                r = (start_color[0] + (end_color[0] - start_color[0]) * dist).astype(np.uint8)
                g = (start_color[1] + (end_color[1] - start_color[1]) * dist).astype(np.uint8)
                b = (start_color[2] + (end_color[2] - start_color[2]) * dist).astype(np.uint8)
                img_array = np.dstack((r, g, b))
            
            case 'radial':
                center_color, outer_color = colors[:2]
                stretch = width / height
                
                dx = (x - center_x)
                dy = (y - center_y) * stretch
                max_radius = np.sqrt(center_x**2 + (center_y * stretch)**2)
                
                dist = np.sqrt(dx**2 + dy**2) / max_radius
                dist = np.clip(dist, 0, 1)
                
                noise = np.random.uniform(-0.02, 0.02, dist.shape)
                dist = np.clip(dist + noise, 0, 1)
                
                r = (center_color[0] + (outer_color[0] - center_color[0]) * dist).astype(np.uint8)
                g = (center_color[1] + (outer_color[1] - center_color[1]) * dist).astype(np.uint8)
                b = (center_color[2] + (outer_color[2] - center_color[2]) * dist).astype(np.uint8)
                img_array = np.dstack((r, g, b))
            
            case 'reflected':
                start_color, end_color = colors[:2]
                angle = self._conf.get('angle', 0)
                theta = np.radians(angle)
                
                x_norm = (x - center_x) / (width / 2)
                y_norm = (y - center_y) / (height / 2)
                proj = x_norm * np.cos(theta) + y_norm * np.sin(theta)
                dist = np.abs(proj)
                
                noise = np.random.uniform(-0.02, 0.02, dist.shape)
                dist = np.clip(dist + noise, 0, 1)
                
                r = (start_color[0] + (end_color[0] - start_color[0]) * dist).astype(np.uint8)
                g = (start_color[1] + (end_color[1] - start_color[1]) * dist).astype(np.uint8)
                b = (start_color[2] + (end_color[2] - start_color[2]) * dist).astype(np.uint8)
                img_array = np.dstack((r, g, b))
            
            case _:
                raise ValueError(f"Unsupported gradient type: {bg_type}")
        
        img = Image.fromarray(img_array, 'RGB')
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        self._texture = pyglet.image.ImageData(
            width, height, 'RGB', img.tobytes())
        
    def _make_sprite(self):
        try:
            self._sprite = pyglet.sprite.Sprite(self._texture, x=0, y=0)
        except AttributeError:
            pass
        
    def get_texture(self):
        return self._texture
    
    def draw(self):
        self._sprite.draw()