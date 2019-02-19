from pathlib import Path
from deptree import DepTree

# Dependency tree specialized for files

class FDepTree(DepTree):
    default_dir = Path.home()

    def __init__(self, children=None, name=None, filepath = None):
        super().__init__(children=children)

        if filepath == None:
            # Virtual root node, in case there are *many* top-level ones
            self.filepath = None
            self.mtime = float('inf') # Never dirty.
        else:
            self.filepath = Path(filepath)  # permit string paths
            assert isinstance(filepath,Path)
            if not name:
                self.name = filepath.parts[-1]

            if filepath.exists():
                self.mtime = filepath.stat().st_mtime_ns
            else:
                self.mtime = 0 # always assumed dirty

    def __str__(self):
        return ("%s: %r (%s)" % (self.get_name(), self.knownDirty,self.filepath))

    @staticmethod
    def globnodes(globlist, filepath=Path.cwd(), children=None):
        # Returns a list of FDepTrees from the argued glob strings

        if type(globlist) == str:
            globlist = [globlist]

        results = []
        for g in globlist:
            files = filepath.glob(g)
            results.extend(files)

        nodes = []
        for f in results:
            c = FDepTree(filepath = f, children=children)
            nodes.append( c )

        return nodes

    @staticmethod
    def from_dict_tree(tree, parent=None, filedir = None):
        # Same as in deptree, but every leaf might represents
        # a glob of filenames in workdir
        workdir = filedir or FDepTree.default_dir
        assert isinstance(workdir, Path)

        # Step 1: Create root node if necessary
        if parent==None:
            # Create and return the root node
            if len(tree) == 1:
                # tree root *is* the root node.
                rootkey = list(tree)[0]
                root = FDepTree()
                FDepTree.from_dict_tree(tree[rootkey], root)
            elif len(tree) > 1:
                # tree starts wide; create a virtual root node
                root = FDepTree()
                FDepTree.from_dict_tree(tree, root)
            else:
                assert False # tree < 1 element?
            return root

        # Step 2: graft tree onto parent
        assert isinstance(parent, FDepTree)
        if tree == None:
            return
        elif type(tree) == dict:
            # grafts every element in tree as a child of parent
            for k in tree.keys():
                node = FDepTree()
                parent.add_child(node)
                FDepTree.from_dict_tree(tree[k], node)
        elif type(tree) == list:
            for v in tree:
                FDepTree.from_dict_tree(v, parent)
        else:  # leaf, presumably
            for f in workdir.glob(tree):
                node = FDepTree(name=f)
                parent.add_child(node)

def eg1():
    sessiondir = Path('/tmp/test')
    clist = FDepTree.globnodes('c*',sessiondir)
    b1 = FDepTree(clist, Path(sessiondir, 'b1'))
    b2 = FDepTree(Path(sessiondir, 'b2'))
    root = FDepTree([b1, b2], Path(sessiondir, 'root'))

    l = root.getDirty()
    assert len(l) == 0

if __name__ == '__main__':
#def eg2():
    treeg= {'root': { 'b1': 'c*'
                     ,'b2': None}}

    sessiondir = Path('/tmp/test')
    root = FDepTree.from_dict_tree(treeg, None)
    root.walk(print)
