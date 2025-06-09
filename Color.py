import re
from typing import Tuple, Dict, Any, Union
import pyglet
from pyglet.shapes import Circle
import colorsys

NAMES_TO_HEX = {
    "aliceblue": "#f0f8ff",
    "antiquewhite": "#faebd7",
    "aqua": "#00ffff",
    "aquamarine": "#7fffd4",
    "azure": "#f0ffff",
    "beige": "#f5f5dc",
    "bisque": "#ffe4c4",
    "black": "#000000",
    "blanchedalmond": "#ffebcd",
    "blue": "#0000ff",
    "blueviolet": "#8a2be2",
    "brown": "#a52a2a",
    "burlywood": "#deb887",
    "cadetblue": "#5f9ea0",
    "chartreuse": "#7fff00",
    "chocolate": "#d2691e",
    "coral": "#ff7f50",
    "cornflowerblue": "#6495ed",
    "cornsilk": "#fff8dc",
    "crimson": "#dc143c",
    "cyan": "#00ffff",
    "darkblue": "#00008b",
    "darkcyan": "#008b8b",
    "darkgoldenrod": "#b8860b",
    "darkgray": "#a9a9a9",
    "darkgrey": "#a9a9a9",
    "darkgreen": "#006400",
    "darkkhaki": "#bdb76b",
    "darkmagenta": "#8b008b",
    "darkolivegreen": "#556b2f",
    "darkorange": "#ff8c00",
    "darkorchid": "#9932cc",
    "darkred": "#8b0000",
    "darksalmon": "#e9967a",
    "darkseagreen": "#8fbc8f",
    "darkslateblue": "#483d8b",
    "darkslategray": "#2f4f4f",
    "darkslategrey": "#2f4f4f",
    "darkturquoise": "#00ced1",
    "darkviolet": "#9400d3",
    "deeppink": "#ff1493",
    "deepskyblue": "#00bfff",
    "dimgray": "#696969",
    "dimgrey": "#696969",
    "dodgerblue": "#1e90ff",
    "firebrick": "#b22222",
    "floralwhite": "#fffaf0",
    "forestgreen": "#228b22",
    "fuchsia": "#ff00ff",
    "gainsboro": "#dcdcdc",
    "ghostwhite": "#f8f8ff",
    "gold": "#ffd700",
    "goldenrod": "#daa520",
    "gray": "#808080",
    "grey": "#808080",
    "green": "#008000",
    "greenyellow": "#adff2f",
    "honeydew": "#f0fff0",
    "hotpink": "#ff69b4",
    "indianred": "#cd5c5c",
    "indigo": "#4b0082",
    "ivory": "#fffff0",
    "khaki": "#f0e68c",
    "lavender": "#e6e6fa",
    "lavenderblush": "#fff0f5",
    "lawngreen": "#7cfc00",
    "lemonchiffon": "#fffacd",
    "lightblue": "#add8e6",
    "lightcoral": "#f08080",
    "lightcyan": "#e0ffff",
    "lightgoldenrodyellow": "#fafad2",
    "lightgray": "#d3d3d3",
    "lightgrey": "#d3d3d3",
    "lightgreen": "#90ee90",
    "lightpink": "#ffb6c1",
    "lightsalmon": "#ffa07a",
    "lightseagreen": "#20b2aa",
    "lightskyblue": "#87cefa",
    "lightslategray": "#778899",
    "lightslategrey": "#778899",
    "lightsteelblue": "#b0c4de",
    "lightyellow": "#ffffe0",
    "lime": "#00ff00",
    "limegreen": "#32cd32",
    "linen": "#faf0e6",
    "magenta": "#ff00ff",
    "maroon": "#800000",
    "mediumaquamarine": "#66cdaa",
    "mediumblue": "#0000cd",
    "mediumorchid": "#ba55d3",
    "mediumpurple": "#9370db",
    "mediumseagreen": "#3cb371",
    "mediumslateblue": "#7b68ee",
    "mediumspringgreen": "#00fa9a",
    "mediumturquoise": "#48d1cc",
    "mediumvioletred": "#c71585",
    "midnightblue": "#191970",
    "mintcream": "#f5fffa",
    "mistyrose": "#ffe4e1",
    "moccasin": "#ffe4b5",
    "navajowhite": "#ffdead",
    "navy": "#000080",
    "oldlace": "#fdf5e6",
    "olive": "#808000",
    "olivedrab": "#6b8e23",
    "orange": "#ffa500",
    "orangered": "#ff4500",
    "orchid": "#da70d6",
    "palegoldenrod": "#eee8aa",
    "palegreen": "#98fb98",
    "paleturquoise": "#afeeee",
    "palevioletred": "#db7093",
    "papayawhip": "#ffefd5",
    "peachpuff": "#ffdab9",
    "peru": "#cd853f",
    "pink": "#ffc0cb",
    "plum": "#dda0dd",
    "powderblue": "#b0e0e6",
    "purple": "#800080",
    "red": "#ff0000",
    "rosybrown": "#bc8f8f",
    "royalblue": "#4169e1",
    "saddlebrown": "#8b4513",
    "salmon": "#fa8072",
    "sandybrown": "#f4a460",
    "seagreen": "#2e8b57",
    "seashell": "#fff5ee",
    "sienna": "#a0522d",
    "silver": "#c0c0c0",
    "skyblue": "#87ceeb",
    "slateblue": "#6a5acd",
    "slategray": "#708090",
    "slategrey": "#708090",
    "snow": "#fffafa",
    "springgreen": "#00ff7f",
    "steelblue": "#4682b4",
    "tan": "#d2b48c",
    "teal": "#008080",
    "thistle": "#d8bfd8",
    "tomato": "#ff6347",
    "turquoise": "#40e0d0",
    "violet": "#ee82ee",
    "wheat": "#f5deb3",
    "white": "#ffffff",
    "whitesmoke": "#f5f5f5",
    "yellow": "#ffff00",
    "yellowgreen": "#9acd32",
}

class Color:
    def __init__(self, color_input):
        self._r = 0
        self._g = 0
        self._b = 0
        self._h = 0
        self._s = 0
        self._v = 0
        self._hex = "#000000"

        if isinstance(color_input, str):
            color_input = NAMES_TO_HEX.get(color_input, color_input)
            if color_input.startswith("#"):
                self._parse_hex(color_input)
            elif color_input.startswith("rgb("):
                self._parse_rgb_str(color_input)
            elif color_input.startswith("hsv("):
                self._parse_hsv_str(color_input)
            else:
                raise ValueError(f"Unsupported color format: {color_input}")
        elif isinstance(color_input, (tuple, list)) and len(color_input) == 2:
            mode, values = color_input
            if mode == "rgb":
                self._set_rgb(*values)
            elif mode == "hsv":
                self._set_hsv(*values)
            else:
                raise ValueError(f"Unsupported color mode: {mode}")
        else:
            raise ValueError("Invalid color input. Expected HEX, 'rgb(r,g,b)', 'hsv(h,s,v)', or ('rgb'/'hsv', (values)).")

    def _parse_hex(self, hex_str):
        if not re.match(r'^#[0-9a-fA-F]{6}$', hex_str):
            raise ValueError("Invalid HEX format. Expected #RRGGBB.")
        self._hex = hex_str.lower()
        self._update_rgb_from_hex()

    def _parse_rgb_str(self, rgb_str):
        match = re.match(r'^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$', rgb_str)
        if not match:
            raise ValueError("Invalid RGB format. Expected 'rgb(r, g, b)' where r,g,b are 0-255.")
        r, g, b = map(int, match.groups())
        self._set_rgb(r, g, b)

    def _parse_hsv_str(self, hsv_str):
        match = re.match(r'^hsv\(\s*(\d+\.?\d*)\s*,\s*(\d+\.?\d*)\s*,\s*(\d+\.?\d*)\s*\)$', hsv_str)
        if not match:
            raise ValueError("Invalid HSV format. Expected 'hsv(h, s, v)' where h=0-360, s,v=0-100.")
        h, s, v = map(float, match.groups())
        self._set_hsv(h, s, v)

    def _set_rgb(self, r, g, b):
        self._r = self._clamp(r, 0, 255)
        self._g = self._clamp(g, 0, 255)
        self._b = self._clamp(b, 0, 255)
        self._update_hex_from_rgb()
        self._update_hsv_from_rgb()

    def _set_hsv(self, h, s, v):
        self._h = self._clamp(h, 0, 360)
        self._s = self._clamp(s, 0, 100)
        self._v = self._clamp(v, 0, 100)
        self._update_rgb_from_hsv()

    def _update_rgb_from_hex(self):
        hex_value = self._hex.lstrip('#')
        self._r = int(hex_value[0:2], 16)
        self._g = int(hex_value[2:4], 16)
        self._b = int(hex_value[4:6], 16)
        self._update_hsv_from_rgb()

    def _update_hex_from_rgb(self):
        self._hex = "#{:02x}{:02x}{:02x}".format(self._r, self._g, self._b)

    def _update_hsv_from_rgb(self):
        r, g, b = self._r / 255.0, self._g / 255.0, self._b / 255.0
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        self._h = h * 360
        self._s = s * 100
        self._v = v * 100

    def _update_rgb_from_hsv(self):
        h, s, v = self._h / 360.0, self._s / 100.0, self._v / 100.0
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        self._r = int(round(r * 255))
        self._g = int(round(g * 255))
        self._b = int(round(b * 255))
        self._update_hex_from_rgb()

    @staticmethod
    def _clamp(value, min_val, max_val):
        return max(min_val, min(max_val, value))

    class _ColorComponent:
        def __init__(self, parent, attr, min_val, max_val):
            self.parent = parent
            self.attr = attr
            self.min_val = min_val
            self.max_val = max_val
        
        def __get__(self, obj, owner):
            return getattr(obj, f"_{self.attr}")
        
        def __set__(self, obj, value):
            value = max(self.min_val, min(self.max_val, value))
            setattr(obj, f"_{self.attr}", value)
            if self.attr in ('r', 'g', 'b'):
                obj._update_hex_from_rgb()
                obj._update_hsv_from_rgb()
            else:
                obj._update_rgb_from_hsv()
        
        def __iadd__(self, other):
            new_val = getattr(self.parent, f"_{self.attr}") + other
            self.__set__(self.parent, new_val)
            return self.parent
        
        def __isub__(self, other):
            new_val = getattr(self.parent, f"_{self.attr}") - other
            self.__set__(self.parent, new_val)
            return self.parent
        
        def __imul__(self, other):
            new_val = getattr(self.parent, f"_{self.attr}") * other
            self.__set__(self.parent, new_val)
            return self.parent
    
    # Определяем свойства через дескрипторы
    r = _ColorComponent(None, 'r', 0, 255)
    g = _ColorComponent(None, 'g', 0, 255)
    b = _ColorComponent(None, 'b', 0, 255)
    h = _ColorComponent(None, 'h', 0, 360)
    s = _ColorComponent(None, 's', 0, 100)
    v = _ColorComponent(None, 'v', 0, 100)
    
    # Инициализация дескрипторов
    def __post_init__(self):
        self.r = self._ColorComponent(self, 'r', 0, 255)
        self.g = self._ColorComponent(self, 'g', 0, 255)
        self.b = self._ColorComponent(self, 'b', 0, 255)
        self.h = self._ColorComponent(self, 'h', 0, 360)
        self.s = self._ColorComponent(self, 's', 0, 100)
        self.v = self._ColorComponent(self, 'v', 0, 100)
    
    @property
    def hex(self):
        return self._hex
    
    @hex.setter
    def hex(self, value):
        if not re.match(r'^#[0-9a-fA-F]{6}$', value):
            raise ValueError("Invalid HEX color format. Expected #RRGGBB.")
        self._hex = value.lower()
        self._update_rgb_from_hex()
    
    @property
    def rgb_abs(self):
        return (self._r, self._g, self._b)
    
    @property
    def hsv_abs(self):
        return (self._h, self._s, self._v)
    
    @property
    def rgb(self):
        return (self._r / 255.0, self._g / 255.0, self._b / 255.0)
    
    @property
    def hsv(self):
        return (self._h / 360.0, self._s / 100.0, self._v / 100.0)
    
    def __repr__(self):
        return f"Color(hex='{self.hex}', rgb={self.rgb_abs}, hsv={self.hsv_abs})"
    
    def copy(self):
        return Color(self.hex)

