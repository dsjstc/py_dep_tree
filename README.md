# Dependency Tree
### What is it?
This supports Makefile-like dependency checking in python.

The problem boils down to "If file A depends on file B, then check whether file B 
has been modified more recently than file A."  Obviously, this can get complex with large trees of dependencies that might have 
interlinking between branches. 

### Status
Written for personal use.  Lacks type checking, testing, and CI.

### Elements
#### DepTree

Nodes are manually created, and are each characterized by a manually set mtime.

#### FDepTree

Superceded

### GFDepTree

Use case: 
  - Given a bunch of CSVs in each of many VID directorys 
    - eg1: .../src/[VID]/*.csv
    - eg2: .../src/[VID]-*.csv
  - For each VID filespec, we wish to depend a separate .../db/VID.pickle 

Simple solution:
  - create every parent db/VID node.
  - for each such parent, create a regex matching the path of all dependencies
  - create a dependent regex node.
  
TBD Hard solution:
  - define a search that extracts the VID from the parent node
  - use a subexpression to create a dependent node for each match.   
 
Sample 
=============
NAME
  /     -> (basedir)/db/final.db
  /A    -> (basedir)/db/intermediate_a.db
  /A/AA -> (basedir)/src1/[a]/*.csv
  /A/AB -> (basedir)/src2/[glob_a].csv      [WATCHES MANY FILES]
  /B    -> (basedir)/db/intermediate_b.db
  /C    -> (basedir)/db/intermediate_c.db
  /C/ABA-> special case?                    [REFERENCE TO EXISTING NODE!]

med_tree_literal = {'/': 
                         {'a': 
                               'c*'}
                        ,{'b': None}
    ]}

NODE-BASED:
===========
r  = dnode('root','db/final.db')
a  = dnode('A','db/intermediate_a.db',parent=r)
aa = dnode('aa','db/intermediate_a.db',parent=a)

WITHOUT NAMES:
===========
This represents as:
'~db/final.db'
'~db/final.db~db/intermediate_a.db'
'~db/final.db~db/intermediate_a.db~src1/[a]/*.csv'


TREE-BASED:
===========

How to represent:
=================
1. Tree container holding nodes.
2. Root node stores tree-global info --> bad; special node.   

 
 Choices:
 1. Static basedir.  Inelegant, may have multiple trees.
 2. Specify absolute path when creating every node.  Annoying.
 3. Root node remembers basedir, subsequent paths are relative.
    Bad: Every node needs to know root; can't create bottom-up.
 4. Tree class that holds nodes.  Seems unnecessary.      
 
 
 CRD EXAMPLE
 ==============
 
 VID -> text description of filespec glob
 [VID] -> expanded list  

ALLCDBs
    cdb-([VID]).db --> one per VID, each depending on
        db-\1.db
            ../\1/*.csv
ALLTDBs 
    tdb-([VID]).db 
        tripdb
            ../trips_and_charges/*.csv
            cdb-\1.db
        cdb-\1.db
                
 tiny
    clean
        ALLTDBS
        ALLCDBS                        
            
            
