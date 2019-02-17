import pytest
from fdeptree import FDepTree
import shutil
from pathlib import Path
import time
import tempfile

class MedTree:
    def __init__(self, tempdir):
        clist = FDepTree.globnodes('c*', tempdir)
        b1 = FDepTree(Path(tempdir, 'b1'), clist)
        b2 = FDepTree(Path(tempdir, 'b2'))
        self.root = FDepTree(Path(tempdir, 'root'), [b1, b2])

class MedTreeLit:
    # Same as above, but declared as a literal.
    def __init__(self, tempdir):
        mtl = { 'root': [
                 {'b1': 'c*'}
                ,{'b2': None }
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

def test_globnodes(sessiondir):
    fdlist = FDepTree.globnodes(['c*'],sessiondir)
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

def test_update(sessiondir):
    time.sleep(0.005) # required to guarantee an mtime_ns difference
    c1p = Path(sessiondir,'c1')
    c1p.touch()

    threedeep = MedTree(sessiondir)
    for n in threedeep.root.getDirty():
        for c in n.children:
            time.sleep(0.005)  # required to guarantee an mtime_ns difference
            shutil.copy(c.filepath,n.filepath)

    threedeep2 = MedTree(sessiondir)
    dirty = threedeep2.root.isDirty()
    assert not dirty


