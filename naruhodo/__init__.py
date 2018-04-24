"""
# Naruhodo 0.2.9

A python library for automatic semantic graph generation from human-readable text.

## Change-Log

### 0.2.9
  * Some bug fix in KSG.
  * Moved parser._preprocessText() to utils.misc.preprocessText().
  * Change sub to obj when adding passive predicates in KSG.
  * Modified synonym/coreference resolution for better accuracy in some situations(still not recomended though). 
### 0.2.8
  * Added new node properties: "passive", "negative", "compulsory", "question", "tense".
  * Added coref variable in parser class to turn automatic synonym/coreference resulution ON/OFF.
  * Added path plotting capability to parser.show. Now this function accepts an optional path(list of nodes) and will plot it if given.
  * Added new function parser.toText. This function takes in a path and generate texts from it. If no path is given, it will generate texts using the entire graph.
  * Added "depth" option to show functions for plotting with depth information(DSG only).
### 0.2.7
  * Added new edge types: "para", "attr", "stat".
  * Tweaks for naruhodo-viewer's clustering function. 
### 0.2.6
  * Improved subject & object searching logic.
  * Removed some debugging output.
  * Added 'yomi' and 'sub' property to nodes.
### 0.2.5
  * Restricted the source node of 'aux' edges to certain node types(stored in EntityTypeDict).
  * Added 'yomi' property to CaboChunks.
  * Added word embedding cosine similarity threshold for synonym identification.
### 0.2.4
  * Refactored KSG core for better code clearance and some bug fixes.
### 0.2.3
  * Fixed a bug in KSG core causing repetitive nodes added to graph.
### 0.2.2
  * Tweaks for use with naruhodo-viewer.
### 0.2.1
  * Primitive coreference resolution for Japanese.
### 0.2.0
  * Major API change for multi-language support and parallel processing. 
  * Parallel processing support for parsing using multiprocessing module. 
### 0.1.0
  * Initial version

"""

from naruhodo.core.parser import parser