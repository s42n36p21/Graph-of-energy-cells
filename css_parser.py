import re
from collections import defaultdict

class CSSParser:
    """Упрощённый парсер CSS с поддержкой селекторов и медиа-запросов"""
    def __init__(self):
        self.rules = defaultdict(dict)
        self.media_rules = []

    def parse(self, css_text):
        # Удаление комментариев
        css_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
        
        # Обработка медиа-запросов
        media_blocks = re.findall(
            r'@media\s*(.*?)\s*{(.*?)}', 
            css_text, 
            flags=re.DOTALL
        )
        
        for media_query, content in media_blocks:
            self.media_rules.append({
                'query': media_query.strip(),
                'rules': self._parse_block(content)
            })
        
        # Обработка обычных правил
        css_text = re.sub(r'@media\s*.*?{.*?}', '', css_text, flags=re.DOTALL)
        self.rules.update(self._parse_block(css_text))
        
        return self.rules, self.media_rules

    def _parse_block(self, css_text):
        rules = defaultdict(dict)
        blocks = re.findall(r'(.*?){(.*?)}', css_text, flags=re.DOTALL)
        
        for selectors, properties in blocks:
            for selector in selectors.split(','):
                selector = selector.strip()
                if not selector: continue
                
                for prop in properties.split(';'):
                    prop = prop.strip()
                    if ':' not in prop: continue
                    
                    key, value = prop.split(':', 1)
                    rules[selector][key.strip()] = value.strip()
        
        return rules