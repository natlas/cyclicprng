from setuptools import setup

with open("README.md") as rfile:
    long_description = rfile.read()

setup(
    name="cyclicprng",
    version="0.1.0",
    author="Ross Snider",
    maintainer="0xdade",
    maintainer_email="dade@actualcrimes.org",
    py_modules=["cyclicprng"],
    url="http://pypi.python.org/pypi/cyclicprng/",
    license="Apache 2.0",
    description=("Efficiently initialize and iterate a cyclic prng."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    install_requires=["sympy"],
)
