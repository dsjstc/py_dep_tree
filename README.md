### Dependency Tree

This basically supports Makefile-like dependency checking in python.

The problem boils down to "If file A depends on file B, then check whether file B 
has been modified more recently than file A."  Obviously, this can get complex with large trees of dependencies that might have 
interlinking between branches. 

#### DepTree

Nodes are manually created, and are each characterized by a manually set mtime.

#### FDepTree

Every node is a file, characterized by its mtime_ns

### FRDepTree

_Not yet implemented_

Use case: 
  - Given a bunch of CSVs in each of many VID directorys 
    - eg1: .../src/[VID]/*.csv
    - eg2: .../src/[VID]-*.csv
  - For each VID filespec, we wish to depend a separate .../db/VID.pickle 

Simple solution:
  - create every parent db/VID node.
  - for each such parent, create a regex matching the path of all dependencies
  - create a dependent regex node.
  
Hard solution:
  - define a search that extracts the VID from the parent node
  - use a subexpression to create a dependent node for each match.   
 