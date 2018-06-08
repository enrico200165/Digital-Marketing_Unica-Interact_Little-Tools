#!/usr/bin/env python

import logging
import argparse
import copy

import EVNetUtils
import config_files as cfg

''' =============================================
horror and evil!!! GLOBAL VARIABLES
================================================= '''

# some of these really is a constant, not so evil ;-)
config_file_path = "../../../../data_dev/jlr/interact_tester.ini"
DESIRED_ENCODING = "utf-8"

log = None
fiddlerProxy = {}
argpars = None
uaci_params = None
session_id = 88888
audienceID_field_name = None
interactive_channel=None
audience_level = None
audienceID = None

numeric_default = 1

not_found = "not-found" # created for (missing)attribute values


'''list where the key is not fixed'''
class ConfigItemCoupleList(object):
    def __init__(self, items_list = None):
        if items_list is None:
            self._items = []
        else:
            if not isinstance(items_list,list):
                raise TypeError
            else:
                self.add_list(items_list)

    def add(self, couple):
        self._items.append(couple)
        return self

    def add_from_ini_cfg_sect(self, cfg_sect):
        for first, second in cfg_sect.items():
            self.add((first, second))
        return self

    def __iter__(self):
        return self._items.__iter__()

    def __next__(self):
        self._items.__next__()

events = None



# just to print out to log, when testing
verification_header = "\n### --------- {} --------- ###"


class ParamsDB(object):
    def __init__(self, user, pwd, server, name, query_wr, query_attr):
        self.db_user = user
        self.db_pwd = pwd
        self.db_server = server
        self.db_name = name
        self.db_query_whole_row = query_wr
        self.db_query_attr = query_attr


params_db = None


class ParamsInteract(object):
    def __init__(self,endpoint_url, channel, aud_lev_name, aud_lev_field_name):
        self._endpoint_url = endpoint_url
        self._channel = channel
        self._aud_lev_name = aud_lev_name
        self._aud_lev_field_name = aud_lev_field_name


params_interact = None


class ConfigTestItemsList(object):
    def __init__(self, items_list = None):
        if items_list is None:
            self._items = []
            self._items_test = {}
        else:
            if not isinstance(items_list,list):
                raise TypeError
            else:
                self.add_list(items_list)

    def add(self, item, testIt = True):
        self._items.append(item)
        if testIt is not None and (testIt or testIt == 1 or testIt == 'y'):
            self._items_test[item] = True
        else:
            self._items_test[item] = False
        return self

    def add_from_ini_cfg_sect(self, cfg_sect):
        for item, testIt in cfg_sect.items():
            self.add(item, testIt)
        return self

    def add_list(self, items_list):
        for item in items_list:
            self.append(item)
        return self


interaction_points = ["HeroImage","RegisterYourInterest", "WhatIsImportantToYou"]
audienceIDs = None
new_vistor_profile_attrs = None

class ParamsTest(object):
    def __init__(self,test_dflt_sess_id, test_dflt_aud_id_val):
        self._test_dflt_sess_id = test_dflt_sess_id
        self._test_dflt_aud_id_val = test_dflt_aud_id_val

params_test = None


class InteractParamsBundle(object):
    def __init__(self, url, channel,session_id, audience_level, audienceID_field_name, audience_ID_val):
        self._url = url
        self._channel = channel
        self._session_id = session_id
        self._audience_level = audience_level
        self._audienceID_field_name = audienceID_field_name
        self._audienceID_val = audience_ID_val

    def setAll(self, url, channel, session_id, audience_level, audienceID_field_name
        ,audience_ID_val, force=False):
        self._url = url if force or self._url is None else self._url
        self._channel = channel if force or self._channel is None else self._channel
        self._session_id = session_id if force or self._session_id is None else self._session_id
        self._audience_level = audience_level if force or self._audience_level is None else self._audience_level
        self._audienceID_field_name = audienceID_field_name if force or self._audienceID_field_name is None else self._audienceID_field_name
        self._audienceID_val = audience_ID_val if force or self._audience_ID_val is None else self._audience_ID_val

    def setInteractBasicParams(self, url, channel, audience_level, audienceID_field_name
        ,force = False):
        self._url = url if force or self._url is None else self._url
        self._channel = channel if force or self._channel is None else self._channel
        self._audience_level = audience_level if force or self._audience_level is None else self._audience_level
        self._audienceID_field_name = audienceID_field_name if force or self._audienceID_field_name is None else self._audienceID_field_name

    def setInteractBasicParamsFromObj(self, obj,force = False):
        if not isinstance(obj,ParamsInteract):
            raise TypeError
        self.setInteractBasicParams(obj._endpoint_url, obj._channel
            ,obj._aud_lev_name, obj._aud_lev_field_name)

    def setTestparam(self, testpar):
        if not isinstance(testpar, ParamsTest):
            raise TypeError
        self._session_id = testpar._test_dflt_sess_id
        self._audienceID_val = testpar._test_dflt_aud_id_val

    def get_url(self):
        return self._url

    def get_channel(self):
        return self._channel

    def set_channel(self, channel):
        self._channel = channel

    def get_session_id(self):
        return self._session_id

    def get_audience_level(self):
        return self._audience_level

    def get_audienceID_field_name(self):
        return self._audienceID_field_name

    def get_audience_ID_val(self):
        return self._audienceID_val

    def set_audience_ID(self,id):
        self._audienceID_val = id

    def deepcopy(self):
        new = copy.deepcopy(self)
        return new

    def setSessionID(self, id):
        self._session_id = id

def parseCmdLinePars():
    argpars  = argparse.ArgumentParser()
    argpars.add_argument("--url",help = "Interact REST Endpoint URL")
    argpars.add_argument("--channel", help="Channel Name")
    argpars.add_argument("--aud_lev", help="Audience Level")
    argpars.add_argument("--aud_fname", help="Audience Field Name")
    argpars.add_argument("--sess_id", help="Session ID")
    argpars.add_argument("--aud_id", help="Audience ID")
    args = argpars.parse_args()
    return args


def init(unitTestRun = False):
    '''
    Manage inizializations
    unitTestRun:
    with unit tests something may miss (command line parameter) and
    because of that code fail, flag that case and avoid some operations
    :return:
    '''
    global log, argpars, uaci_params

        # g.info(sys.path())
    logging.basicConfig(filename="interactREST.log", level=logging.INFO)
    log = logging.getLogger()
    log.addHandler(logging.StreamHandler())

    # reads config file OUTSIDE of project
    # as it contains DB credentials
    cfg.get_config_from_file()

    args_cmd_line = parseCmdLinePars()
    uaci_params = InteractParamsBundle(args_cmd_line.url, args_cmd_line.channel
        ,args_cmd_line.sess_id,"Online", args_cmd_line.aud_fname, args_cmd_line.aud_id)

    uaci_params.setInteractBasicParamsFromObj(params_interact, force= False)
    uaci_params.setTestparam(params_test)

    log.info("interact endpoint: " + uaci_params.get_url())
