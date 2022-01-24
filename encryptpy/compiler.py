import os
import shutil
import sys
import tempfile
import typing

from setuptools import setup
from setuptools.command.build_ext import build_ext
from setuptools.command.build_py import build_py

from .config import BaseConfig
from .utils import walk_dir

from Cython.Build import cythonize  # isort:skip


build_ext.run = lambda self: super(
    build_ext, self
).run()  # Do not build extensions in build directory if --inplace
build_py.get_package_dir = lambda *args: ""


class CompileError(Exception):
    pass


def compile_one(file_path, clean_py=True) -> str:
    file_path = os.path.abspath(file_path)
    origin_work_dir = os.getcwd()
    dirname = os.path.dirname(file_path)
    os.chdir(dirname)
    try:
        with tempfile.TemporaryDirectory() as td:
            dist = setup(
                ext_modules=cythonize([file_path], quiet=True, language_level=3),
                script_args=["build_ext", "-t", td, "--inplace"],
            )
            extension = dist.ext_modules[0]
            build_ext = dist.command_obj["build_ext"]
            so_file = build_ext.get_ext_fullpath(extension.name)

        c_file = file_path.replace(".py", ".c")
        if os.path.exists(c_file):
            os.remove(c_file)
        if clean_py:
            if os.path.exists(file_path):
                os.remove(file_path)
        return so_file
    except Exception as e:
        raise CompileError(e)

    finally:
        os.chdir(origin_work_dir)


def _do_compile(
    paths, clean_py=True, ignores=None
) -> typing.Tuple[
    typing.List[str], typing.Tuple[typing.List[str], typing.List[str], typing.List[str]]
]:
    """
    :param paths: file or directory
    :param clean_py: delete origin .py file
    :return: 2-tuple: so file paths, (file paths, ignored paths, failed paths)
    """
    file_paths = []
    failed_paths = []
    ignored_paths = []
    so_file_paths = []

    for dir_path in paths:
        _files, _ignores = walk_dir(dir_path, ignores)
        file_paths.extend(_files)
        ignored_paths.extend(_ignores)

    file_paths = list(set(file_paths))
    ignored_paths = list(set(ignored_paths))

    print("--------------------------------------")
    print(f"Total {len(file_paths)} files")
    for file_path in file_paths:
        try:
            so_file_paths.append(compile_one(file_path, clean_py=clean_py))
        except CompileError:
            failed_paths.append(file_path)

        c_file = file_path.replace(".py", ".c")
        if os.path.exists(c_file):
            os.remove(c_file)

    print("--------------------------------------")
    print("Compilation completed")
    print(f"Total {len(file_paths)} files")
    if ignored_paths:
        print("--------------------------------------")
        print(f"Ignore {len(ignored_paths)} files: ")
        for i in ignored_paths:
            print(i)
    if failed_paths:
        print("--------------------------------------")
        print(f"Failed {len(failed_paths)} files: ")
        for i in failed_paths:
            print(i)

    return so_file_paths, (file_paths, ignored_paths, failed_paths)


def do_compile(paths, build_dir="build", clean_py=False, ignores=None):
    base_dir = os.getcwd()
    so_file_paths, _ = _do_compile(paths, clean_py=clean_py, ignores=ignores)
    for so_file_path in so_file_paths:
        relpath = os.path.relpath(so_file_path, base_dir)
        dst = os.path.join(build_dir, relpath)
        dst_py = os.path.join(
            os.path.dirname(dst),
            os.path.basename(dst).split(".", maxsplit=1)[0] + ".py",
        )
        if os.path.exists(dst):
            shutil.move(so_file_path, dst)
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(so_file_path, dst)
        # Ensure that previously ignored .py files are removed when need to be compiled
        if os.path.exists(dst_py):
            os.remove(dst_py)


class Compiler:
    def __init__(self, config_obj: "BaseConfig" = None):
        self.config = config_obj

    def run(self):
        do_compile(
            self.config.paths,
            self.config.build_dir,
            clean_py=self.config.clean_py,
            ignores=self.config.ignores,
        )

    def init_run(self, src):
        """
        Copy src to build_dir and do compile, usually used for the first time.

        :param src: src directory
        :return:
        """
        if os.path.exists(self.config.build_dir):
            rm = input(
                f"The dst: {self.config.build_dir} is not empty, remove it (Y/n)? "
            )
            if rm.lower() != "y":
                sys.exit(1)
            shutil.rmtree(self.config.build_dir)
        shutil.copytree(
            src,
            self.config.build_dir,
            ignore=shutil.ignore_patterns(*self.config.copy_ignores)
            if self.config.copy_ignores
            else None,
        )
        os.chdir(self.config.build_dir)
        do_compile(
            self.config.paths, build_dir=".", clean_py=True, ignores=self.config.ignores
        )
