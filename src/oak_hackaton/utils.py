import json

def load_json(path: str) -> dict:
    with open(path, "r") as file:
        return json.load(file)
