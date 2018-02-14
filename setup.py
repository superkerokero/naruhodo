
from setuptools import setup, find_packages

setup(
    name = 'naruhodo',
    packages = find_packages(exclude=['contrib', 'docs', 'test']),
    version = '0.1.5',
    description = 'A python library for generating dependency graph(DG) and knowledge graph(KG) from Japanese text.',
    long_description = """
    Naruhodo is a python library for generating dependency-graph(DG) and knowledge-graph(KG) in networkx format from Japanese text or urls that contains Japanese texts. You can visualize these graphs directly in jupyter notebook or export graphs to JSON file for visualization using external programs.
    For detailed documentation and tutorials, visit https://github.com/superkerokero/naruhodo
    """,
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
    python_requires='>=3.4',
)
