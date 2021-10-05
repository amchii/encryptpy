import os.path

import click
from click import Context

from .compiler import Compiler
from .config import BaseConfig, Config, DictConfig

try:
    default_config = Config()
except FileNotFoundError:
    default_config = BaseConfig()


@click.group()
@click.option(
    "--config",
    default=".encryptpy.cfg",
    show_default=True,
    help="The config file, ignore if given is invalid",
)
@click.pass_context
def encryptpy(ctx: Context, config):
    """Encrypt your Python code"""
    ctx.ensure_object(dict)
    ctx.obj["config_file"] = config


@encryptpy.command()
@click.option(
    "-b",
    "--build-dir",
    default=default_config.build_dir,
    show_default=True,
    help="The build directory.",
)
@click.option(
    "-i",
    "--ignore",
    "ignores",
    default=default_config.ignores,
    show_default=True,
    multiple=True,
    help="Regex pattern, files matched will not be compiled. Can be used multiple times.",
)
@click.option(
    "--clean-py",
    is_flag=True,
    default=default_config.clean_py,
    show_default=True,
    help="Clean the source .py.",
)
@click.argument(
    "paths",
    nargs=-1,
)
@click.pass_context
def run(ctx, paths, build_dir, ignores, clean_py):
    """Compile given Python code files\n
    If PATHS not provided, try to read them from config file, otherwise back to the current work directory
    """
    config_file = ctx.obj["config_file"]
    if os.path.isfile(config_file):
        config = DictConfig(**Config(config_file).to_dict())
    else:
        config = DictConfig()

    if not paths:
        paths = config.paths or ["."]
    specified = DictConfig(
        paths=paths, build_dir=build_dir, ignores=ignores, clean_py=clean_py
    )
    config.update_from_other(specified)
    compiler = Compiler(config)
    compiler.run()


@encryptpy.command()
@click.option(
    "-b",
    "--build-dir",
    default=default_config.build_dir,
    show_default=True,
    help="The build directory.",
)
@click.option(
    "-i",
    "--ignore",
    "ignores",
    default=default_config.ignores,
    show_default=True,
    multiple=True,
    help="Regex pattern, files matched will not be compiled. Can be used multiple times.",
)
@click.option(
    "-I",
    "--copy-ignore",
    "copy_ignores",
    default=default_config.copy_ignores,
    show_default=True,
    multiple=True,
    help="Glob-style patterns, files matched will not be copied when init-run. Can be used multiple times.",
)
@click.argument("src_dir", type=click.Path(exists=True))
@click.pass_context
def init_run(ctx, src_dir, build_dir, ignores, copy_ignores):
    """Copy src to build-dir and do compile, usually used for the first time.\n
    The files to be compiled will be read from config file.
    """
    config_file = ctx.obj["config_file"]
    if os.path.isfile(config_file):
        config = DictConfig(**Config(config_file).to_dict())
    else:
        config = DictConfig()
    specified = DictConfig(
        build_dir=build_dir, ignores=ignores, copy_ignores=copy_ignores
    )
    config.update_from_other(specified)
    compiler = Compiler(config)
    compiler.init_run(src=src_dir)


if __name__ == "__main__":
    encryptpy()
