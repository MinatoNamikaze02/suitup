import toml

def load_config():
    try:
        with open("config.toml", 'r') as config_file:
            config = toml.load(config_file)
        return config
    except Exception as e:
        raise e
    