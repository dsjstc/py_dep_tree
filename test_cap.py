import configargparse

def test_appdir():
    p = configargparse.get_argument_parser(name='test_cap', appdir_conf=True)
    #p = configargparse.ArgParser(appdir_conf=True)
