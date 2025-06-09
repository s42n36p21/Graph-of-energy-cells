import re
import colorsys
import random
import math
import time
from collections import namedtuple

# Предопределенные цвета (упрощенный вариант)
NAMES_TO_HEX = {
    'red': '#ff0000',
    'green': '#00ff00',
    'blue': '#0000ff',
    'white': '#ffffff',
    'black': '#000000',
    'yellow': '#ffff00',
    'cyan': '#00ffff',
    'magenta': '#ff00ff'
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
            color_input = NAMES_TO_HEX.get(color_input.lower(), color_input)
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
        self._update_hex_from_rgb()

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
    
    @staticmethod
    def from_rgb(r, g, b):
        return Color(('rgb', (r, g, b)))
    
    @staticmethod
    def from_hsv(h, s, v):
        return Color(('hsv', (h, s, v)))

class DinamicColor:
    EFFECTS_REGISTRY = {}
    
    def __init__(self, color_input):
        self.static = False
        self.base_color = None
        self.effect = None
        self.nested_colors = []
        self.current_color = Color("#000000")
        self.last_update_time = time.monotonic()
        
        if isinstance(color_input, str):
            color_input = color_input.strip()
            if color_input.startswith("#") or color_input in NAMES_TO_HEX or color_input.startswith("rgb(") or color_input.startswith("hsv("):
                self.static = True
                self.base_color = Color(color_input)
                self.current_color = self.base_color
            else:
                self._parse_dynamic_string(color_input)
        else:
            try:
                self.static = True
                self.base_color = Color(color_input)
                self.current_color = self.base_color
            except Exception as e:
                raise ValueError(f"Invalid color input: {color_input}") from e
                
    def _parse_dynamic_string(self, s):
        # Разбираем строку на эффект и цвета
        pattern = r'^(\w+)(?:\(([^)]*)\))?(?::(.+))?$'
        match = re.match(pattern, s)
        if not match:
            # Если это не эффект, возможно это список цветов в квадратных скобках
            if s.startswith('[') and s.endswith(']'):
                colors_list = self._parse_colors(s)
                self.nested_colors = [DinamicColor(c) for c in colors_list]
                self.effect = StaticBlendEffect(self.nested_colors)
                self.update(0)
                return
            raise ValueError(f"Invalid dynamic color format: {s}")
        
        effect_name = match.group(1)
        args_str = match.group(2) or ""
        colors_str = match.group(3) or ""
        
        args, kwargs = self._parse_arguments(args_str)
        colors_list = self._parse_colors(colors_str)
        
        self.nested_colors = [DinamicColor(c) for c in colors_list]
        effect_cls = self.EFFECTS_REGISTRY.get(effect_name)
        if not effect_cls:
            raise ValueError(f"Unknown effect: {effect_name}")
        
        self.effect = effect_cls(self.nested_colors, *args, **kwargs)
        self.update(0)  # Initial update
        
    def _parse_arguments(self, args_str):
        args = []
        kwargs = {}
        if not args_str:
            return args, kwargs
        
        parts = [p.strip() for p in args_str.split(',') if p.strip()]
        for part in parts:
            if '=' in part:
                key, value = part.split('=', 1)
                key = key.strip()
                value = value.strip()
                if value.replace('.', '', 1).lstrip('-').isdigit():
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                kwargs[key] = value
            else:
                if part.replace('.', '', 1).lstrip('-').isdigit():
                    if '.' in part:
                        args.append(float(part))
                    else:
                        args.append(int(part))
                else:
                    args.append(part)
        return args, kwargs
    
    def _parse_colors(self, colors_str):
        if not colors_str:
            return []
        if colors_str.startswith('[') and colors_str.endswith(']'):
            inner = colors_str[1:-1].strip()
            if not inner:
                return []
            return [c.strip() for c in inner.split(',')]
        return [colors_str]
    
    def update(self, dt=None):
        if self.static:
            return
        
        current_time = time.monotonic()
        if dt is None:
            dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        for color in self.nested_colors:
            color.update(dt)
        
        self.effect.update(dt)
        self.current_color = self.effect.get_current_color()
    
    def get_current_color(self):
        if self.static:
            return self.base_color
        return self.current_color
    
    @property
    def hex(self):
        return self.get_current_color().hex
    
    @property
    def r(self):
        return self.get_current_color().r
    
    @property
    def g(self):
        return self.get_current_color().g
    
    @property
    def b(self):
        return self.get_current_color().b
    
    @property
    def h(self):
        return self.get_current_color().h
    
    @property
    def s(self):
        return self.get_current_color().s
    
    @property
    def v(self):
        return self.get_current_color().v
    
    @property
    def rgb_abs(self):
        return self.get_current_color().rgb_abs
    
    @property
    def hsv_abs(self):
        return self.get_current_color().hsv_abs
    
    @property
    def rgb(self):
        return self.get_current_color().rgb
    
    def __repr__(self):
        if self.static:
            return f"DinamicColor(static={self.base_color})"
        return f"DinamicColor(effect={self.effect.__class__.__name__}, current={self.current_color})"

# ===== Effect Implementations =====
class RainbowEffect:
    def __init__(self, nested_colors, speed=1.0, scale=1.0):
        self.nested_colors = nested_colors
        self.speed = speed
        self.scale = scale
        self.phase = 0.0
        self.current_color = Color("#ff0000")
    
    def update(self, dt):
        base_color = self.nested_colors[0].get_current_color() if self.nested_colors else Color("#ff0000")
        h0, s0, v0 = base_color.hsv_abs
        self.phase = (self.phase + dt * self.speed) % 1.0
        current_h = (h0 + 360 * self.phase * self.scale) % 360
        self.current_color = Color.from_hsv(current_h, s0, v0)
    
    def get_current_color(self):
        return self.current_color

class FireEffect:
    def __init__(self, nested_colors, speed=1.0, scale=1.0, h_shift=60, s_shift=-50, v_shift=42):
        self.nested_colors = nested_colors
        self.speed = speed
        self.scale = scale
        self.h_shift = h_shift
        self.s_shift = s_shift
        self.v_shift = v_shift
        self.start_t = random.random()
        self.target_t = random.random()
        self.elapsed = 0.0
        self.duration = scale / speed
        self.current_color = Color.from_hsv(0, 100, 33)
    
    def update(self, dt):
        base_color = self.nested_colors[0].get_current_color() if self.nested_colors else Color.from_hsv(0, 100, 33)
        h0, s0, v0 = base_color.hsv_abs
        h1 = (h0 + self.h_shift) % 360
        s1 = max(0, min(100, s0 + self.s_shift))
        v1 = max(0, min(100, v0 + self.v_shift))
        
        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.duration)
        
        if progress < 0.5:
            t_ease = 2 * progress * progress
        else:
            t_ease = -2 * progress**2 + 4 * progress - 1
        
        current_t = self.start_t + t_ease * (self.target_t - self.start_t)
        current_t = max(0, min(1, current_t))
        
        h = (h0 + current_t * (h1 - h0)) % 360
        s = s0 + current_t * (s1 - s0)
        v = v0 + current_t * (v1 - v0)
        self.current_color = Color.from_hsv(h, s, v)
        
        if progress >= 1.0:
            self.start_t = self.target_t
            self.target_t = random.random()
            self.elapsed = 0.0
    
    def get_current_color(self):
        return self.current_color

class FlashingEffect:
    def __init__(self, nested_colors, speed=1.0):
        self.nested_colors = nested_colors
        self.speed = speed
        self.phase = 0.0
        self.current_color = Color("#000000")
        if len(nested_colors) < 2:
            self.nested_colors = [DinamicColor("#000000"), DinamicColor("#ffffff")]
    
    def update(self, dt):
        color1 = self.nested_colors[0].get_current_color()
        color2 = self.nested_colors[1].get_current_color()
        self.phase = (self.phase + dt * self.speed) % 1.0
        t = 1 - 4 * (self.phase - 0.5)**2
        r = int(color1.r * (1 - t) + color2.r * t)
        g = int(color1.g * (1 - t) + color2.g * t)
        b = int(color1.b * (1 - t) + color2.b * t)
        self.current_color = Color.from_rgb(r, g, b)
    
    def get_current_color(self):
        return self.current_color

class FireworkEffect:
    Flash = namedtuple('Flash', ['color', 'life_time', 'progress'])
    
    def __init__(self, nested_colors, speed=1.0, scale=3):
        self.nested_colors = nested_colors
        self.speed = speed
        self.scale = scale
        self.flashes = []
        self.current_color = Color("#000000")
        self._init_flashes()
    
    def _init_flashes(self):
        bg_color = self.nested_colors[0] if self.nested_colors else DinamicColor("#000000")
        flash_colors = self.nested_colors[1:] if len(self.nested_colors) > 1 else [DinamicColor("#ffffff")]
        
        for _ in range(self.scale):
            color_idx = random.randint(0, len(flash_colors) - 1)
            life_time = random.uniform(0.5, 1.5) / self.speed
            progress = random.uniform(0.0, 1.0)
            self.flashes.append(self.Flash(
                color=flash_colors[color_idx],
                life_time=life_time,
                progress=progress
            ))
    
    def update(self, dt):
        bg_color = self.nested_colors[0].get_current_color() if self.nested_colors else Color("#000000")
        r, g, b = bg_color.rgb_abs
        total_weight = 1.0
        
        new_flashes = []
        for flash in self.flashes:
            progress = flash.progress + dt / flash.life_time
            intensity = 1 - progress**2
            
            if progress < 1.0:
                flash_color = flash.color.get_current_color()
                r += intensity * flash_color.r
                g += intensity * flash_color.g
                b += intensity * flash_color.b
                total_weight += intensity
                new_flashes.append(flash._replace(progress=progress))
            else:
                # Replace dead flash
                flash_colors = self.nested_colors[1:] if len(self.nested_colors) > 1 else [DinamicColor("#ffffff")]
                color_idx = random.randint(0, len(flash_colors) - 1)
                life_time = random.uniform(0.5, 1.5) / self.speed
                new_flashes.append(self.Flash(
                    color=flash_colors[color_idx],
                    life_time=life_time,
                    progress=0.0
                ))
        
        self.flashes = new_flashes
        r = int(r / total_weight)
        g = int(g / total_weight)
        b = int(b / total_weight)
        self.current_color = Color.from_rgb(r, g, b)
    
    def get_current_color(self):
        return self.current_color

class IridescentEffect:
    def __init__(self, nested_colors, speed=1.0, scale=1.0):
        self.nested_colors = nested_colors
        self.speed = speed
        self.scale = scale
        self.duration = scale / speed
        self.elapsed = 0.0
        self.current_weights = self._generate_weights()
        self.target_weights = self._generate_weights()
        self.current_color = Color("#000000")
    
    def _generate_weights(self):
        weights = [random.random() for _ in range(len(self.nested_colors))]
        total = sum(weights)
        return [w / total for w in weights]
    
    def update(self, dt):
        self.elapsed += dt
        progress = min(1.0, self.elapsed / self.duration)
        
        if progress < 0.5:
            t_ease = 2 * progress * progress
        else:
            t_ease = -2 * progress**2 + 4 * progress - 1
        
        weights = []
        for i in range(len(self.current_weights)):
            w = self.current_weights[i] + t_ease * (self.target_weights[i] - self.current_weights[i])
            weights.append(w)
        
        r, g, b = 0, 0, 0
        for i, weight in enumerate(weights):
            color = self.nested_colors[i].get_current_color()
            r += weight * color.r
            g += weight * color.g
            b += weight * color.b
        
        self.current_color = Color.from_rgb(int(r), int(g), int(b))
        
        if progress >= 1.0:
            self.current_weights = self.target_weights
            self.target_weights = self._generate_weights()
            self.elapsed = 0.0
    
    def get_current_color(self):
        return self.current_color

class PulseEffect:
    def __init__(self, nested_colors, speed=1.0, min_v=50, max_v=100):
        self.nested_colors = nested_colors
        self.speed = speed
        self.min_v = min_v
        self.max_v = max_v
        self.phase = 0.0
        self.current_color = Color("#000000")
    
    def update(self, dt):
        base_color = self.nested_colors[0].get_current_color() if self.nested_colors else Color("#ff0000")
        self.phase = (self.phase + dt * self.speed) % 1.0
        t = (math.sin(self.phase * 2 * math.pi) + 1) / 2  # 0..1
        v = self.min_v + t * (self.max_v - self.min_v)
        h, s, _ = base_color.hsv_abs
        self.current_color = Color.from_hsv(h, s, v)
    
    def get_current_color(self):
        return self.current_color

class CycleEffect:
    def __init__(self, nested_colors, speed=1.0):
        self.nested_colors = nested_colors
        self.speed = speed
        self.phase = 0.0
        self.current_color = Color("#000000")
        if not nested_colors:
            self.nested_colors = [DinamicColor("#ff0000"), DinamicColor("#00ff00"), DinamicColor("#0000ff")]
    
    def update(self, dt):
        self.phase = (self.phase + dt * self.speed) % len(self.nested_colors)
        idx1 = int(self.phase) % len(self.nested_colors)
        idx2 = (idx1 + 1) % len(self.nested_colors)
        t = self.phase - idx1
        
        color1 = self.nested_colors[idx1].get_current_color()
        color2 = self.nested_colors[idx2].get_current_color()
        
        r = int(color1.r * (1 - t) + color2.r * t)
        g = int(color1.g * (1 - t) + color2.g * t)
        b = int(color1.b * (1 - t) + color2.b * t)
        self.current_color = Color.from_rgb(r, g, b)
    
    def get_current_color(self):
        return self.current_color

class StaticBlendEffect:
    def __init__(self, nested_colors):
        self.nested_colors = nested_colors
        self.current_color = Color("#000000")
    
    def update(self, dt):
        if not self.nested_colors:
            return
        
        r, g, b = 0, 0, 0
        for color in self.nested_colors:
            color.update(dt)
            r += color.r
            g += color.g
            b += color.b
        
        r = int(r / len(self.nested_colors))
        g = int(g / len(self.nested_colors))
        b = int(b / len(self.nested_colors))
        self.current_color = Color.from_rgb(r, g, b)
    
    def get_current_color(self):
        return self.current_color

# Регистрация эффектов
DinamicColor.EFFECTS_REGISTRY = {
    'rainbow': RainbowEffect,
    'fire': FireEffect,
    'flashing': FlashingEffect,
    'firework': FireworkEffect,
    'iridescent': IridescentEffect,
    'pulse': PulseEffect,
    'cycle': CycleEffect
}


