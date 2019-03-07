from pathlib import Path
from obs_deptree.deptree_base import DepTree

# Dependency tree specialized for files
# A node is defined by a  glob string indicating a file path.
from obs_deptree.fdeptree import FDepTree

class Dnode():
    # This is a single node in a dependency tree.
    def __init__(self
                 , children=[]
                 , name=None
                 , filepath=None
                 , globstr=None):

        assert isinstance(children,list)
        self.children = list

        assert (name is None) or isinstance(name,str)
        self.name = name

        assert (filepath is None) or isinstance(filepath,Path)
        self.filepath = filepath

        assert (globstr is None) or isinstance(globstr,str)
        self.globstr = globstr


class DTree(DepTree):
    default_dir = Path.home()

    def __init__(self, root=None):
        super().__init__(root)

        self.basedir = self.default_dir
        if filepath:
            if filepath.isfile():
                self.basedir = filepath.parent
            else:
                self.basedir = filepath

        if (filepath == None) & (globstr == None):
            # Virtual root node, in case there are *many* top-level ones
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
                self._max_mtime = self._min_mtime = 0 # Not-yet-generated; always dirty.
        else:
            # globstr is defined; matches many files.
            # If filepath is also defined, it's a directory to prepend to the globstr
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

    ####################################################################################
    # Generation

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
    def from_dict_tree(tree, parent=None, filedir = None, expand_leaves=True):
        # Same as in deptree, but every leaf might represent
        # a glob of filenames in filedir
        #
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
                root = GFDepTree(name=rootkey, filepath=self.str2path(rootkey))
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

    ####################################################################################
    # Utility
    def str2path(self,stringpath, defaultstr=None):
        # returns an absolute Path(), expanding a stringpath which is:
        # Relative: tack on to self.basedir
        # Absolute: use it.
        # None: use defaultstr instead.

        if not hasattr(self, 'basedir'):
            self.basedir = Path.home()
        if stringpath == None:
            return Path(self.basedir, defaultstr)
        elif Path(stringpath).is_absolute():
            return Path(stringpath)
        else:  # relative stringpath
            return Path(self.basedir, stringpath)


    def __str__(self):
        return ("%s: %r (%s)" % (self.get_name(), self.knownDirty, self.filepath))


if __name__ == '__main__':
#def eg2():
    treeg= {'root': { 'b1': 'c*'
                     ,'b2': None}}

    GFDepTree.default_dir = Path('/tmp/test')

    root = FDepTree.from_dict_tree(treeg, None)
    root.walk(print)
