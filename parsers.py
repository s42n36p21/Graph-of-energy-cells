import re

def get_param(property, element, propertys, default=None):
    return element.get(property, propertys.get(property, default))

def parse_color(color_hex: str):
    """Преобразует hex-цвет в tuple (R, G, B, A)"""
    color_hex = color_hex.lstrip('#')
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)
    return (r, g, b, 255)

import re

def parse_expression(expression: str, propertys):
    if not isinstance(expression, str):
        return expression
    if expression in {
        'top': 1,
        'right': 1,
        'left': 0,
        'bottom': 0,
        'center': 0.5
    }:
        return expression

    def replace_units(match):
        value = match.group(1) or '1'
        unit = match.group(2)

        if unit == 'px':
            return value
        elif unit in ['vh', 'vw', 'em', 'rem', '%']:
            return f'({value})*({propertys.get(unit, 0)})'
        else:
            return match.group(0)

    def replace_calc(match):
        inner_expr = match.group(1)
        # Рекурсивно парсим выражение внутри calc
        return str(parse_expression(inner_expr, propertys))

    allowed_names = {
        'min': min,
        'max': max,
        'abs': abs,
        'round': round,
        'calc': lambda x: x,  # Заглушка, фактически не используется
    }

    # Сначала обрабатываем calc()
    calc_pattern = r'calc\(([^)]+)\)'
    processed_expr = re.sub(calc_pattern, replace_calc, expression)
    
    # Затем обрабатываем единицы измерения
    units_pattern = r'([-+]?[\d.]+)(px|vw|vh|em|rem|%)'
    processed_expr = re.sub(units_pattern, replace_units, processed_expr)
    
    try:
        return eval(processed_expr, {'__builtins__': None}, allowed_names)
    except:
        return 0

def parse_gap(element, propertys, gap_name):
    """
    Парсит значения padding или margin из элемента и свойств.
    Возвращает массив из 4 значений [top, right, bottom, left]
    
    Поддерживает:
    - Сокращенную запись (1-4 значения)
    - Проверку на наличие отдельных свойств (padding-top и т.д.)
    - Обработку выражений через calc()
    """
    prop_name = gap_name
    # Получаем основное значение (например, padding: 10px 20px)
    main_value = get_param(prop_name, element, propertys)
    
    # Получаем индивидуальные направления (например, padding-top: 5px)
    top = get_param(f'{prop_name}-top', element, propertys)
    right = get_param(f'{prop_name}-right', element, propertys)
    bottom = get_param(f'{prop_name}-bottom', element, propertys)
    left = get_param(f'{prop_name}-left', element, propertys)
    
    # Инициализируем результат
    result_gaps = [0, 0, 0, 0]  # top, right, bottom, left
    
    input_str = get_param(prop_name, element, propertys)
    if input_str:
                
        pattern = re.compile(r'(\d+\.?\d*|calc\(([^)]+)\))')
        matches = pattern.finditer(input_str)

        result = []
        for match in matches:
            item = match.group(0)
            # Если это calc(exep), обрабатываем специальной функцией
            if item.startswith("calc("):
                exep = match.group(2)  # Группа 2 содержит exep
                processed = parse_expression(exep, propertys)
                result.append(processed)
            else:
                result.append(item)

        parsed_parts = result
        if len(parsed_parts) == 1:
            result = [parsed_parts[0]] * 4
        elif len(parsed_parts) == 2:
            result = [parsed_parts[0], parsed_parts[1], parsed_parts[0], parsed_parts[1]]
        elif len(parsed_parts) == 3:
            result = [parsed_parts[0], parsed_parts[1], parsed_parts[2], parsed_parts[1]]
        elif len(parsed_parts) == 4:
            result = parsed_parts[:4]
    
    
    # Перезаписываем значения индивидуальными направлениями, если они есть
    if top is not None:
        result[0] = parse_expression(top, propertys) if isinstance(top, str) else top
    if right is not None:
        result[1] = parse_expression(right, propertys) if isinstance(right, str) else right
    if bottom is not None:
        result[2] = parse_expression(bottom, propertys) if isinstance(bottom, str) else bottom
    if left is not None:
        result[3] = parse_expression(left, propertys) if isinstance(left, str) else left
    
    return [float(p) for p in result]