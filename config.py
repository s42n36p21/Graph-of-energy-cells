import json


with open("cfg.json", 'r', encoding="utf-8") as file:
    data = json.load(file)
    
background =  data["default_settings"]["graphics"]["background"]
debug = data["debug"]