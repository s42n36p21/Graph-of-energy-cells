import numpy as np
from PIL import Image
import pyglet
from typing import Dict, Tuple, Optional


class Background:
    """
    A class for creating and managing background textures with various gradient types.

    Attributes:
        width (int): The width of the background texture.
        height (int): The height of the background texture.
        _config (Dict): Configuration dictionary for the background.
        _texture (pyglet.image.ImageData): The generated texture.
        _sprite (pyglet.sprite.Sprite): The sprite using the generated texture.
    """

    def __init__(self, app):
        """
        Initialize the Background with the application dimensions.

        Args:
            app: The application object containing width and height attributes.
        """
        self.width, self.height = app.width, app.height
        self._config = {}
        self._texture = None
        self._sprite = None

    def config(self, conf: Optional[Dict] = None) -> None:
        """
        Update the background configuration and regenerate the texture.

        Args:
            conf (Optional[Dict]): Configuration dictionary. If None, uses empty dict.
        """
        if conf is None:
            conf = {}
        self._config.update(conf)
        
        self._render()
        self._make_sprite()
        
    def _render(self) -> None:
        """
        Render the texture based on the current configuration.
        
        The gradient type is determined by the 'type' key in the configuration.
        Supported types: 'solid', 'linear', 'radial', 'reflected'.
        """
        width, height = self.width, self.height
        bg_type = self._config.get('type', 'solid')
        start_color = self._config.get('start_color', (0,)*3)
        stop_color = self._config.get('stop_color', (0,)*3)
        angle = self._config.get('angle', 0)
    
        colors = start_color, stop_color    
        x = y = None
        
        # Prepare coordinates if needed for gradient calculations
        if bg_type != 'solid':
            x = np.arange(width)
            y = np.arange(height)
            x, y = np.meshgrid(x, y)
            center_x, center_y = width // 2, height // 2
        
        # Generate image array based on gradient type
        match bg_type:
            case 'solid':
                img_array = self._create_solid_gradient(colors[0], height, width)
            
            case 'linear':
                img_array = self._create_linear_gradient(
                    x, y, center_x, center_y, width, height, 
                    colors[0], colors[1], angle)
            
            case 'radial':
                img_array = self._create_radial_gradient(
                    x, y, center_x, center_y, width, height, 
                    colors[0], colors[1])
            
            case 'reflected':
                img_array = self._create_reflected_gradient(
                    x, y, center_x, center_y, width, height, 
                    colors[0], colors[1], angle)
            
            case _:
                raise ValueError(f"Unsupported gradient type: {bg_type}")
        
        # Convert numpy array to pyglet texture
        img = Image.fromarray(img_array, 'RGB')
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        self._texture = pyglet.image.ImageData(
            width, height, 'RGB', img.tobytes())
    
    def _create_solid_gradient(self, color: Tuple[int, int, int], 
                              height: int, width: int) -> np.ndarray:
        """
        Create a solid color gradient.
        
        Args:
            color: RGB color tuple.
            height: Image height.
            width: Image width.
            
        Returns:
            numpy array with the gradient.
        """
        return np.full((height, width, 3), color, dtype=np.uint8)
    
    def _create_linear_gradient(self, x: np.ndarray, y: np.ndarray,
                              center_x: int, center_y: int,
                              width: int, height: int,
                              start_color: Tuple[int, int, int],
                              end_color: Tuple[int, int, int],
                              angle: float) -> np.ndarray:
        """
        Create a linear gradient.
        
        Args:
            x, y: Meshgrid coordinates.
            center_x, center_y: Center coordinates.
            width, height: Image dimensions.
            start_color, end_color: Gradient colors.
            angle: Gradient angle in degrees.
            
        Returns:
            numpy array with the gradient.
        """
        theta = np.radians(angle)
        
        x_norm = (x - center_x) / (width / 2)
        y_norm = (y - center_y) / (height / 2)
        proj = x_norm * np.cos(theta) + y_norm * np.sin(theta)
        dist = (proj + 1) / 2
        
        noise = np.random.uniform(-0.02, 0.02, dist.shape)
        dist = np.clip(dist + noise, 0, 1)
        
        return self._interpolate_colors(start_color, end_color, dist)
    
    def _create_radial_gradient(self, x: np.ndarray, y: np.ndarray,
                              center_x: int, center_y: int,
                              width: int, height: int,
                              center_color: Tuple[int, int, int],
                              outer_color: Tuple[int, int, int]) -> np.ndarray:
        """
        Create a radial gradient.
        
        Args:
            x, y: Meshgrid coordinates.
            center_x, center_y: Center coordinates.
            width, height: Image dimensions.
            center_color, outer_color: Gradient colors.
            
        Returns:
            numpy array with the gradient.
        """
        stretch = width / height
        
        dx = (x - center_x)
        dy = (y - center_y) * stretch
        max_radius = np.sqrt(center_x**2 + (center_y * stretch)**2)
        
        dist = np.sqrt(dx**2 + dy**2) / max_radius
        dist = np.clip(dist, 0, 1)
        
        noise = np.random.uniform(-0.02, 0.02, dist.shape)
        dist = np.clip(dist + noise, 0, 1)
        
        return self._interpolate_colors(center_color, outer_color, dist)
    
    def _create_reflected_gradient(self, x: np.ndarray, y: np.ndarray,
                                 center_x: int, center_y: int,
                                 width: int, height: int,
                                 start_color: Tuple[int, int, int],
                                 end_color: Tuple[int, int, int],
                                 angle: float) -> np.ndarray:
        """
        Create a reflected gradient.
        
        Args:
            x, y: Meshgrid coordinates.
            center_x, center_y: Center coordinates.
            width, height: Image dimensions.
            start_color, end_color: Gradient colors.
            angle: Gradient angle in degrees.
            
        Returns:
            numpy array with the gradient.
        """
        theta = np.radians(angle)
        
        x_norm = (x - center_x) / (width / 2)
        y_norm = (y - center_y) / (height / 2)
        proj = x_norm * np.cos(theta) + y_norm * np.sin(theta)
        dist = np.abs(proj)
        
        noise = np.random.uniform(-0.02, 0.02, dist.shape)
        dist = np.clip(dist + noise, 0, 1)
        
        return self._interpolate_colors(start_color, end_color, dist)
    
    def _interpolate_colors(self, color1: Tuple[int, int, int],
                           color2: Tuple[int, int, int],
                           dist: np.ndarray) -> np.ndarray:
        """
        Interpolate between two colors based on distance values.
        
        Args:
            color1: Starting color.
            color2: Ending color.
            dist: Normalized distance array (0-1).
            
        Returns:
            numpy array with interpolated colors.
        """
        r = (color1[0] + (color2[0] - color1[0]) * dist).astype(np.uint8)
        g = (color1[1] + (color2[1] - color1[1]) * dist).astype(np.uint8)
        b = (color1[2] + (color2[2] - color1[2]) * dist).astype(np.uint8)
        return np.dstack((r, g, b))
        
    def _make_sprite(self) -> None:
        """Create a sprite from the current texture."""
        self._sprite = pyglet.sprite.Sprite(self._texture, x=0, y=0)
        
    def get_texture(self) -> pyglet.image.ImageData:
        """
        Get the current texture.
        
        Returns:
            The pyglet texture object.
        """
        return self._texture
    
    def draw(self) -> None:
        """Draw the background sprite."""
        self._sprite.draw()