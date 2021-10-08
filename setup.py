from setuptools import find_packages, setup

setup(
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.6",
    install_requires=["Cython", "Click", "GitPython~=3.0"],
    entry_points={
        "console_scripts": [
            "encryptpy = encryptpy.__main__:main",
        ],
    },
)
