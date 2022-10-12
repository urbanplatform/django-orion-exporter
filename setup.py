import os
from setuptools import find_packages
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="orion_exporter",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=open("requirements.txt").readlines(),
    zip_safe=False,
    license="MIT",
    description="A simple Django app for exporting models to Orion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.ubiwhere.com/mbaas/apps/orion_exporter.git",
    author="Francisco Monsanto",
    author_email="fmonsanto@ubiwhere.com",
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
