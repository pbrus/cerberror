from importlib import import_module

import setuptools

with open("README.md", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="cerberror",
    version=import_module("cerberror").__version__,
    author=import_module("cerberror").__author__,
    description="A package allowing to define own error messages for Cerberus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pbrus/cerberror",
    packages=setuptools.find_packages(exclude=["tests"]),
    tests_require=["pytest"],
    install_requires=["setuptools", "Cerberus==1.3.2"],
    keywords=["validation", "customized", "error", "messages"],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Utilities",
    ],
)
