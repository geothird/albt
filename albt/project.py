from __future__ import absolute_import
from .printmsg import PrintMsg
from .lamb import Lambda
from .config import Config
from os.path import basename
import os
import json
import yaml

"""
Default config yaml
"""
DEFAULT_CONFIG = {
    "Description": None,
    "FunctionName": None,
    "Handler": "lambda_handler",
    "MemorySize": 128,
    "Role": None,
    "Runtime": "python2.7",
    "Timeout": 15,
    "VpcConfig": None,
    "Environment": None,
    "KMSKeyArn": None,
    "TracingConfig": None,
    "DeadLetterConfig": None
}

"""
Default python source code
"""
DEFAULT_SOURCE = """from __future__ import print_function


# noinspection PyUnusedLocal
def lambda_handler(event, context):
    print(event)
"""

"""
Default Invoke config
"""
DEFAULT_INVOKE_CONFIG = {
    "FunctionName": None,
    "InvocationType": "Event",
    "LogType": "None",
    "ClientContext": None,
    "Payload": None,
    "Qualifier": None
}


class Project(object):
    """
    Project of lambda functions
    """
    path = None
    functions = []
    func = None
    libraries = None
    qualifier = None
    config_file = "config.yaml"
    i_config_file = "invoke.yaml"
    payload = None
    json_payload_file = None
    invoke_type = None
    virtual_env = None
    debug = False
    region = None
    dry = False
    config_postfix = '.yml'
    function_postfix = '.py'
    invoke_postfix = '-invoke.yml'

    def __init__(self, **kwargs):
        """
        Initialize project
        :param kwargs:
        :return:
        """
        if 'path' not in kwargs:
            raise KeyError('path is a Required Argument')
        else:
            self.path = kwargs['path']
        if 'qualifier' in kwargs:
            self.qualifier = kwargs['qualifier']
        if 'virtual_env' in kwargs:
            self.virtual_env = kwargs['virtual_env']
        if 'libraries' in kwargs:
            self.libraries = kwargs['libraries']
        if 'config_file' in kwargs:
            self.config_file = kwargs['config_file']
        if 'invoke_file' in kwargs:
            self.i_config_file = kwargs['invoke_file']
        if 'payload' in kwargs and kwargs['payload']:
            self.payload = self.load_json(kwargs['payload'])
        if 'invoke_type' in kwargs and kwargs['invoke_type']:
            self.invoke_type = kwargs['invoke_type']
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        if 'region' in kwargs:
            self.region = kwargs['region']
        if 'dry' in kwargs:
            self.dry = kwargs['dry']
        if 'func' in kwargs and kwargs['func']:
            self.func = kwargs['func']
        PrintMsg.debug = self.debug
        PrintMsg.cmd('Path {}'.format(self.path), 'INITIALIZING', 'yellow')
        if not self.func:
            self.initialize_functions()

    def initialize_functions(self):
        """
        Initialize list of functions
        """
        for root, dirs, files in os.walk(self.path):
            for f in files:
                if f.endswith(self.function_postfix):
                    file_name = os.path.splitext(basename(f))[0]
                    config = self.get_config(
                        root,
                        self.config_file,
                        file_name,
                        DEFAULT_CONFIG
                    )
                    icf = self.get_config(
                        root,
                        self.i_config_file,
                        file_name,
                        DEFAULT_INVOKE_CONFIG,
                        self.invoke_postfix
                    )
                    self.functions.append(
                        Lambda(
                            function=f,
                            function_name=file_name,
                            path=os.path.join(root),
                            virtual_env=self.virtual_env,
                            config=config,
                            qualifier=self.qualifier,
                            libraries=self.libraries,
                            region=self.region,
                            debug=self.debug,
                            dry=self.dry,
                            invoke_config=icf,
                            payload=self.json_payload_file,
                            invoke_type=self.invoke_type
                        )
                    )

    def get_config(self, path, config_file, name=None,
                   default=None, postfix='.yml'):
        """
        Load config yaml
        :param name:
        :param postfix:
        :param default:
        :param path:
        :param config_file:
        :return:
        """
        if os.path.exists(os.path.join(path, config_file)):
            cf = Config(os.path.join(path, config_file))
            data = cf.yaml_data
            if default:
                data = self.merge_config(data, default)
            return data
        elif name and os.path.exists(os.path.join(path, name) + postfix):
            cf = Config(os.path.join(path, name) + postfix)
            data = cf.yaml_data
            if default:
                data = self.merge_config(data, default)
            return data
        else:
            return default

    @staticmethod
    def merge_config(data, default):
        """
        Merge config data with default
        :param data:
        :param default:
        :return data:
        """
        for k, v in default.items():
            if k not in data:
                data[k] = v
        return data

    def load_json(self, payload):
        """
        Load json from payload file
        :param payload:
        :return rj:
        """
        rj = None
        if os.path.exists(os.path.join(self.path, payload)):
            self.json_payload_file = os.path.join(self.path, payload)
            with open(os.path.join(self.path, payload), 'r') as j:
                try:
                    rj = json.load(j)
                except TypeError:
                    PrintMsg.error('Invalid json payload')
        elif os.path.exists(payload):
            self.json_payload_file = payload
            with open(payload, 'r') as j:
                try:
                    rj = json.load(j)
                except TypeError:
                    PrintMsg.error('Invalid json payload')
        if self.debug:
            PrintMsg.out(rj)
        return rj

    def invoke(self, func):
        """
        Invoke a lambda function
        :param func:
        :return:
        """
        file_name = os.path.join(self.path, func)
        config = self.get_config(
            self.path,
            self.config_file,
            file_name,
            DEFAULT_CONFIG
        )
        icf = self.get_config(
            self.path,
            self.i_config_file,
            file_name,
            DEFAULT_INVOKE_CONFIG,
            self.invoke_postfix
        )
        Lambda(
            function=file_name,
            path=self.path,
            funcion_name=func,
            virtual_env=self.virtual_env,
            config=config,
            qualifier=self.qualifier,
            libraries=self.libraries,
            region=self.region,
            debug=self.debug,
            dry=self.dry,
            invoke_config=icf,
            payload=self.json_payload_file,
            invoke_type=self.invoke_type
        ).invoke()

    def invoke_all(self):
        """
        Invoke all functions in path
        :return:
        """
        for f in self.functions:
            f.invoke()
        PrintMsg.done('Invoking all')

    def deploy(self, func):
        """
        Deploy function
        :param func:
        :return:
        """
        file_name = os.path.join(self.path, func)
        config = self.get_config(
            self.path,
            self.config_file,
            file_name,
            DEFAULT_CONFIG
        )
        icf = self.get_config(
            self.path,
            self.i_config_file,
            file_name,
            DEFAULT_INVOKE_CONFIG,
            self.invoke_postfix
        )
        f = func + self.function_postfix
        Lambda(
            function=f,
            function_name=func,
            path=self.path,
            virtual_env=self.virtual_env,
            config=config,
            qualifier=self.qualifier,
            libraries=self.libraries,
            region=self.region,
            debug=self.debug,
            dry=self.dry,
            invoke_config=icf,
            payload=self.json_payload_file,
            invoke_type=self.invoke_type
        ).create()
        PrintMsg.done('Deploying')

    def deploy_all(self):
        """
        Deploy all functions in path
        :return:
        """
        for f in self.functions:
            f.create()
        PrintMsg.done('Deploying all')

    @staticmethod
    def new(**kwargs):
        """
        New function
        :param kwargs:
        :return:
        """
        if 'Path' not in kwargs or not kwargs['Path']:
            raise KeyError('path is a Required Argument')
        if 'Function' not in kwargs or not kwargs['Function']:
            raise KeyError('function is a Required Argument')
        PrintMsg.cmd('New lambda function {}.'.format(
            kwargs['Function']), 'INITIALIZING', 'yellow')
        path = kwargs['Path']
        func = kwargs['Function']
        kwargs.pop('Path', None)
        kwargs.pop('Function', None)
        cf = {k: v for k, v in kwargs.items() if v}
        cf = Project.merge_config(cf, DEFAULT_CONFIG)
        cf = {k: v for k, v in cf.items() if v}
        cf_name = os.path.join(path, func) + Project.config_postfix
        f_name = os.path.join(path, func) + Project.function_postfix
        PrintMsg.creating('Config file {}.'.format(cf_name))
        if not os.path.exists(cf_name):
            with open(cf_name, 'w') as j:
                yaml.safe_dump(cf, j, default_flow_style=False)
            PrintMsg.done('Creating config file {}.'.format(cf_name))
        else:
            PrintMsg.error('Config file already exists.')
        PrintMsg.creating('Source file {}'.format(f_name))
        if not os.path.exists(f_name):
            f = open(f_name, 'w')
            f.write(DEFAULT_SOURCE)
            f.close()
            PrintMsg.done('Creating source file {}.'.format(f_name))
        else:
            PrintMsg.error('File already exists.')
        PrintMsg.done('Creating lambda function {}.'.format(func))
