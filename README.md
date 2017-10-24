# Aws Lambda Build Tool

[![Build Status](https://travis-ci.org/geothird/albt.svg?branch=master)](https://travis-ci.org/geothird/albt)

> Build and deploy projects that use AWS Lambda.

```bash
$ albt --help
Usage: albt [OPTIONS] COMMAND [ARGS]...

  AWS Lambda Build Tool

  Build and deploy projects that use AWS Lambda.

Options:
  --help  Show this message and exit.

Commands:
  deploy   Deploy lambda functions
  invoke   Invoke lambda functions
  new      Create new lambda function
  version  Display albt version
```

## Goals

- Simplify deploying and invoking lambda functions with less flags.
- Configure projects with yaml files instead of using multi line command line attributes. 
- Automate zip file creation of lambda functions that use external packages or custom libraries.
- Integrate with services that use Lambda functions such as API Gateway.

# Installing

## Requirements

[Aws cli](http://aws.amazon.com/cli/) is a required pre-installation step, or at minimum creating a credentials file.

```bashg
$ aws configure
```
This will prompt for credentials and set up the `~/.aws/credentials` file.

## Install from pip

```bash
$ pip install albt
```

# Usage

## Creating

### Create a new function in current directory

```bash
$ albt new . my_function
```

### Create a new function with specific role and handler

```bash
$ albt new . my_function --role=arn:aws:iam:::role/my_role --handler=my_handler
```


## Deploying

### Deploy an entire directory of functions

```bash
$ albt deploy .
```

### Deploy a single function

```bash
$ albt deploy . lambda_function
```

### Deploy to a specific region

```bash
$ albt deploy . lambda_function --region=us-west-2
```

## Invoking

### Invoke a function

```bash
$ albt invoke . my_function
```

### Invoke a function with a json payload

```bash
$ albt invoke . my_function --payload=payloads/new.json --invoketype="RequestResponse"
```

## Environment

### Add an environment variable

Edit the function config yaml file.

```bash
vi my_function.yml
```
```yaml
FunctionName: my-function-name
MemorySize: 128
Timeout: 15
Environment:
  Variables:
      Debug: 'True'
```

Add code to lambda function to retrieve environment variable
```python
import os
DEBUG = os.environ['Debug'] == 'True'
```

## Building

### Local development installation

```bash
$ virtualenv venv
$ . venv/bin/activate
$ pip install --editable .
```

### Create source distributuion

```bash
python setup.py sdist
```

Install wheel

```bash
pip install wheel
```

Install universal

```bash
python setup.py bdist_wheel --universal
```

### Uploading to PyPi

```bash
twine upload dist/*
```

## Signing and uploading to PyPi

```bash
gpg --detach-sign -a dist/albt-<VERSION>.tar.gz
twine upload dist/albt-<VERSION>.tar.gz dist/albt-<VERSION>.tar.gz.asc
```

## TODO

- Add swagger file generation and import for api gateway lambda project
- Add cloud formation for project roles policies and resources

## License

MIT