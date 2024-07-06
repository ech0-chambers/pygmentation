from pathlib import Path
from setuptools import setup

setup(
    name='pygmentation',
    version='0.1',
    packages=['pygmentation'],
    install_requires=[
        "numpy",
        "rich",
    ],
    entry_points={
        'console_scripts': [
            'pygmentation = pygmentation.__main__:main',
        ],
    },
    package_data={
        'pygmentation': ['color_schemes.json'],
    },
    include_package_data=True,
)