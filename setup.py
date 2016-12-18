# Automatically created by: shub deploy

from setuptools import setup, find_packages

setup(
    name         = 'amazon',
    version      = '1.0',
    packages     = find_packages(),
    package_data={
        'amazon': ['spiders/itemDetails.json']
    },
    entry_points = {'scrapy': ['settings = amazon.settings']},
    include_package_data=True,
)
