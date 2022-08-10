[English](README.md)

# 加密你的Python项目

使用Cython将Python代码编译为二进制以达到加密的目的，并且支持通过`git-diff`来获取两次提交间的差异文件，方便地进行编译。



## 安装

`$ pip install encryptpy`

## 基本用法

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

子命令用法可以使用`encryptpy <subcommand> --help`来查看。



## 例子

比如当前路径下有一个包名叫`package_a`，其目录结构如下：

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

配置文件 `.encryptpy.cfg`的内容如下

```ini
[encryptpy]
; 将被编译的文件
paths =
    package_a
; 编译时忽略的文件，支持正则
ignores =
    setup.py
; 用于子命令`init`, 拷贝项目时会忽略的文件，Glob风格
copy_ignores =
    *.pyc
    *.md
; The build directory
build_dir = build
; 用于子命令`run` and `git-diff`, 编译后是否移除源.py文件
clean_py = 0
```



#### 1. 项目第一次使用

`$ encryptpy init . `

查看`build`目录：

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



#### 2. 使用`run`

`$ encryptpy run package_a/main.py`

文件 `package_a/main.py` 会被重新编译至 `package_a/main.cpython-38-x86_64-linux-gnu.so`。



#### 3. 使用 `git-diff`

`$ encryptpy git-diff 0.1 0.2`

标签（或commit，或branch）0.1和0.2之间的差异文件会被编译。

## 缺陷

主要的缺陷来自于Cython，一些Python语法无法被正确地编译，以下是已知的问题：

1. ~~赋值表达式（海象运算符） `:=`: [Implement PEP 572: Assignment Expressions #2636](https://github.com/cython/cython/issues/2636)~~

2. ~~@dataclass:  [Implement @dataclass for cdef classes #2903](https://github.com/cython/cython/issues/2903)~~

3. Class method decorators combination: [Combining @staticmethod with other decorators is broken #1434](https://github.com/cython/cython/issues/1434)

   e.g.

   ```python
   class C:
       @staticmethod
       @some_decorator
       def f():
           pass
   ```

   但是可以改写为 `f = staticmethod(some_decorator(f))`。

如果你有一些和上面一样的代码，要么改写要么简单地忽略它们，毕竟对大多数项目来说展示一些代码不影响其安全。



**2022.08.10 UPDATE:** 好像前两个issue已经解决了。
