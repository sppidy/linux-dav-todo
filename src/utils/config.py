def load_config(file_path):
    import configparser

    config = configparser.ConfigParser()
    config.read(file_path)
    return config

def save_config(file_path, config):
    import configparser

    with open(file_path, 'w') as configfile:
        config.write(configfile)