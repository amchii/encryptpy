import os

from setuptools import find_packages, setup

base_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_dir, "README.md"), encoding="utf-8") as fp:
    long_description = fp.read()

setup(
    name="encryptpy",
    version="1.0.0",
    url="https://github.com/amchii/encryptpy",
    project_urls={"Source": "https://github.com/amchii/encryptpy"},
    license="MIT",
    author="Amchii",
    author_email="finethankuandyou@gmail.com",
    description="Use Cython to compile Python code to binary and support git-diff to get changed files conveniently.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=["Cython", "Click", "GitPython~=3.0"],
    entry_points={
        "console_scripts": [
            "encryptpy = encryptpy.__main__:main",
        ],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Compilers",
    ],
)
