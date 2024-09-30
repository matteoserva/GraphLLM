import yaml

def get_client_config(config_file="client_config.yml", client_name="default_client"):
    with open(config_file,"r") as f:
        v = yaml.safe_load(f)
    return v[client_name]
