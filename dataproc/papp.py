from pathlib import Path
import dataproc.configargparse as configargparse

# Todo: move paths into configargparse in papp.
# Todo: change defaultstr to use configargparse values.


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
                 , basedir=None     # Root -- handling relative pathnames.
                 , inspecs=None
                 , outspec=None
                 , group_ids=None   # If the data is naturally grouped, the Papp maintains the list of groups
                 , group_specs=None # Append the last path element (eg, filename) of every file matching these specs to the group_id list.
                 , processors=[]    # A list of processor objects to apply
                 ):


        cap = configargparse.ArgParser(
            appdir_conf=True)
        self.cap = cap

        self.basedir = Path.home()
        self.basedir = self.str2path(basedir)

        assert isinstance(group_ids,list) or isinstance(group_ids,type(None))
        self.group_ids = group_ids or []

    def config_parser(self):
        # This is where all configuration options are defined.
        pass


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
