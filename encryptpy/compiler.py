import configparser
import os
import re
import shutil
import sys
import tempfile
import typing
from distutils.command.build_py import build_py
from distutils.core import setup

from Cython.Build import cythonize

build_py.get_package_dir = lambda *args: ""


class CompileError(Exception):
    pass


def walk_dir(path, ignores: typing.List[str] = None):
    """
    :param path: file or directory
    :param ignores: list of regex pattern
    :return:
    """
    ignores = ignores or []
    path = os.path.abspath(path)
    files = []
    ignored_files = []
    if os.path.isfile(path):
        files.append(path)
        return files, ignored_files

    for dirpath, dirnames, filenames in os.walk(path):
        if "__pycache__" in dirpath:
            continue
        for filename in filenames:
            if not filename.endswith(".py"):
                continue

            full_path = os.path.join(dirpath, filename)
            ignored = False
            for ignore_pattern in ignores:
                if not ignore_pattern.startswith(r".*?"):
                    ignore_pattern = r".*?" + ignore_pattern

                if re.match(ignore_pattern, full_path):
                    ignored_files.append(full_path)
                    ignored = True
                    break
            if not ignored:
                files.append(full_path)

    return files, ignored_files


def cleanup(dir_paths):
    print("--------------------------------------")
    print("Cleaning")
    need_delete_dirs = []
    deleted_dirs = []
    for dir_path in dir_paths:
        for dirpath, dirnames, filenames in os.walk(dir_path):
            if dirpath.endswith("build") or dirpath.endswith("__pycache__"):
                need_delete_dirs.append(dirpath)
    for _dir in need_delete_dirs:
        shutil.rmtree(_dir, ignore_errors=True)
        deleted_dirs.append(_dir)

    print("--------------------------------------")
    print("Clean up done")
    print("Deleted dirs: ")
    for i in deleted_dirs:
        print(i)


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
        if os.path.exists(dst):
            shutil.move(so_file_path, dst)
        else:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(so_file_path, dst)


def copy_and_compile(src, build_dir="build", copy_ignores=None):
    """
    Copy src to build_dir and do compile, usually used for the first time.

    :param src: src directory
    :param build_dir: dst build directory
    :param copy_ignores: ignore during copying
    :return:
    """
    if os.path.exists(build_dir):
        rm = input(f"The dst: {build_dir} is not empty, remove it (Y/n)? ")
        if rm.lower() != "y":
            sys.exit(1)
        shutil.rmtree(build_dir)
    shutil.copytree(
        src, build_dir, ignore=(lambda *args: copy_ignores) if copy_ignores else None
    )
    os.chdir(build_dir)


class BaseConfig:
    default = {
        "copy_ignores": [
            "venv",
            "logs",
            ".git",
            ".idea",
            ".vscode",
            "__pycache__",
        ],
        "clean_py": True,
        "build_dir": "build",
    }

    @property
    def dirs(self):
        return []

    @property
    def paths(self):
        return self.dirs

    @property
    def ignores(self) -> typing.List[str]:
        return []

    @property
    def copy_ignores(self) -> typing.List[str]:
        return self.default.get("copy_ignores", [])

    @property
    def build_dir(self):
        return self.default.get("build", "")

    @property
    def clean_py(self):
        return self.default.get("clean_py", True)


class Config(BaseConfig):
    def __init__(
        self, filename=".encryptpy.cfg", encoding="utf-8", section="encryptpy"
    ):
        self._filename = filename
        self.section = section
        self.parser = configparser.ConfigParser()
        with open(filename, encoding=encoding) as fp:
            self.parser.read_file(fp, filename)

    def get(self, option, **kwargs):
        try:
            return self.parser.get(self.section, option, **kwargs)
        except configparser.NoOptionError:
            return None

    def getboolean(self, option, **kwargs):
        try:
            return self.parser.getboolean(self.section, option, **kwargs)
        except (configparser.NoOptionError, ValueError):
            return None

    @property
    def dirs(self) -> typing.List[str]:
        return self.paths

    @property
    def paths(self) -> typing.List[str]:
        paths_str = self.get("paths")
        return paths_str.split() if paths_str else super().paths

    @property
    def ignores(self) -> typing.List[str]:
        ignores_str = self.get("ignores")
        return ignores_str.split() if ignores_str else super().ignores

    @property
    def copy_ignores(self) -> typing.List[str]:
        ignores_str = self.get("copy_ignores")
        return ignores_str.split() if ignores_str else super().copy_ignores

    @property
    def build_dir(self) -> str:
        return self.get("build_dir") or super().build_dir

    @property
    def clean_py(self) -> bool:
        clean = self.getboolean("clean_py")
        return clean if clean is not None else super().clean_py


class DictConfig(BaseConfig):
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def __getattribute__(self, item):
        if item == "kwargs":
            return object.__getattribute__(self, item)
        if item in self.kwargs:
            return self.kwargs[item]
        return super().__getattribute__(item)


class Compiler:
    def __init__(self, config_obj: "BaseConfig" = None):
        self.config = config_obj

    def run(self):
        paths = self.config.paths
        build_dir = self.config.build_dir
        ignores = self.config.ignores
        clean_py = self.config.clean_py
        do_compile(paths, build_dir, clean_py=clean_py, ignores=ignores)


def main():
    config = Config()
    compiler = Compiler(config_obj=config)
    compiler.run()


if __name__ == "__main__":
    main()
