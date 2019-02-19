import pytest
from deptree import DepTree

# A deeper tree, clean by default, structured as follows:
'''
root
    a
        aa
            aaa
            aab
        ab
    b
        ba
        bb
    c
        aab # == root.a.aa.aab
'''

class DeepTree:
    def __init__(self):
        aaa = DepTree(name='aaa')
        aab = DepTree(name='aab')
        aa = DepTree(children=[aaa, aab], name='aa')
        ab = DepTree(name='ab')
        a = DepTree(children=[aa, ab], name='a')
        bb = DepTree(name='bb')
        ba = DepTree(name='ba')
        b = DepTree(children=[ba, bb], name='b')
        c = DepTree(children=[aab], name='c')
        root = DepTree(children=[a, b, c], name='root')

        self.root = root
        self.aab = aab

class MedTree:
    def __init__(self):
        aa = DepTree(name='aa')
        a = DepTree(children=aa, name='a')
        b = DepTree(name='b')
        root = DepTree(children=[a, b], name='root')

        self.root = root
        self.aa = aa


@pytest.fixture
def deeptree():
    return DeepTree()

def test_single_isclean():
    s = DepTree()
    assert not s.isDirty()

def test_double_isclean():
    child = DepTree()
    root = DepTree([child])
    assert not root.isDirty()

def test_double_isdirty():
    child = DepTree(mtime=5)
    root = DepTree([child])
    assert root.isDirty()

def test_deeptree_isdirty(deeptree):
    deeptree.aab.mtime = 5
    assert deeptree.root.isDirty()

def test_double_getdirty():
    child = DepTree(mtime=5)
    root = DepTree([child])
    l = root.getDirty()
    assert len(l) == 1

def test_deeptree_getdirty(deeptree):
    deeptree.aab.mtime = 5
    r = deeptree.root
    l = r.getDirty()
    assert l[0].name == 'aa'
    assert l[1].name in ['a','c']
    assert l[2].name in ['a','c']
    assert l[3].name == 'root'
    assert len(l) == 4
    #for d in l: print(d)

def test_walkdeep(deeptree):
    r = deeptree.root
    r.walk(print)

def test_fromliteral():
    treeg= {'base': { 'b1': ['cb1a', 'cb1b']
                     ,'b2': 'cb2'}}
    root = DepTree.from_dict_tree(tree=treeg)

    def make1dirty(x):
        if x.name == 'cb2': x.mtime = 5

    root.walk(make1dirty)
    l = root.getDirty()
    print(l)
