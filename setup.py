import setuptools

setuptools.setup(
    name="cerberror",
    packages=setuptools.find_packages(exclude=["tests"]),
    tests_require=["pytest"],
)
