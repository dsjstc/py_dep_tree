from pathlib import Path
from deptree import DepTree

# Dependency tree specialized for files
# A node is a single file/directory

class FDepTree(DepTree):
    default_dir = Path.home()

    def __init__(self, children=None, name=None, filepath = None):
        super().__init__(children=children)

        self.name = name
        if filepath == None:
            # Virtual root node, in case there are *many* top-level ones
            self.filepath = None
            self._mtime = float('inf') # Never dirty.
        else:
            self.filepath = Path(filepath)  # permit string paths
            assert isinstance(filepath,Path)
            if self.name == None: self.name = filepath.parts[-1]

            if filepath.exists():
                self._mtime = filepath.stat().st_mtime_ns
            else:
                self._mtime = 0 # always assumed dirty

    def __str__(self):
        return ("%s: %r (%s)" % (self.get_name(), self.knownDirty,self.filepath))

    @staticmethod
    def expand_glob_to_nodes(globlist, filepath=Path.cwd(), children=None):
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
                FDepTree.from_dict_tree(tree[rootkey], root,filedir = workdir)
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
                node = FDepTree(name=k, filepath=Path(workdir,k))
                parent.add_child(node)
                FDepTree.from_dict_tree(tree[k], node, filedir = workdir)
        elif type(tree) == list:
            for v in tree:
                FDepTree.from_dict_tree(v, parent, filedir = workdir)
        else:  # leaf, presumably
            for f in workdir.glob(tree):
                fn = f.parts[-1]
                node = FDepTree(name=fn, filepath=f)
                parent.add_child(node)

if __name__ == '__main__':
#def eg2():
    treeg= {'root': { 'b1': 'c*'
                     ,'b2': None}}

    sessiondir = Path('/tmp/test')
    root = FDepTree.from_dict_tree(treeg, None)
    root.walk(print)
