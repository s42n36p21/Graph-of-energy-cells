import re
from collections import defaultdict

class CSSRule:
    def __init__(self, selector, properties):
        self.selector = selector
        self.properties = properties
        self.specificity = self._calculate_specificity(selector)
    
    def _calculate_specificity(self, selector):

        specificity = [0, 0, 0, 0]
        
        selector = re.sub(r':[a-zA-Z-]+', '', selector)
        
        ids = re.findall(r'#([a-zA-Z_-][a-zA-Z0-9_-]*)', selector)
        specificity[1] = len(ids)
        
        classes = re.findall(r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)', selector)
        attributes = re.findall(r'\[[^\]]+\]', selector)
        specificity[2] = len(classes) + len(attributes)
        
        elements = re.findall(r'(^|[ #.])([a-zA-Z_-][a-zA-Z0-9_-]*)', selector)
        elements = [e[1] for e in elements if e[1] not in ('', '*')]
        specificity[3] = len(elements)
        
        return tuple(specificity)
    
    def __repr__(self):
        return f"CSSRule(selector='{self.selector}', properties={self.properties}, specificity={self.specificity})"

class CSSStyleSheet:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, rule):
        self.rules.append(rule)
    
    def get_styles_for_element(self, elem):
        styles = {}
        matching_rules = []
        
        for rule in self.rules:
            if self._selector_matches_element(rule.selector, elem):
                matching_rules.append(rule)
        
        matching_rules.sort(key=lambda x: x.specificity, reverse=True)
        
        for rule in matching_rules:
            styles.update(rule.properties)
        
        return styles
    
    def _selector_matches_element(self, selector, elem):
        selectors = re.split(r'\s*,\s*', selector)
        for sel in selectors:
            if self._simple_selector_matches_element(sel, elem):
                return True
        return False
    
    def _simple_selector_matches_element(self, selector, elem):
        element_name_match = re.match(r'^([a-zA-Z_-][a-zA-Z0-9_-]*|\*)', selector)
        if element_name_match:
            element_name = element_name_match.group(1)
            if element_name != '*' and element_name != elem.tag:
                return False
            selector = selector[element_name_match.end():]
        
        id_match = re.search(r'#([a-zA-Z_-][a-zA-Z0-9_-]*)', selector)
        if id_match:
            elem_id = elem.attrib.get('id', '')
            if elem_id != id_match.group(1):
                return False
            selector = selector.replace(id_match.group(0), '')
        
        class_matches = re.findall(r'\.([a-zA-Z_-][a-zA-Z0-9_-]*)', selector)
        if class_matches:
            elem_classes = elem.attrib.get('class', '').split()
            for required_class in class_matches:
                if required_class not in elem_classes:
                    return False
            selector = re.sub(r'\.[a-zA-Z_-][a-zA-Z0-9_-]*', '', selector)
        
        attr_matches = re.findall(r'\[([a-zA-Z_-][a-zA-Z0-9_-]*)(?:=([^\]]+))?\]', selector)
        for attr_name, attr_value in attr_matches:
            if attr_name not in elem.attrib:
                return False
            if attr_value and elem.attrib[attr_name] != attr_value.strip('"\''):
                return False
        
        return True

class CSSParser:
    def __init__(self):
        self.stylesheet = CSSStyleSheet()
    
    def parse_file(self, file_path):
        """Парсит CSS из файла и добавляет к существующим правилам"""
        with open(file_path, 'r') as f:
            css_content = f.read()
        self.parse_string(css_content)
    
    def parse_string(self, css_string):
        """Парсит CSS из строки и добавляет к существующим правилам"""
        css_string = re.sub(r'/\*.*?\*/', '', css_string, flags=re.DOTALL)
        rules = re.findall(r'([^{]+)\{([^}]*)\}', css_string)
        
        for selector_block, properties_block in rules:
            selectors = re.split(r'\s*,\s*', selector_block.strip())
            properties = self._parse_properties(properties_block)
            
            for selector in selectors:
                if selector and properties:
                    self.stylesheet.add_rule(CSSRule(selector, properties))
    
    def _parse_properties(self, properties_block):
        """Вспомогательный метод для парсинга свойств"""
        properties = {}
        for prop in properties_block.split(';'):
            prop = prop.strip()
            if prop:
                parts = prop.split(':', 1)
                if len(parts) == 2:
                    name, value = parts
                    properties[name.strip()] = value.strip()
        return properties
    
    def get_stylesheet(self):
        """Возвращает объединённую таблицу стилей"""
        return self.stylesheet