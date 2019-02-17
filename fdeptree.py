from pathlib import Path
from deptree import DepTree

# Dependency tree specialized for files

class FDepTree(DepTree):
    def __init__(self, filepath, children=None):
        super().__init__(children=children)

        if filepath == None:
            # Virtual root node, in case there are *many* top-level ones
            self.filepath = None
            self.mtime = float('inf') # Never dirty.
        else:
            self.filepath = Path(filepath)  # permit string paths
            assert isinstance(filepath,Path)
            self.name = filepath.parts[-1]

            if filepath.exists():
                self.mtime = filepath.stat().st_mtime_ns
            else:
                self.mtime = 0 # always assumed dirty

    def __str__(self):
        return ("%s: %r (%s)" % (self.get_name(), self.knownDirty,self.filepath))

    @staticmethod
    def globnodes(globlist, path=Path.cwd(),children=None):
        # Returns a list of FDepTrees from the argued glob strings

        if type(globlist) == str:
            globlist = [globlist]

        results = []
        for g in globlist:
            files = path.glob(g)
            results.extend(files)

        nodes = []
        for f in results:
            c = FDepTree(filepath=f, children=children)
            nodes.append( c )

        return nodes

    @staticmethod
    def appendtree(parentnode, tree, workdir):
        # Same as in deptree, but every leaf might represents
        # a glob of filenames in workdir
        assert isinstance(workdir,Path)

        # Step 1: Create root node if necessary
        if parentnode==None:
            # Create and return the root node
            if len(tree) == 1:
                # tree root *is* the root node.
                rootkey = list(tree)[0]
                root = FDepTree(filepath=Path(workdir,rootkey))
                FDepTree.appendtree(root,tree[rootkey],workdir)
            elif len(tree) > 1:
                # tree starts wide; create a virtual root node
                root = FDepTree(filepath=None)
                FDepTree.appendtree(root, tree,workdir)
            else:
                assert False # tree < 1 element?
            return root

        # Step 2: graft tree onto parent
        assert isinstance(parentnode, FDepTree)
        if tree == None:
            return
        elif type(tree) == dict:
            # grafts every element in tree as a child of parent
            for k in tree.keys():
                node = FDepTree(filepath=Path(workdir,k))
                parentnode.children[node] = None
                FDepTree.appendtree(node, tree[k],workdir)
        elif type(tree) == list:
            for v in tree:
                FDepTree.appendtree(parentnode, v)
        else:  # leaf, presumably
            for f in workdir.glob(tree):
                node = FDepTree(filepath=f)
                parentnode.children[node] = None

def eg1():
    sessiondir = Path('/tmp/test')
    clist = FDepTree.globnodes('c*',sessiondir)
    b1 = FDepTree( Path(sessiondir,'b1'), clist)
    b2 = FDepTree(Path(sessiondir, 'b2'))
    root = FDepTree(Path(sessiondir, 'root'), [b1,b2])

    l = root.getDirty()
    assert len(l) == 0

if __name__ == '__main__':
#def eg2():
    treeg= {'root': { 'b1': 'c*'
                     ,'b2': None}}

    sessiondir = Path('/tmp/test')
    root = FDepTree.appendtree(None,treeg,sessiondir)
    root.walk(print)

