
from setuptools import setup, find_packages

setup(
    name = 'naruhodo',
    packages = find_packages(exclude=['contrib', 'docs', 'test']),
    version = '0.1',
    description = 'A python library for generating dependency graph(DG) and knowledge graph(KG) from Japanese text.',
    author = 'superkerokero',
    author_email = 'superkerokero@outlook.com',
    url = 'https://github.com/superkerokero/naruhodo',
    download_url = 'https://github.com/superkerokero/naruhodo',
    keywords = ['nlp', 'japanese'],
    classifiers = [],
    license = "MIT",
    install_requires = [
        'networkx',
        'beautifulsoup4',
        'nxpd',
        'lxml'
    ],
)
