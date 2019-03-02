import sys
from pathlib import Path


# Todo: move paths into configargparse in papp.
# Todo: change defaultstr to use configargparse values.

# Case 1:
#   /final <-- /a1, /a2
# Case 2:
#   /final <-- /a*
# Case 3:
#   /db/final <-- /src/a*/*
# Case 4:
#   /db/(a*) <-- /src/\1/*
#   IE: each a* relies on a separate directory full of files.
# Case n:
# (VID*)/*.csv -> db/db-\1.pickle
#    This means process every VID separately.
from typing import Union

name = 'processor'
_singleton_papp = None


def get_papp(basedir = None):
    global _singleton_papp
    if _singleton_papp is None:
        _singleton_papp = Papp(basedir)
    elif basedir is not None:
        assert basedir == _singleton_papp.basedir

    return _singleton_papp


# This singleton class provides all global configuration
class Papp():
    def __init__(self
                 , basedir=None     # Root of tree for processing input and output files.
                 , group_ids=None   # If the data is naturally grouped, the Papp maintains the list of groups
                 , group_specs=None # Append the last path element (eg, filename) of every file matching these specs to the group_id list.
                 ):
        self.basedir = Path.home()
        self.basedir = self.str2path(basedir)

        assert isinstance(group_ids,list) or isinstance(group_ids,type(None))
        self.group_ids = group_ids or []

    def str2path(self, stringpath, defaultstr=None):
        # Determines an absolute path, based on appropriate precedence:

        if stringpath is not None:
            if Path(stringpath).is_absolute():
                return Path(stringpath)
            else:  # relative stringpath
                return Path(self.basedir, stringpath)
        else:  # stringpath is None
            if defaultstr == None: return Path(self.basedir)
            return Path(self.basedir, defaultstr)


def Processor():
    # Processes a single pair of pspecs.
    def __init__(self
                 , input: Pspec
                 , output: Pspec
                 , singlethreaded: bool = False):
        self.app = get_papp()

    def go(self):
        pass


class Pspec():
    # This is a glorified wrapper of a directory and a string.
    # The string represents file(s) inside the directory
    # The string may include subdirectories

    def __init__(self, specs:Union[str, Path, list]=None, dir=None, papp=None):
    #def __init__(self, spec=None, dir=None, papp=None):
        self.app = papp or get_papp()
        self.dir = self.app.str2path(dir)
        if isinstance(specs,Path) or isinstance(specs,str):
            self.specs = [specs]
        else: self.specs = specs

        self.evaluate_spec()

    def evaluate_spec(self, specs:list=None):
        specs = specs or self.specs

        # Set filecount, min_mtime, max_mtime
        self.filecount = 0
        self._biggest_mtime = 0
        self._smallest_mtime = float('inf')

        for spec in specs:
            if isinstance(spec,Path):
                # Case 1: spec is a simple file.
                p = Path(self.dir, spec)
                if p.is_file():
                    self.filecount += 1
                    self._biggest_mtime = self._smallest_mtime = p.stat().st_mtime_ns
            else:
                # Case 2: spec is a pathglob
                expandedlist = expand_pathglobs(spec, self.dir)
                for f in expandedlist:
                    if not f.exists(): continue
                    self.filecount += 1
                    mt = f.stat().st_mtime_ns
                    if mt < self._smallest_mtime: self._smallest_mtime = mt
                    if mt > self._biggest_mtime: self._biggest_mtime = mt

    def is_dirtied_by(self, child):
        return self.is_partly_older_than(child)

    def is_partly_older_than(self, other):
        # "self" is older (for at least one file)
        # than this specific, non-recursive child
        # older times are smaller; older := <
        if hasattr(other, '_smallest_mtime'):  # Another Pspec
            return self._smallest_mtime < other._biggest_mtime
        elif hasattr(other, '_mtime'):  # A deptree, for example
            return self._smallest_mtime < other._mtime
        elif isinstance(other, Path):  # A file
            mt = other.stat().st_mtime_ns
            rc = self._smallest_mtime < mt
            return rc
        else:
            assert False  # Cannot compare



def Processor():
    def __init__(self
                 , input: Pspec
                 , output: Pspec
                 , singlethreaded: bool = False):
        self.app = get_papp()

        # An inputstr might be
        # 1. A path (no stars, no parens)
        # 2. A globpath
        # 3. A globpath with subexpressions

    def go(self):
        pass


def expand_pathglobs(pathparts, basepaths=None):
    # Posted to https://stackoverflow.com/a/54936154/5368599
    # Logic:
    # 0. Argue with a Path(str).parts and optional ['/start','/dirs'].
    # 1. for each basepath, expand out pathparts[0] into "expandedpaths"
    # 2. If there are no more pathparts, expandedpaths is the result.
    # 3. Otherwise, recurse with expandedpaths and the remaining pathparts.
    # eg: expand_pathglobs('/tmp/a*/b*')
    #   --> /tmp/a1/b1
    #   --> /tmp/a2/b2

    if isinstance(pathparts, str) or isinstance(pathparts, Path):
        pathparts = Path(pathparts).parts
    if isinstance(basepaths, Path):
        basepaths = [basepaths]

    if basepaths == None:
        return expand_pathglobs(pathparts[1:], [Path(pathparts[0])])
    else:
        assert pathparts[0] != '/'

    expandedpaths = []
    for p in basepaths:
        assert isinstance(p, Path)
        globs = p.glob(pathparts[0])
        for g in globs:
            expandedpaths.append(g)

    if len(pathparts) > 1:
        return expand_pathglobs(pathparts[1:], expandedpaths)

    return expandedpaths
