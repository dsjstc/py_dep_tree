import shutil
import time
from pathlib import Path

import processor
import pytest


@pytest.fixture
def cleandir(request):
    '''
    /final (depends on a*)
    /a1
    /a2
    '''

    base = Path('/tmp/test/')
    shutil.rmtree(base,ignore_errors=True) # Cleanup before starting
    base.mkdir(parents=True)
    for f in ['a2','a1','final']:
        Path(base,f).touch()
    return base


@pytest.fixture
def deepdir(request):
    # This uses a hard directory instead of a proper temp file, in order to allow
    # investigation on failure.  It contains the following structure:
    '''
    /db/
        final   (depends on db/int)
        int     (depends on db/[ab]*)
        a1      (depends on src/a1/*)
        a2      (depends on src/a2/*)
        b1      (depends on src/b1*)
        b2      (depends on src/b2*)
    /src/a1/
            a11
            a12
    /src/a2/
            a21
            a22
    '''

    base = Path('/tmp/test/')
    shutil.rmtree(base,ignore_errors=True) # Cleanup before starting

    src = Path(base,'src')
    src.mkdir(parents=True)
    for f in ['a11','a12','a21','a22']:
        p = Path(src,f)
        p.touch()
    db = Path(base,'db')
    db.mkdir(parents=True)
    for f in ['a1','a2','int','final']:
        Path(db,f).touch()

    # request.addfinalizer(lambda: shutil.rmtree(hd,ignore_errors=True))
    return base

###########################################
# PApp tests
###########################################
def test_papp():
    a1 = processor.get_papp()
    a2 = processor.get_papp()
    assert a1 == a2
    assert a1.basedir == a2.basedir

###########################################
# PSpec tests
###########################################
def test_pspec_single(cleandir):
    papp = processor.Papp(basedir=cleandir)
    f = processor.Pspec(specs='final', papp=papp)
    #f = processor.Pspec('final', h, papp)
    assert f.dir == Path('/tmp/test/')
    assert f.filecount == 1
    fp = Path(f.dir,'final')
    assert not f.is_partly_older_than(fp)

def test_pspec_wild(cleandir):
    papp = processor.Papp(basedir=cleandir)
    a = processor.Pspec('a*',papp=papp)
    assert a.dir == Path('/tmp/test/')
    assert a.filecount == 2

def test_pspec_multiple(cleandir):
    papp = processor.Papp(basedir=cleandir)
    a = processor.Pspec(['a1','a2'],papp=papp)
    assert a.dir == Path('/tmp/test/')
    assert a.filecount == 2

def test_pspec_deep(deepdir):
    papp = processor.Papp(basedir=deepdir)
    f = processor.Pspec('db/final',papp=papp)
    assert f.filecount == 1
    a = processor.Pspec('s*/a*',papp=papp)
    assert a.filecount == 4
    assert not f.is_partly_older_than(a)
    a11 = Path(deepdir,'src/a11')
    time.sleep(0.005) # required to guarantee an mtime_ns difference
    a11.touch()
    assert f.is_dirtied_by(a11)
    a.evaluate_spec()
    assert f.is_dirtied_by(a)

