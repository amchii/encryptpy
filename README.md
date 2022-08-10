[简体中文](https://github.com/amchii/encryptpy/blob/main/README_CN.md)

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
; Files will be ignored when compiling, support Regex
ignores =
    setup.py
; For command `init`, files will be ignored when copying, Glob-style
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

The `package_a/main.py` will be recompiled to `package_amain.cpython-38-x86_64-linux-gnu.so`



#### 3. Use normally by `git-diff`

`$ encryptpy git-diff 0.1 0.2`

The changed files between tag(or commit, or branch) 0.1 and 0.2 will be compiled.

## Defect

The defects mainly come from Cython - some Python code can not be compiled correctly. Here are known issues:

1. ~~Assignment Expressions `:=`: [Implement PEP 572: Assignment Expressions #2636](https://github.com/cython/cython/issues/2636)~~

2. ~~@dataclass: [Implement @dataclass for cdef classes #2903](https://github.com/cython/cython/issues/2903)~~

3. Class method decorators combination: [Combining @staticmethod with other decorators is broken #1434](https://github.com/cython/cython/issues/1434)

   e.g.

   ```python
   class C:
       @staticmethod
       @some_decorator
       def f():
           pass
   ```

   but this can be rewrite to `f = staticmethod(some_decorator(f))`, it's ok.

If you have some code like the above, you can refactor or just ignore them, it is safe enough for most projects.

**2022.08.10 UPDATE:** It seems that the first two defects have been resolved.
