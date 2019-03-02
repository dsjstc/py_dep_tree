import sys

import appdirs
import configargparse
from pathlib import Path

# Extra configargparse functionality.
# 1. Defaults to singleton behaviour
# 2. Add argument appdir_conf
#       =True --> searches for `appname.py`.conf in system-appropriate config directories
#       ='App'  --> searches for App.conf in system-appropriate config directories

class Vconf (configargparse.ArgParser):
    singleton = None

    def __init__(self, appname=None, parsedir=None):
        # Assume singleton use without requiring it.

        #if self.singleton == None or not hasattr(self,'singleton'):
        #    Vconf.singleton = self



        # Get a list of platform independent directories where config files might live
        parsedir = Path(Path.home(), parsedir, 'config')
        d = appdirs.AppDirs('fcparser','aju')
        configdirs =[Path(d.site_config_dir), Path(d.user_config_dir), parsedir]

        self.appname = appname or


        # Remember what we've decided here.
        self.basedir = parsedir
        self.d = d

        # Initialize the base class
        got = configargparse.get_argument_parser('default')
        configargparse.ArgParser.__init__(self, default_config_files=configdirs)

        self.add('-c', '--config', required=False, is_config_file=True, help='config file path')


    @staticmethod
    def get_argument_parser(name=None, **kwargs):
        p = configargparse.get_argument_parser()

    def dump(self):
        self.cap.print_values()

if __name__ == '__main__':
    configargparse.init_argument_parser('default')
    single = configargparse.get_argument_parser('default')
    vc = Vconf()
    got = configargparse.get_argument_parser('default')
    got.print_values()
