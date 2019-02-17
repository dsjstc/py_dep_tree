import inspect
from collections import OrderedDict

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
    def __init__(self, name=None, children=None, mtime=0):
        if children == None:
            self.children = OrderedDict()
        elif type(children) == type(self):
            self.children = OrderedDict({children:None}) # Protect against common use case
        else:
            self.children = children

        self.knownDirty = False  # IE, has not yet been shown to be dirty
        self.mtime = mtime
        self.name = name

    def isDirty(self):
        # This is only for performance -- it stops recursing a tree as soon as it's known to be dirty.

        # First test all immediate children
        for c in self.children:
            if( c.knownDirty == True
            or c.mtime >= self.mtime):  # same time can't be known to be clean.
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
        # returns a bottom-up ordered list of dirty children
        dd = self._getDirtyDict()
        if dd: return list(dd.keys())
        else: return []

    def _getDirtyDict(self):
        # returns a bottom-up OrderedDict of all the dirty nodes in the tree
        # the Odict is used to ensure uniqueness and preserve order.

        dirtykids = OrderedDict() # unique and keeps order
        if len(self.children) == 0:
            return None  # don't want to be appending empty lists

        # start with the list of dirty children
        for c in self.children:
            d = c._getDirtyDict()
            if d: dirtykids.update( d )

        # append self, if dirty
        for c in self.children:
            if( c.knownDirty
            or c.mtime > self.mtime):
                self.knownDirty = True
                dirtykids[self]=None

        if len(dirtykids) > 0:
            self.knownDirty = True

        return dirtykids

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
        for d in self._getDirtyDict():
            print(d)

    @staticmethod
    def appendtree(parentnode, tree):
        # Step 1: Create root node if necessary
        if parentnode==None:
            # Create and return the root node
            if len(tree) == 1:
                # tree root *is* the root node.
                rootkey = list(tree)[0]
                root = DepTree(name=rootkey)
                DepTree.appendtree(root,tree[rootkey])
            elif len(tree) > 1:
                # tree starts wide; create a virtual root node
                root = DepTree(name=None)
                DepTree.appendtree(root, tree)
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
                parentnode.children[node] = None
                DepTree.appendtree(node,tree[k])
        elif type(tree) == list:
            for v in tree:
                DepTree.appendtree(parentnode,v)
        else: # leaf, presumably
            node = DepTree(name=tree)
            parentnode.children[node] = None


if __name__ == '__main__':
    treeg= {'base': { 'b1': ['cb1a', 'cb1b']
                     ,'b2': 'cb2'}}
    root = DepTree.appendtree(parentnode=None,tree=treeg)

    def make1dirty(x):
        if x.name == 'cb2': x.mtime = 5
    root.walk(make1dirty)
    l = root.getDirty()
    print(l)

