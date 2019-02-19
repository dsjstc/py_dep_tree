import inspect
from pathlib import PosixPath

# Generalized dependency tree.
# Think of each node as a file which...
#   1. may depend on one or more other nodes (dependencies)
#   2. may be depended on other nodes (dependent)
#   3. is considered "dirty" (needs rebuild) if any dependency has a later mtime.
#      ie, (child.mtime > self.mtime)
#
# This class is essentially virtual -- you must manually set mtimes.  See fdeptree for a useful example
#
# NB that self.children is an OrderedDict where all values are None.
#

class DepTree:
    def __init__(self, children=None, name=None, mtime=0):
        if children == None:
            self.children = []
        elif type(children) == type(self):
            self.children = [children]
        elif type(children) == list:
            self.children = children
        else:
            assert False

        self.knownDirty = False  # IE, has not yet been shown to be dirty
        self.mtime = mtime
        self.name = name

    def isDirty(self):
        # This is only for performance -- it stops recursing a tree as soon as it's known to be dirty.

        # First test all immediate children
        for c in self.children:
            if( c.knownDirty == True
            or c.mtime > self.mtime):  # NB that *same* time presumed clean.
                self.knownDirty = True
                break

        # Then recurse
        for c in self.children:
            if c.isDirty():
                self.knownDirty = True
                break

        return self.knownDirty

    def walk(self, func):
        for c in self.children:
            c.walk(func)
        func(self)

    def getDirty(self):
        # returns a bottom-up ordered list of all the dirty nodes in the tree

        dirtykids = []
        if len(self.children) == 0:
            return None  # don't want to be appending empty lists

        # start with the list of dirty children
        for c in self.children:
            dirtlist = c.getDirty()
            # Add only new elements
            if not dirtlist:
                continue
            for d in dirtlist:
                if not d in dirtykids:
                    assert isinstance(d,DepTree)
                    dirtykids.append( d )

        # append self, if dirty
        for c in self.children:
            if( c.knownDirty
            or c.mtime > self.mtime):
                self.knownDirty = True
                if not self in dirtykids:
                    assert isinstance(self, DepTree)
                    dirtykids.append(self)

        if len(dirtykids) > 0:
            self.knownDirty = True

        return dirtykids

    def add_child(self,child):
        # but don't add dups
        if not child in self.children:
            self.children.append(child)


    def get_name(self):
        if hasattr(self,"name"):
            return self.name

        # Dirty hack to give useful names for testing
        # Search parent's globals, find first name referencing self
        ans = []
        frame = inspect.currentframe().f_back
        tmp = dict(list(frame.f_globals.items()) + list(frame.f_locals.items()))
        for k, var in tmp.items():
            if k == 'self': continue
            if isinstance(var, self.__class__):
                if hash(self) == hash(var):
                    return k
        return None

    def __str__(self):
        return ("%s: %r" % (self.get_name(), self.knownDirty))

    def __repr__(self):
        s = self.get_name()
        return s
        #return 'dep'

    def printwalk(self):
        for d in self.getDirty():
            print(d)

    @staticmethod
    def from_dict_tree(tree, parent=None):
        # Adds tree to parentnode.  Create parentnode if necessary.

        # Step 1: Create root node if necessary
        if parent==None:
            # Create and return the root node
            if len(tree) == 1:
                # tree root *is* the root node.
                rootkey = list(tree)[0]
                root = DepTree(name=rootkey)
                DepTree.from_dict_tree(tree[rootkey], root)
            elif len(tree) > 1:
                # tree starts wide; create a virtual root node
                root = DepTree(name=None)
                DepTree.from_dict_tree(tree, root)
            else:
                assert False # tree < 1 element?
            return root

        # Step 2: graft tree onto parent
        if tree == None:
            return
        elif type(tree) == dict:
            # grafts every element in tree as a child of parent
            for k in tree.keys():
                node = DepTree(name=k)
                parent.add_child(node)
                DepTree.from_dict_tree(tree[k], node)
        elif type(tree) == list:
            for v in tree:
                DepTree.from_dict_tree(v, parent)
        else: # leaf, presumably
            node = DepTree(name=tree)
            parent.add_child(node)

# Todo: move test into the test file

if __name__ == '__main__':
    pass
