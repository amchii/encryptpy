import os

from setuptools import find_packages, setup

base_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_dir, "README.md"), encoding="utf-8") as fp:
    long_description = fp.read()

setup(
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["setuptools", "Cython", "Click", "GitPython~=3.0"],
    entry_points={
        "console_scripts": [
            "encryptpy = encryptpy.__main__:main",
        ],
    },
)
