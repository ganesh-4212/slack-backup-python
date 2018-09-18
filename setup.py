from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='slack-backup',
    version='1.02',
    author="Ganesh Poojary",
    description="Tool to backup slack conversations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ganesh-4212/slack-backup-python",
    py_modules='backup',
    install_requires=[
        'Click',
        'requests'
    ],
    entry_points='''
        [console_scripts]
        slack-backup=backup:cli
    ''',
     classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
   