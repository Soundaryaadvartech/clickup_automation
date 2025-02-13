import json
import os

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as file:
        return json.load(file)

config = load_config()

personal_token = config['personal_token']
headers = config['headers']
team_id = config['team_id']
team_name = config['team_name']
spaces = config['spaces']