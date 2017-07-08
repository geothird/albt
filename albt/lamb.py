from __future__ import absolute_import
from os.path import basename
from .printmsg import PrintMsg
from botocore.exceptions import ClientError
import concurrent.futures
import json
import zipfile
import base64
import boto3
import os


class Lambda(object):
    """
    Lambda Functions
    """
    zip_name = "deploy.zip"
    virtual_env = None
    config = None
    invoke_config = None
    function = None
    function_name = None
    qualifier = None
    libraries = None
    client = None
    path = None
    region = None
    debug = False
    dry = False
    runtime = None
    invoke_type = None
    payload = None

    def __init__(self, **kwargs):
        """
        Initialize lambda
        :param kwargs:
        :return:
        """
        if 'function' not in kwargs:
            raise KeyError('function is a Required Argument')
        else:
            self.function = kwargs['function']
        if 'function_name' not in kwargs:
            self.function_name = os.path.splitext(basename(self.function))[0]
        else:
            self.function_name = kwargs['function_name']
        if 'config' not in kwargs:
            raise KeyError('config is a Required Argument')
        else:
            self.config = kwargs['config']
        if 'path' not in kwargs:
            raise KeyError('path is a Required Argument')
        else:
            self.path = kwargs['path']
        if 'virtual_env' in kwargs and kwargs['virtual_env']:
            self.virtual_env = kwargs['virtual_env']
            if '~' in self.virtual_env:
                self.virtual_env = os.path.expanduser(self.virtual_env)
        if 'qualifier' in kwargs:
            self.qualifier = kwargs['qualifier']
        if 'invoke_type' in kwargs and kwargs['invoke_type']:
            self.invoke_type = kwargs['invoke_type']
        if 'payload' in kwargs and kwargs['payload']:
            self.payload = kwargs['payload']
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        if 'dry' in kwargs:
            self.dry = kwargs['dry']
        if 'invoke_config' in kwargs and kwargs['invoke_config']:
            self.invoke_config = kwargs['invoke_config']
        if not self.payload and 'Payload' in self.invoke_config:
            self.payload = self.invoke_config['Payload']
        PrintMsg.debug = self.debug
        self.libraries = []
        if 'libraries' in kwargs and kwargs['libraries']:
            if ',' in kwargs['libraries']:
                libs = kwargs['libraries'].split(',')
                for lib in libs:
                    if '~' in lib:
                        self.libraries.append(os.path.expanduser(lib))
                    else:
                        self.libraries.append(lib)
            else:
                lib = kwargs['libraries']
                if '~' in lib:
                    lib = os.path.expanduser(lib)
                self.libraries.append(lib)
        self.zip_name = 'deploy-{}.zip'.format(self.function)
        if 'FunctionName' in self.config and self.config['FunctionName']:
            self.function_name = self.config['FunctionName']
        if 'region' in kwargs and kwargs['region']:
            self.region = kwargs['region']
        elif 'region' in self.config and self.config['region']:
            self.region = self.config['region']
        if 'runtime' in kwargs:
            self.runtime = kwargs['runtime']
        elif 'Runtime' in self.config:
            self.runtime = self.config['Runtime']
        if self.qualifier:
            self.invoke_config['Qualifier'] = self.qualifier
        if self.payload:
            self.invoke_config['Payload'] = self.__read_payload__()
        if self.dry:
            self.invoke_config['InvocationType'] = 'DryRun'
        elif self.invoke_type:
            self.invoke_config['InvocationType'] = self.invoke_type
        if 'FunctionName' not in self.invoke_config:
            self.invoke_config['FunctionName'] = self.function_name
        if not self.invoke_config['FunctionName']:
            self.invoke_config['FunctionName'] = self.function_name
        if '.' not in self.config['Handler']:
            fn = self.function.split('.')[0]
            self.config['Handler'] = '{}.{}'.format(fn, self.config['Handler'])
        self.invoke_config = {k: v for k, v in self.invoke_config.items() if v}
        self.config = {k: v for k, v in self.config.items() if v}
        self.client = boto3.client('lambda',  region_name=self.region)

    def create(self):
        """
        Create a new lambda function or update
        an existing function.
        :return:
        """
        try:
            PrintMsg.out(self.get())
            PrintMsg.updating('{} in region {}'.format(
                self.function_name, self.region))
            self.__update__()
        except ClientError as e:
            PrintMsg.out(e)
            PrintMsg.creating(self.function_name)
            self.__create__()

    def update(self):
        """
        Update a lambda function
        :return:
        """
        self.create()

    def get(self):
        """
        Get lambda function
        :return:
        """
        if self.qualifier:
            response = self.client.get_function(
                FunctionName=self.function_name,
                Qualifier=self.qualifier
            )
        else:
            response = self.client.get_function(
                FunctionName=self.function_name
            )
        return response

    def invoke(self):
        """
        Invoke lambda function
        :return:
        """
        try:
            PrintMsg.out(self.get())
            PrintMsg.invoking('{} in region {}'.format(
                self.function_name, self.region))
            self.__invoke__()
        except ClientError as e:
            PrintMsg.out(e)
            PrintMsg.error('Unable to invoke a function that does not exist')

    def __details__(self):
        """
        Show details of lambda function
        :return:
        """
        PrintMsg.out('{')
        PrintMsg.attr('  path', self.path)
        PrintMsg.attr('  function_name', self.function_name)
        PrintMsg.attr('  function', self.function)
        PrintMsg.attr('  qualifier', self.qualifier)
        PrintMsg.attr('  virtual_env', self.virtual_env)
        PrintMsg.attr('  libraries', self.libraries)
        PrintMsg.attr('  region', self.region)
        PrintMsg.attr('  config', self.config)
        PrintMsg.attr('  invoke_type', self.invoke_type)
        PrintMsg.attr('  invoke_config', self.invoke_config)
        PrintMsg.out('}')

    def __invoke__(self):
        """
        Invoke by configuration
        :return:
        """
        self.__details__()
        if self.invoke_type:
            invoke_type = self.invoke_type
        else:
            invoke_type = self.invoke_config['InvocationType']
        response = None
        if invoke_type == "RequestResponse":
            with concurrent.futures.ThreadPoolExecutor(
                    max_workers=5) as executor:
                futures = {executor.submit(
                    self.client.invoke, **self.invoke_config)}
                for future in concurrent.futures.as_completed(futures):
                    try:
                        response = future.result()
                        PrintMsg.cmd('Result', 'PAYLOAD')
                        payload = response['Payload'].read()
                        parsed = json.loads(payload)
                        print(json.dumps(parsed, indent=4, sort_keys=True))
                    except Exception as exc:
                        PrintMsg.error(exc)
        else:
            response = self.client.invoke(**self.invoke_config)
        if response:
            if self.debug:
                PrintMsg.out(response)
            if 'StatusCode' in response:
                PrintMsg.cmd(response['StatusCode'], 'STATUS')
            if 'LogResult' in response:
                PrintMsg.cmd("", "LOG")
                print('')
                print(base64.b64decode(response['LogResult']))

    def __update__(self):
        """
        Update function code and properties
        :return:
        """
        self.__details__()
        self.__zip_function__()
        response = self.client.update_function_code(
            FunctionName=self.function_name,
            ZipFile=self.__read_zip__()
        )
        if self.debug:
            PrintMsg.out(response)
        PrintMsg.cmd('Sha256: {}'.format(
            response['CodeSha256']), 'UPDATED CODE')
        self.__delete_zip__()
        if not self.dry:
            response = self.client.update_function_configuration(
                **self.config)
            if self.debug:
                PrintMsg.out(response)
            PrintMsg.cmd('Sha256: {}'.format(
                response['CodeSha256']), 'UPDATED CONFIG')

    def __create__(self):
        """
        Create function code and properties
        :return:
        """
        self.__details__()
        self.__zip_function__()
        if not self.dry:
            self.config['Code'] = {"ZipFile": self.__read_zip__()}
            response = self.client.create_function(**self.config)
            if self.debug:
                PrintMsg.out(response)
            PrintMsg.cmd(response['CodeSha256'], 'CREATED')
            self.config.pop('Code', None)
        self.__delete_zip__()

    @staticmethod
    def zip_add_dir(path, zipf, keep_parent=False):
        """
        Add directory to zip file
        :param path:
        :param zipf:
        :param keep_parent:
        :return:
        """
        base = basename(os.path.dirname(path))
        if keep_parent:
            len_dir_path = len(path)-len(base)
        else:
            len_dir_path = len(path)
        for root, _, files in os.walk(path):
            for f in files:
                file_path = os.path.join(root, f)
                zipf.write(file_path, file_path[len_dir_path:])

    def __zip_function__(self):
        """
        Zip source code
        :return:
        """
        PrintMsg.cmd('{}'.format(
            os.path.join(self.path, self.zip_name)), 'ARCHIVING')
        zipf = zipfile.ZipFile(
            os.path.join(self.path, self.zip_name), 'w', zipfile.ZIP_DEFLATED)
        if self.virtual_env:
            env_path = self.virtual_env
            for root, dirs, files in os.walk(self.virtual_env):
                for d in dirs:
                    if d == 'site-packages':
                        env_path = os.path.join(root, d)
            Lambda.zip_add_dir(env_path, zipf)
        if len(self.libraries) > 0:
            for lib in self.libraries:
                Lambda.zip_add_dir(lib, zipf, True)
        zipf.write(os.path.join(self.path, self.function), self.function)
        zipf.close()

    def __read_zip__(self):
        """
        Read zip file returning bytes
        :return bytes:
        """
        return self.__read_file__(self.zip_name)

    def __read_payload__(self):
        """
        Read payload json file
        :return bytes:
        """
        return self.__read_file__(self.payload)

    def __read_file__(self, file_name):
        """
        Read a file and return bytes
        :param file_name:
        :return bts:
        """
        with open(os.path.join(self.path, file_name), 'rb') as zf:
            bts = zf.read()

        return bts

    def __delete_zip__(self):
        """
        Delete zip file of source
        :return:
        """
        if os.path.exists(os.path.join(self.path, self.zip_name)):
            PrintMsg.out('Deleting {}'.format(
                os.path.join(self.path, self.zip_name)))
            os.remove(os.path.join(self.path, self.zip_name))
