from __future__ import absolute_import
from .project import Project

import click
import os


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """
    AWS Lambda Build Tool

    Build and deploy projects that use AWS Lambda.
    """
    if ctx.invoked_subcommand is None:
        print(ctx.get_help())


@cli.command()
def version():
    """
    Display albt version
    """
    with open(os.path.abspath(os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'VERSION'))) as version_file:
        v = version_file.read().strip()
    click.echo(click.style('albt: ', fg='white') + click.style(v, fg='green'))


@cli.command()
@click.argument('path', nargs=1)
@click.argument('func', nargs=-1)
@click.option('--qualifier', default=None,
              help='Qualifier example: dev|prod|latest')
@click.option('--region', default=None, help='AWS Region override')
@click.option('--venv', default=None, help='Included Virtual environment')
@click.option('--libs', default=None, help='Include library folders')
@click.option('--debug/--no-debug', default=False,
              help='Show Debugging information')
@click.option('--dry/--no-dry', default=False, help='Dry Run')
def deploy(path, func, qualifier, region, venv, libs, debug, dry):
    """
    Deploy lambda functions
    """
    p = Project(
        path=path,
        func=func,
        qualifier=qualifier,
        virtual_env=venv,
        libraries=libs,
        debug=debug,
        region=region,
        dry=dry
    )

    if func:
        p.deploy(''.join(func))
    else:
        p.deploy_all()


@cli.command()
@click.argument('path', nargs=1)
@click.argument('func', nargs=-1)
@click.option('--payload', default=None, help='Invoke payload')
@click.option('--invocation', default=None, help='Invocation type')
@click.option('--qualifier', default=None,
              help='Qualifier example: dev|prod|latest')
@click.option('--region', default=None, help='AWS Region override')
@click.option('--venv', default=None, help='Included Virtual environment')
@click.option('--libs', default=None, help='Include library folders')
@click.option('--debug/--no-debug', default=False,
              help='Show Debugging information')
@click.option('--dry/--no-dry', default=False, help='Dry run')
@click.option('--d/--no-d', default=False, help='Also deploy')
def invoke(path, func, payload, invocation, qualifier,
           region, venv, libs, debug, dry, d):
    """
    Invoke lambda functions
    """
    p = Project(
        path=path,
        func=func,
        virtual_env=venv,
        libraries=libs,
        qualifier=qualifier,
        debug=debug,
        region=region,
        dry=dry,
        payload=payload,
        invoke_type=invocation
    )

    if func:
        if d:
            p.deploy(''.join(func))
        p.invoke(''.join(func))
    else:
        if d:
            p.deploy_all()
        p.invoke_all()


@cli.command()
@click.argument('path', nargs=1)
@click.argument('func', nargs=1)
@click.option('--handler', default=None, help='Function handler name')
@click.option('--role', default=None, help='AWS Role')
@click.option('--memory', default=None, help='Memory Size')
@click.option('--timeout', default=None, help='Timeout')
@click.option('--description', default=None, help='Description')
@click.option('--runtime', default=None, help='Runtime')
@click.option('--name', default=None, help='Override function name')
@click.option('--region', default=None, help='AWS Region override')
@click.option('--venv', default=None, help='Included Virtual environment')
@click.option('--libs', default=None, help='Include library folders')
@click.option('--qualifier', default=None,
              help='Qualifier example: dev|prod|latest')
@click.option('--debug/--no-debug', default=False,
              help='Show Debugging information')
@click.option('--dry/--no-dry', default=False, help='Dry run')
@click.option('--d/--no-d', default=False, help='Also deploy')
def new(path, func, handler, role, memory, timeout,
        description, runtime, name, region, venv, libs,
        qualifier, debug, dry, d):
    """
    Create new lambda function
    """
    Project.new(
        Path=path,
        Function=func,
        FunctionName=name,
        Handler=handler,
        Role=role,
        MemorySize=memory,
        Timeout=timeout,
        Description=description,
        Tuntime=runtime,
        Region=region
    )

    if d:
        Project(
            path=path,
            qualifier=qualifier,
            virtual_env=venv,
            libraries=libs,
            debug=debug,
            region=region,
            dry=dry
        ).deploy(func)
