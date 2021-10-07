# Encrypt your Python project
Use Cython to compile Python code to binary and support `git-diff` to get changed files conveniently.

## Installation

`$ pip install encryptpy`

## Basic Usage

```
Usage: encryptpy [OPTIONS] COMMAND [ARGS]...

  Encrypt your Python code

Options:
  --config TEXT  The config file, ignore if given is invalid  [default:
                 .encryptpy.cfg]
  --help         Show this message and exit.

Commands:
  clean     Simply clean `build` and `__pycache__` directory in DIRS
  git-diff  Compile files between two COMMITS, see `git-diff`: `--name-only`
  init      Copy src to build-dir and do compile, usually used for the...
  run       Compile given Python code files

```

For the subcommand info, use `encryptpy <subcommand> --help`.

## Examples

For example, there is a package named `package_a` (notice the work directory):

`$ tree -a .`

```
.
├── .encryptpy.cfg
└── package_a
    ├── __init__.py
    ├── main.py
    ├── README.md
    ├── setup.py
    └── utils.py

1 directory, 6 files
```

The `.encryptpy.cfg`'s contents are as follow:

```ini
[encryptpy]
; Files will be compiled
paths =
    package_a
; Files will be ignored when compiling
ignores =
    setup.py
; For command `init`, files will be ignored when copying
copy_ignores =
    *.pyc
    *.md
; The build directory
build_dir = build
; For commands `run` and `git-diff`, whether the source .py will be removed
clean_py = 0
```



#### 1. Use in the first time

`$ encryptpy init . `

Look the `build` directory:

`$ tree -a build`

```
build
├── .encryptpy.cfg
└── package_a
    ├── __init__.cpython-38-x86_64-linux-gnu.so
    ├── main.cpython-38-x86_64-linux-gnu.so
    ├── setup.py
    └── utils.cpython-38-x86_64-linux-gnu.so

1 directory, 5 files
```



#### 2. Use normally by `run`

`$ encryptpy run package_a/main.py`

The `package_a/main.py` will be recompiled to `main.cpython-38-x86_64-linux-gnu.so`



#### 3. Use normally by `git-diff`

`$ encryptpy git-diff 0.1 0.2`

The changed files between tag(or commit, or branch) 0.1 and 0.2 will be compiled.
