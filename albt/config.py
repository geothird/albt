import yaml


class Config(object):
    """
    Load Config yaml file
    """
    def __init__(self, yaml_file):
        """
        Initialize config yaml
        :param yaml_file:
        :return:
        """
        with open(yaml_file, 'r') as stream:
            try:
                self.yaml_data = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)
