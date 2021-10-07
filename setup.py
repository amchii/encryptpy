from setuptools import find_packages, setup

setup(
    name="encryptpy",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["Cython", "Click", "GitPython~=3.0"],
    entry_points={
        "console_scripts": [
            "encryptpy = encryptpy.__main__:main",
        ],
    },
)
