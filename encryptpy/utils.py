import os
import re
import shutil
import typing


def suffix_match(s, regexs: typing.List[str]) -> bool:
    for pattern in regexs:
        if not pattern.startswith(r".*?"):
            pattern = r".*?" + pattern

        if re.match(pattern, s):
            return True
    return False


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
        if path.endswith(".py"):
            if suffix_match(path, ignores):
                ignored_files.append(path)
            else:
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
            if suffix_match(full_path, ignores):
                ignored_files.append(full_path)
                ignored = True
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
