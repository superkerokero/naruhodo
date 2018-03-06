
from setuptools import setup, find_packages

setup(
    name = 'naruhodo',
    packages = find_packages(exclude=['contrib', 'docs', 'test']),
    version = '0.2.1',
    description = 'A python library for automatic semantic graph generation from human-readable text.',
    long_description = """
    A python library for automatic semantic graph generation from human-readable text.
    For detailed documentation and tutorials, visit https://github.com/superkerokero/naruhodo
    """,
    author = 'superkerokero',
    author_email = 'superkerokero@outlook.com',
    url = 'https://github.com/superkerokero/naruhodo',
    download_url = 'https://github.com/superkerokero/naruhodo/archive/master.zip',
    keywords = ['nlp', 'knowledge graph', 'knowledge representation', 'japanese'],
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
