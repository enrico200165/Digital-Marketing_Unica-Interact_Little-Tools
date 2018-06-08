#!/usr/bin/env python

import configparser
import globals as g
from InteractRESTCore import interactCommands as ia


def read_config_file(pathname):
    '''' just read (and parse file) '''
    config = configparser.ConfigParser()
    config.read(pathname)
    return config


def get_config_from_file(pathname = None):
    ''' extract values from parsed config'''

    pathname = g.config_file_path if pathname is None else pathname
    print("reading config file: " + pathname)
    config = read_config_file(pathname)
    # old debug: for section in config: print(section)

    # Read DB Params
    section = config['interact_profile_db']
    g.params_db = g.ParamsDB(section['db_user'], section['db_pwd']
        ,section['db_server'], section['db_name']
        ,section['db_query_whole_row'], section['db_query_attr'])

    # Read interact Params
    section = config['interact_basic_params']
    g.params_interact = g.ParamsInteract(section['endpoint_url'], section['channel']
        ,section['aud_lev_name'], section['aud_lev_field_name'])

    section = config['interact_test_params']
    g.params_test = g.ParamsTest(section['test_dflt_sess_id']
                               ,section['test_dflt_aud_id_val'])

    # Read interaction points
    ips = g.ConfigTestItemsList()
    ips.add_from_ini_cfg_sect(config['interaction_points'])

    # Read Audience IDs
    aud_ids = g.ConfigTestItemsList()
    aud_ids.add_from_ini_cfg_sect(config['audience_ids'])

    # Read Events
    g.events = g.ConfigItemCoupleList()
    g.events.add_from_ini_cfg_sect(config['interact_events'])
    for e in g.events:
        print(e)

    g.new_vistor_profile_attrs = ia.Attributes("Defaul Profile")
    g.new_vistor_profile_attrs.setFromCfgSect(config['profile_default_1'])


    return (g.params_db, g.params_interact, ips, g.params_test, aud_ids)


def printHelpCmdParams():
    ''' if present should override file '''
    s = ""
    s += "--url <interact API URL>"
    s += " --channel <interact channel>"
    s += " --aud_lev <audience level>"
    s += " --aud_fname <name of field containing audience ID>"
    s += " --sess_id <session ID> used for testing, may be overridden, see code"
    s += " --aud_id <audicence ID value> used for testing, may be overridden, see code"
    print(s)


if __name__ == '__main__':
    pass