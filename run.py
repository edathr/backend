import os

from app import create_app

config_name = os.getenv('FLASK_CONFIG')

if not config_name:
    config_name = "development"

app = create_app(config_name)


if __name__ == '__main__':
    print("Config Name from run.py", config_name)
    app.run('0.0.0.0')