"""
Naruhodo 0.2.7

A python library for automatic semantic graph generation from human-readable text.

## Change-Log

# 0.2.7
  * Added new edge types: "para", "attr", "stat".
  * Tweaks for naruhodo-viewer's clustering function. 
* 0.2.6
  * Improved subject & object searching logic.
  * Removed some debugging output.
  * Added 'yomi' and 'sub' property to nodes.
* 0.2.5
  * Restricted the source node of 'aux' edges to certain node types(stored in EntityTypeDict).
  * Added 'yomi' property to CaboChunks.
  * Added word embedding cosine similarity threshold for synonym identification.
* 0.2.4
  * Refactored KSG core for better code clearance and some bug fixes.
* 0.2.3
  * Fixed a bug in KSG core causing repetitive nodes added to graph.
* 0.2.2
  * Tweaks for use with naruhodo-viewer.
* 0.2.1
  * Primitive coreference resolution for Japanese.
* 0.2.0
  * Major API change for multi-language support and parallel processing. 
  * Parallel processing support for parsing using multiprocessing module. 
* 0.1.0
  * Initial version

"""

from naruhodo.core.parser import parser