from pathlib import Path
from deptree import DepTree

# Dependency tree specialized for files
# A node is defined by a  glob string indicating a file path.
from fdeptree import FDepTree

class GFDepTree(FDepTree):

    def __init__(self, children=None, name=None, filepath=None, globstr=None):
        super().__init__(children=children)

        if filepath == None & globstr == None:
            # Virtual root node, in case there are *many* top-level ones
            self.filepath = None
            self._min_mtime = float('inf') # Never dirty.
        elif globstr == None:
            # Standard filepath node
            self.filepath = Path(filepath)  # permit string paths
            assert isinstance(filepath,Path)
            if not name:
                self.name = filepath.parts[-1]

            if filepath.exists():
                self._max_mtime = self._min_mtime = filepath.stat().st_mtime_ns
            else:
                self._max_mtime = self._min_mtime = 0 # IE, real children are always newer.
        else:
            # globstr is defined; make a filelist.
            # If filepath is defined, it's a directory to prepend to the globstr
            p = Path(filepath or self.default_dir)
            self.get_glob_mtimes(p,globstr)


    def get_glob_mtimes(self,filepath,globstr):
        for f in filepath.glob(globstr):
            mt = f.stat().st_mtime_ns
            if mt < self._min_mtime: self._min_mtime = mt
            if mt > self._max_mtime: self._max_mtime = mt

    def is_older_than(self,childGFDepTree):
        # This specific, non-recursive child makes Self dirty iff...
        # iff any element of child is newer than any element of self.
        # EG, if newest element of child is newer than oldest element of self.
        if isinstance(childGFDepTree,GFDepTree):
            return childGFDepTree._max_mtime > self._min_mtime
        else:
            return childGFDepTree._mtime > self._min_mtime

    def __str__(self):
        return ("%s: %r (%s)" % (self.get_name(), self.knownDirty,self.filepath))

    @staticmethod
    def from_dict_tree(tree, parent=None, filedir = None, expand_leaves=True):
        # Same as in deptree, but every leaf might represents
        # a glob of filenames in workdir
        # expand_leaves = False: keep the leaves as globs.

        assert not expand_leaves # not implemented!

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
    clist = FDepTree.expand_glob_to_nodes('c*', sessiondir)
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
