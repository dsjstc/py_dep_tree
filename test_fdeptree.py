import pytest
from fdeptree import FDepTree
import shutil
from pathlib import Path
import time
import tempfile

class MedTree:
    def __init__(self, tempdir):
        clist = FDepTree.expand_glob_to_nodes('c*', filepath=tempdir)
        b1 = FDepTree(children=clist, filepath=Path(tempdir,'b1'))
        b2 = FDepTree(filepath=Path(tempdir,'b2'))
        self.root = FDepTree([b1, b2], filepath=Path(tempdir, 'root'))

med_tree_literal = {'root': [
        {'b1': 'c*'}
        , {'b2': None}
    ]}

@pytest.fixture
def sessiondir(request):
    # This uses a hard directory instead of a proper temp file, in order to allow
    # investigation on failure.
    hd = Path('/tmp/test/')
    shutil.rmtree(hd,ignore_errors=True) # Cleanup before starting
    hd.mkdir()
    for f in ['c1','c2','b1','b2','root']:
        Path(hd,f).touch()

    #request.addfinalizer(lambda: shutil.rmtree(hd,ignore_errors=True))
    return hd

@pytest.fixture
def threedeep(request,sessiondir):
    root = FDepTree.from_dict_tree(med_tree_literal, filedir=sessiondir)
    return root

def test_from_tree(threedeep,sessiondir):
    constructed = MedTree(sessiondir).root
    literal = threedeep
    assert len(constructed.children) == len(literal.children)
    assert constructed.children[0].name == literal.children[0].name
    assert len(constructed.children[1].children) == len(literal.children[1].children)


def test_globnodes(sessiondir):
    fdlist = FDepTree.expand_glob_to_nodes(['c*'], sessiondir)
    assert len(fdlist) == 2

def test_clean(threedeep):
    l = threedeep.getDirty()
    assert len(l) == 0

def test_dirty(sessiondir):
    time.sleep(0.005) # required to guarantee an mtime_ns difference
    c1p = Path(sessiondir,'c1')
    c1p.touch()

    threedeep = MedTree(sessiondir)
    root = threedeep.root
    l = root.getDirty()
    assert len(l) == 2
    #for n in l: print(n)

def test_update(sessiondir,threedeep):
    time.sleep(0.005) # required to guarantee an mtime_ns difference
    c1p = Path(sessiondir,'c1')
    c1p.touch()

    mt = MedTree(sessiondir)
    dirtlist = mt.root.getDirty()
    for n in dirtlist:
        if not n.filepath: continue
        for c in n.children:
            if not c.filepath: continue
            time.sleep(0.005)  # required to guarantee an mtime_ns difference
            shutil.copy(c.filepath,n.filepath)

    mt2 = MedTree(sessiondir)
    dirty = mt2.root.isDirty()
    assert not dirty
