# Naruhodo(なるほど)

[![Build Status](https://travis-ci.org/superkerokero/naruhodo.svg?branch=master)](https://travis-ci.org/superkerokero/naruhodo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Naruhodo is a python library for generating dependency-graph(DG) and knowledge-graph(KG) in networkx format from Japanese text or urls that contains Japanese texts. You can visualize these graphs directly in jupyter notebook or export graphs to JSON file for visualization using external programs.

### Dependency graph (DG)

[Dependency grammar](https://en.wikipedia.org/wiki/Dependency_grammar) is a class of modern syntactic theories that are all based on the dependency relation (as opposed to the constituency relation) and that can be traced back primarily to the work of Lucien Tesnière. Dependency is the notion that linguistic units, e.g. words, are connected to each other by directed links.

[Dependency parsing](https://web.stanford.edu/~jurafsky/slp3/14.pdf) is the analysis of dependency grammar on a block of text using computer programs. 
The directed linking nature of dependency grammar makes the result of dependency parsing directed graphs.

Naruhodo generates denpendency graphs(DG) directly from the output of dependency parsing programs.

## Installation

You can install the library directly from github using pip:

```bash
pip install git+https://github.com/superkerokero/naruhodo.git
```

Naruhodo relies on external programs to do Japanese word and dependency parsing, so you need to have corresponding programs installed as well.

Naruhodo is designed to support multiple backend parsers, but currently only the support for `mecab` + `cabocha` is implemented.

For guide on installing `mecab` and `cabocha`, please refer to this page:

[Amazon Linux に MeCab と CaboCha をインストール](https://qiita.com/january108/items/85c80769ea870c190eaa)

Support for other parsers such as `KNP` is planned in the future.

## Tutorial on how to use the library

I have made a jupyter notebook for the tutorial of naruhodo.
