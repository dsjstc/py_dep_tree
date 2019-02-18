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

Every node is a regex, characterized by the min and max mtime of all files matching.
  
Dependency paths are defined by a transformed (?) subexpression of the dependency.  
  - EG, create a separate database file from each maching directory of CSVs. 
