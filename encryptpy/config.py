import configparser
import typing


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
    def paths(self):
        return []

    @property
    def ignores(self) -> typing.List[str]:
        return []

    @property
    def copy_ignores(self) -> typing.List[str]:
        return self.default.get("copy_ignores", [])

    @property
    def build_dir(self):
        return self.default.get("build_dir", "")

    @property
    def clean_py(self):
        return self.default.get("clean_py", True)

    def to_dict(self):
        return {
            "paths": self.paths,
            "ignores": self.ignores,
            "copy_ignores": self.copy_ignores,
            "build_dir": self.build_dir,
            "clean_py": self.clean_py,
        }


class Config(BaseConfig):
    """
    Config read from config file.

    """

    def __init__(
        self, filename=".encryptpy.cfg", encoding="utf-8", section="encryptpy"
    ):
        """
        :param filename: ini style config file, all paths in config should be relative to work directory
        :param encoding: file encoding
        :param section: default encryptpy section name
        """
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

    def update_from_other(self, c: "DictConfig"):
        for k, v in c.kwargs.items():
            self.kwargs[k] = v
