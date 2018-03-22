#!/usr/bin/env python

import json
import sys
import unittest
import numbers
import pprint
import re
import requests
import time
import datetime
import copy

import globals as g
import EVNetUtils


def get_type(val):
    if (isinstance(val, str)):
        return "string"
    elif (isinstance(val, numbers.Number)):
        return "numeric"
    elif (isinstance(val, datetime.date)):
        return "date"
    else:
        sys.exit(-1)


def double_curly(s):
    '''
    to use format, DUMB, always doubles
    :param s:
    :return:
    '''
    s = s.replace("{","{{")
    s = s.replace("}","}}")
    return s


# KEPT, not sure will use it
def batch_wrap(# sessionID,
        commands):
    s = '{{"sessionId":"#(sessionID#)","commands":[ {} ]}}'
    cmdsList = ""

    if not isinstance(commands,list):
        cl = list()
        cl.append(commands)
        commands = cl

    first = True
    for c in commands:
        if not first:
            cmdsList += ","
        if not isinstance(c,JSONCmd):
            raise Exception
        cmdsList += c.get_json()
        first = False
    s = s.format(cmdsList)
    s = double_curly(s)
    s = s.replace("#(","{")
    s = s.replace("#)","}")
    return s

# KEPT, not sure will use it
def wrap_command(sessionID, commandString):
    s = '{{"sessionId":{},"commands":[ {} ]}}'.format(sessionID,commandString)
    return s


def wrap_response(sessionID, commandString):
    s = '{{"batchStatusCode":{},"responses":[{}]}}'.format(sessionID,commandString)
    # g.log.info(s)
    return s




def decode(s):
    try:
        return s.decode(g.DESIRED_ENCODING)
    except:
        return s


def clean_json(s):
    ret = s.replace('\r\n', ' ')
    ret = ret.replace('\n', ' ')
    ret = re.sub(" +", " ", ret)
    return ret


class NV(object):
    ''' Actual trivial name value pair
    '''
    def __init__(self, name,value):
        self._data = { name : value}

    def get_json(self):
        return json.dumps(self._data, indent=4)


class JSONMapped(object):
    ''' Pompous name for something very trivial, just trying to group
    elementary methods for reading writing from JSon
    Emulating a basic java interface or C++ pure virtual class

    Added "late" due to hurry, so probably derived classes do (simple)
    work that could be done at this level and reused via call to super()
    '''
    def __init__(self):
        pass

    def get_json(self):
        raise NotImplementedError

    def set_from_json(self, jstring):
        raise NotImplementedError

    def dump(self, verbose):
        raise NotImplementedError


class NameValuePairImpl(JSONMapped):
    ''' Provide "standard" storage for attributes
    Wraps the 3entries dictionaries used by interact
    An interact NameValuePairImpl so  actually three pair that verbosely
    express name value and type
    '''
    def __init__(self):
        super().__init__()
        self._data = { "n": None, "v": None, "t": None }

    def set_from_2pars(self, name,value):
        self._data = { "n": None, "v": None, "t": None }
        if  all(v is not None for v in [value, name]):
            self._data["v"] = value
            self._data["t"] = get_type(value)
            self._data["n"] = name
        else:
            raise SystemExit
            # just to remember, normal way would be sys.exit()

    def set_from_tuple(self, tuple):
        self._data["n"] = tuple[0].lower()
        self._data["t"] = tuple[1]
        self._data["v"] = tuple[2]
        return self

    def set_from_basic_attr(self, data):
        ''' from the elementary dict with entries "n" "v"  "t" '''
        self._data = data
        return self

    def get_json(self):
        ret = clean_json(json.dumps(self._data))
        return ret

    def dump(self, verbose):
        return self.get_json()

    def get_name(self):
        return self._data["n"]

    def get_value(self):
        return self._data["v"]

    def get_type(self):
        return self._data["t"]


class Attributes(JSONMapped):
    ''' Common elementary functionalities for a set of attributes
    Currently based on a DICT with
        key: attribute name
        value: NameValuePairImpl()
    '''

    def __init__(self, descr_name,attr_tuple = None):
        self._attrs_d = {} # list of will contain NameValuePairImpl
        if (attr_tuple != None):
            self.add_tuple(attr_tuple)
        self._descr_name = descr_name # just for developer's comfort during testing

    def get_descr_name(self):
        return self._descr_name

    def set_descr_name(self, descr_name):
        self._descr_name = descr_name

    def len(self):
        if self._attrs_d is None:
            return 0
        return len(self._attrs_d)

    def add_tuple(self, attr_tuple):
        if attr_tuple is not None and type(attr_tuple) is tuple:
            attr = NameValuePairImpl().set_from_tuple(attr_tuple)
            self._attrs_d[attr.get_name()] = attr
        else:
            raise TypeError
        pass

    def add_namve_value_par_impl(self,nvp):
        if nvp is None:
            pass
        if not isinstance(nvp,NameValuePairImpl):
            raise TypeError
        self._attrs_d[nvp.get_name()] = nvp

    def set_from_json(self, jstring, descr_name):
        self.set_descr_name(descr_name)
        glob_dict = json.loads(jstring)

        # this is dirty due to arry, we attempt
        # try more general case
        if 'parameters' in glob_dict['commands'][0]:
            attrs_list = glob_dict['commands'][0]['parameters']
        else:
            attrs_list = []

        for attr in attrs_list:
            nvp = NameValuePairImpl().set_from_basic_attr(attr)
            self.add_namve_value_par_impl(nvp)

    def setFromCfgSect(self, cfgSect):
        try:
            for key, value in cfgSect.items():
                type, value = value.split(",")
                self.add_tuple((key,type,value))
        except ValueError as v:
            g.log.error(v)
        return self

    def get_json(self):
        if self._attrs_d is None or len(self._attrs_d) == 0:
            return ""
        s,i,l = "[{}]", 1, ""
        for k in self._attrs_d:
            if i  > 1:
                l += ","
            l += self._attrs_d[k].get_json()
            i += 1
        s = s.format(l)
        return clean_json(s)

    def deepcopy(self, descr_name = None):
        new_copy = copy.deepcopy(self)
        if descr_name is not None:
            new_copy.set_descr_name(descr_name)
        else:
            new_copy.set_descr_name("deep copy of "+ self.get_descr_name())
        return new_copy

    def dump(self, verbose = False):
        if verbose:
            # pprint.PrettyPrinter(indent=4).pprint(clean_json(self.get_json()))
            g.log.info("attributes of [{}], raw json (MAY BE EMPTY): ".format(self.get_descr_name())
                       +clean_json(self.get_json()))
        t = ' ### [{}] attributes pretty print:'.format(self.get_descr_name())
        s = ""
        keys = sorted(self._attrs_d.keys())
        for k in keys:
            # s += self._attrs_d[k].get_json()+" \n"
            s += "\n{} = {} ({})".format(self._attrs_d[k].get_name(),self._attrs_d[k].get_value()
                                         ,self._attrs_d[k].get_type())
        if len(s) <= 0:
            s = " (no attributes found)"
        g.log.info(t+s)
        return s

    def set_attribute(self, name, value, type = None, strict = True):
        if strict and not name in self._attrs_d:
            g.log.info("cannot set <"+name+"> attribute does not exit")
            raise Exception
        if type is None:
            type = get_type(value)
        self._attrs_d[name] = NameValuePairImpl().set_from_tuple((name,type,value))
        pass

    def get_attribute_value(self, name):
        if name not in self._attrs_d:
            return None
        return self._attrs_d[name].get_value()

    def left_compare(self, other):
        '''  check if all attributes are present in "other", with same value
        note that other might have other attributes not present here
        '''
        equal = True
        differences = []
        for k in self._attrs_d:
            if other.get_attribute_value(k) != None:
                if other.get_attribute_value(k) == self.get_attribute_value(k):
                    continue
            differences.append(k)
        return differences

    def right_compare(self, other):
        return other.left_compare(self)


    def full_compare(self, other):
        return list(set(self.left_compare(other)+other.left_compare(self)))

    def compare_values(self,other,keys):
        s = ""
        diff_found = False
        sorted_keys = sorted(keys)
        for k in sorted_keys:
            diff_found = True
            s += "\n" + k + " =  (\"" + self.get_descr_name() + "\" = "
            s += str(self.get_attribute_value(k)) if self.get_attribute_value(k) != None else g.not_found
            s += ") (\""+other.get_descr_name()+ " = (\""
            s += str(other.get_attribute_value(k)) if other.get_attribute_value(k) != None else g.not_found
            s += ")"
        if not diff_found:
            s = "no diff found between \"{}\", \"{}\"".format(self.get_descr_name(), other.get_descr_name())
        g.log.info(s)

    def left_print_side_2_side(self,other ):
        sorted_keys = self._attrs_d
        s = "side by side attributes"
        for k in sorted_keys:
            s += "[{}] values in ".format(k)
            s += '({}) vs. ({})'.format(self.get_descr_name(),other.get_descr_name())
            s += "\n{}\n{}\n".format (self.get_attribute_value(k), other.get_attribute_value(k))
        g.log.info(s)


class JSONCmd(object):
    ''' Common elementary functionalities
    '''
    def __init__(self, uaci_params):
        self._uaci_params = uaci_params
        self._time_msec = -999
        self._req_json = None
        self._resp_json = None
        self._data_dict = None

    def get_json(self):
        s = wrap_command(self._uaci_params.get_session_id(), self.get_bare_json())
        return s

    def get_bare_json(self):
        raise NotImplemented

    # EV check delete if it does not work
    def get_send_attributes(self, descr_name = None):
        ''' Only to facilitate one debug
        return Attributes() with attributes sent
        :return:
        '''
        if descr_name is None:
            descr_name = "attributes sent at "+str(datetime.datetime.now())
        send_attributes = Attributes(descr_name)
        j = self.get_json()
        send_attributes.set_from_json(j,descr_name)
        return send_attributes

    @staticmethod
    def clean_json(s):
        return clean_json(s)

    def get_rsp_json(self):
        return self._resp_json

    def set_from_json(self, jstring):
        j = decode(jstring)
        self._resp_json = j
        self._data_dict = json.loads(j)
        pass

    def set_json_from_rsp(self, rsp):
        self.set_from_json(rsp.content)

    def dump(self, verbose = False):
        if verbose:
            g.log.info("REQUEST json")
            if self.get_json() is not None:
                #pprint.PrettyPrinter(indent=4).pprint(clean_json(self.get_json()))
                g.log.info(clean_json(self.get_json()))
            else:
                g.log.info("REQUEST json NOT SET")
            g.log.info("RESPONSE json")
            if self.get_rsp_json() is not None:
                # pprint.PrettyPrinter(indent=4).pprint(clean_json(self.get_rsp_json()))
                g.log.info(clean_json(self.get_rsp_json()))
            else:
                g.log.info("RESPONSE json NOT SET")
        else:
            pass
        return None # just to debug/break

    def call_simple(self, dumpOnError = False):
        resp = myREST(self.get_json(), self._uaci_params.get_url(), False)
        self.set_json_from_rsp(resp)
        if not self.OK():
            s = "{} call failed, batch code {batch_code}".format(type(self).__name__
                                                                 ,batch_code = self._data_dict['batchStatusCode'])
            for resp in self._data_dict['responses']:
                s += " resp code {}".format(resp['statusCode'])
                g.log.warning(s)
            if dumpOnError:
                self.dump(True)
            else:
                pass

        return self.OK()

    def call(self, verbose = False, dumpOnError = False, dumpAttributes = False):
        start_time = time.time()
        ret = self.call_simple(dumpOnError)
        end_time = time.time()
        self._time_msec = (end_time - start_time)*1000
        if verbose:
            g.log.info("called  {:12}  at {} time = {} ".format(type(self).__name__
                                                                ,datetime.datetime.now().time(),(end_time - start_time)*1000))
            self.dump(verbose)
        if dumpAttributes:
            send_attrs = self.get_send_attributes()
            send_attrs.set_descr_name("attr of [{}]".format(type(self).__name__))
            send_attrs.dump(verbose)
        return ret

    def OK(self):
        '''
        Quick high level check
        :return:
        '''
        if self._data_dict is None or not 'batchStatusCode' in self._data_dict or self._data_dict['batchStatusCode'] is None:
            # should never happen, bug it it does
            return False

        ok = self._data_dict['batchStatusCode'] ==  0
        for resp in self._data_dict['responses']:
            ok = ok and resp['statusCode'] == 0
        if not ok:
            pass # g.log.info("")
        return ok


class GetVersion(JSONCmd):
    def __init__(self, uaci_params):
        super().__init__(uaci_params)
        self._uaci_params = uaci_params
        self._req_json = '{"action":"getVersion"}'

    def get_bare_json(self):
        s =  self._req_json
        return s


class StartSession(JSONCmd):

    def __init__(self, uaci_params, params, rely):
        super().__init__(uaci_params)
        if params != None and not isinstance(params, Attributes):
            raise TypeError
        self._attrs = params
        self._rely = rely
        self._req_json = '''
            {{
                "audienceID":[{{"v":"{aud_id}","t":"{aud_type}","n":"{aud_fname}"}}],
                "audienceLevel":"{aud_lev}",
                "ic":"{chan}",
                "relyOnExistingSession": {rely},
                "action":"startSession",
                "debug":"true"
                {params}                
            }}'''


    def get_bare_json(self):
        parStr = ''
        if self._attrs != None and self._attrs.len() > 0:
            parStr = ' ,"parameters": {attrs} '.format(attrs = self._attrs.get_json())
        s = self._req_json.format(
            chan = self._uaci_params.get_channel(),
            aud_lev = self._uaci_params.get_audience_level(),
            aud_fname = self._uaci_params.get_audienceID_field_name(),
            aud_type = get_type(self._uaci_params.get_audience_ID_val()),
            aud_id = self._uaci_params.get_audience_ID_val(),
            rely = self._rely, params = parStr)
        #s = wrap_command(self._uaci_params.get_session_id(),s)
        return s

    def get_send_attributes(self, descr_name = None):
        ''' Only to facilitate one debug
        return Attributes() with attributes sent
        :return:
        '''
        if descr_name is None:
            descr_name = "send attribues "+str(datetime.datetime.now())
        send_attributes = Attributes(descr_name)
        j = self.get_json()
        send_attributes.set_from_json(j,descr_name)
        return send_attributes

    def set_attributes(self, attrs, overwrite = False):
        if not overwrite and ( self._attrs != None and len(self._attrs) > 0 ):
            raise Exception
        self._attrs = attrs



class GetOffers(JSONCmd):

    def __init__(self, uaci_params, IP):
        super().__init__(uaci_params)
        self._uaci_params = uaci_params
        self._IP = IP
        self._req_json = '''{{"numberRequested":5,"action":"getOffers","ip":"{ip}"}}'''

    def get_bare_json(self):
        s = self._req_json.format(sess = self._uaci_params.get_session_id(), ip = self._IP)
        return s

    def set_from_json(self,jstring):
        super().set_from_json(jstring)

    def dump(self, verbose):
        spaces,indent  = 0, 4
        super().dump(verbose)
        try:
            # pprint.PrettyPrinter(indent=4).pprint(self._data_dict)
            g.log.info(" " * spaces + "batchStatusCode = {}".format(self._data_dict['batchStatusCode']))
            g.log.info(" " * spaces + "--- responses ---")
            spaces += indent
            for resp in self._data_dict['responses']:
                g.log.info(" " * spaces + "--- response ---")
                g.log.info(" " * spaces + "statusCode = {}".format(resp['statusCode']))
                g.log.info(" " * spaces + "sessionId = {}".format(resp['sessionId']))
                g.log.info(" " * spaces + "version = {}".format(resp['version']))

                g.log.info(" " * spaces + "--- Offer Lists ---")
                spaces += indent
                for offer_list in resp['offerLists']:
                    g.log.info(" " * spaces + "ip = {}".format(offer_list['ip']))

                    g.log.info(" " * spaces + " --- Offers ---")
                    try:
                        spaces += indent
                        for offer in offer_list['offers']:
                            g.log.info(" " * spaces + "--- Offer ---")
                            g.log.info(" " * spaces + "desc = {}".format(offer['desc']))
                            g.log.info(" " * spaces + "score = {}".format(offer['score']))
                            g.log.info(" " * spaces + "n = {}".format(offer['n']))
                            g.log.info(" " * spaces + "treatmentCode = {}".format(offer['treatmentCode']))
                            g.log.info(" " * spaces + "code = {}".format(offer['code']))

                            g.log.info(" " * spaces + "--- Attributes ---")
                            spaces += indent
                            for attr in offer['attributes']:
                                g.log.info(" " * spaces + "{} = {} - type: {}".format(attr['n'], attr['v'], attr['t']))
                            spaces -= indent
                        spaces -= indent
                    except KeyError:
                        g.log.info("No offers")
                spaces -= indent
            spaces -= indent
        except AttributeError as e:
            pass


class GetProfile(JSONCmd):
    '''
    '''
    def __init__(self, uaci_params):
        self._uaci_params = uaci_params
        self._data_dict = {}
        self._profile = None # set on response
        type = get_type(self._uaci_params.get_audience_ID_val())
        # self._req_json =  '''{{"sessionId":"{sess}","commands":[{{"action":"getProfile"}}]}}'''
        self._req_json =  '''{"action":"getProfile"}'''

    # def get_json(self):
    #     s = self._req_json.format(sess = self._uaci_params.get_session_id())
    #     return s
    def get_bare_json(self):
        s = self._req_json
        return s

    def get_attr(self, attr):
        return self._data_dict[attr]

    def set_from_json(self,jstring):
        super().set_from_json(jstring)
        # syntactic sugar, just aliases
        self._responses = self._data_dict['responses']
        # normally only one rest accessed via this
        self._resp = self._responses[0]
        self._profile = self._resp['profile']
        pass

    def dump_raw(self, verbose = False):
        try:
            super().dump(verbose)
            s = "audience ID: <" + str(self._uaci_params.get_audience_ID_val())+">\n"
            for attr in self._profile:
                s += "[{}] = {}".format(attr['n'], attr['v'])
                if verbose:
                    s +=  " - (type {})".format(attr['t'])
                s += "\n"
            g.log.info(s)
            # pprint.PrettyPrinter(indent=4).pprint(self._profile)
        except AttributeError as e:
            pass

    def dump(self, verbose = False):
        '''Use other class to get sort'''
        super().dump(verbose)
        attrs = self.create_Attributes("GetProfile Attributes")
        attrs.dump()

    def create_Attributes(self, name = None):
        ''' dreate Attributes object for comparisons'''
        if name is None:
            name = "from GetProfile for " + self._uaci_params.get_audience_ID_val()

        attributes = Attributes(name)
        if self._profile is None:
            g.log.error("no attributes present")
            return attributes
        for attr in self._profile:
            attributes.add_tuple((attr["n"],attr["t"],attr["v"]))
        return attributes


class PostEvent(JSONCmd):
    '''
    '''
    def __init__(self, uaci_params, evt):
        self._uaci_params = uaci_params
        self._event = evt
        self._attrs = Attributes(None)
        self._req_json =  '''{{
                "event":"{evt}",
                "action":"postEvent"
                {params}                
        }}'''

    def get_bare_json(self):
        parStr = ''
        if self._attrs != None and self._attrs.len() > 0:
            parStr = ' ,"parameters": {attrs} '.format(attrs = self._attrs.get_json())

        s = self._req_json.format(evt = self._event, params = parStr)
        return clean_json(s)

    def sett_attrs(self, attrs):
        if not isinstance(attrs,Attributes):
            raise TypeError
        self._attrs = attrs

    def set_from_json(self,jstring):
        super().set_from_json(jstring)
        pass

    def dump(self, verbose):
        super().dump(verbose)
        # g.log.info(self.get_json())
        # g.log.info(self.get_rsp_json())


class EndSession(JSONCmd):

    def __init__(self, uaci_params):
        super().__init__(uaci_params)
        self._uaci_params = uaci_params
        # self._req_json = '''
        # {{"sessionId":"{sess}","commands":[{{"action":"endSession"}}]}}
        # '''
        self._req_json = '''{"action":"endSession"}'''

    # def get_json(self):
    #     s = self._req_json.format(sess = self._uaci_params.get_session_id())
    #     return s
    def get_bare_json(self):
        s = self._req_json
        return s


class SetDebug(JSONCmd):

    def __init__(self, uaci_params,debug):
        super().__init__(uaci_params)
        self._uaci_params = uaci_params
        self._debug = debug
        self._req_json = '''{{"action":"setDebug","debug":{dbg}}}'''

    def get_bare_json(self):
        debug = "True" if self._debug else "False"
        s = self._req_json.format(dbg = debug)
        return s


class BatchCmds(JSONCmd):
    def __init__(self, uaci_params, cmdsList = None):
        super().__init__(uaci_params)
        self._uaci_params = uaci_params
        if cmdsList is not None:
            if ( not isinstance(cmdsList, list) or
                not isinstance(cmdsList[0], JSONCmd)):
                g.log.error("BatchCmds received non None wrong data as commands list")
                raise Exception
            else:
                self._cmdsList = cmdsList
        else:
            self._cmdsList = list()
        self._req_json = '''{{sorry, no json yet}}'''

    def get_bare_json(self):
        s = ""
        first = True
        for c in self._cmdsList:
            if not first:
                s += ","
            else:
                first = False
            s += c.get_bare_json()
        return s

    def set_json_from_rsp(self, rsp):
        self.set_from_json(rsp.content)


    def set_from_json(self, jstring):
        ''' extract the parts for each command and rewrap them as
        now all commands expect to find the wrapper'''
        j = decode(jstring)
        all_rsps = json.loads(j) # dicts are easier to manage
        for i, c in enumerate(self._cmdsList):
            # g.log.info(i)
            c_rsp = all_rsps['responses'][i] # resp of object
            c_bare_rsp_json = json.dumps(c_rsp) # to json
            # wrap it in batch wrapper as commands now all process that
            c_rsp_json = wrap_response(c_rsp['statusCode'], c_bare_rsp_json)
            c.set_from_json(c_rsp_json )
        # after setting the commands included in the batch
        # set itself, as it is treated as a command from code
        self._resp_json = j
        self._data_dict = json.loads(j)
        pass

    def append(self, cmd):
        self._cmdsList.append(cmd)
        return self



def myREST(bodyJson, UACIUrl, verbose):
    global log
    ret = requests.post(UACIUrl, headers=EVNetUtils.head, data = bodyJson
                        , proxies = g.fiddlerProxy)
    # adjust from bytes to string
    if (not ret.ok):
        g.log.info("error")
    if (verbose or not ret.ok):
        g.log.info("response content:\n");
        g.log.info(ret.content)
    return ret


def callAPI(cmd):
    if not isinstance(cmd, JSONCmd):
        raise TypeError

    resp = myREST(cmd.get_json(), False)
    cmd.set_json_from_rsp(resp)
    if not cmd.OK():
        cmd.dump(True)
        return False
    return True


def API_unit_test(uaci_params, inter_point):
    '''
    One method of calling the Interact API is by using JSON over HTTP
    The REST API returns SessionIDs and messages in the HTML-escaped
    format and not in the Unicode format.

    :return:
    '''

    global head, log

    ok = True
    # GET VERSION
    # ok = ok and callAPI(GetVersion(sess_id))
    ok = ok and GetVersion(uaci_params).call(True)

    # START SESSION
    ok = ok and StartSession(uaci_params, None,"false").call(True)

    #  GET OFFERS
    ok = ok and GetOffers(uaci_params, g.interaction_points[0]).call(True)

    #  POST EVENT
    eventNameString = g.events[0][0]
    po = PostEvent(uaci_params,eventNameString)
    ok = ok and po.call(True)
    # add a couple of attrributes
    attrs = Attributes(('ds_segment',"string","enrico_ds_segment"))
    attrs.add_tuple(('ds_cmp_1', 'numeric',0.0))
    po.sett_attrs(attrs)
    ok = ok and  po.call(True)

    #  GET PROFILE
    ok = ok and GetProfile(uaci_params).call(True)

    #  SET DEBUG
    ok = ok and SetDebug(uaci_params,False).call(True)
    ok = ok and SetDebug(uaci_params,True).call(True)

    # BATCH
    cmdsList = list()
    cmdsList.append(SetDebug(uaci_params,False))
    cmdsList.append(GetVersion(uaci_params))
    # cmdsList.append(GetProfile(uaci_params))
    bc = BatchCmds(uaci_params, cmdsList)
    ok = ok and bc.call(True)

    #  END SESSION
    ok = ok and EndSession(uaci_params).call(True)


# ================================================================
#              TESTING
# ================================================================

class TestNameValuePairImpl(unittest.TestCase):

    def banner(self,text):
        s = ""
        s = "="*50+"\n"+" "*8+text+"\n"+"="*50
        return s


    @classmethod
    def setUpClass(cls):
        g.init(unitTestRun = True)

    def setUp(self):
        # g.init(unitTestRun = True)
        pass

    def test_Attributes(self):
        '''
        print(self.banner("Attributes"))
        o = Attributes(('ds_segment',"string","enrico_ds_segment"))
        print(o.get_json())
        o.add_tuple(('ds_cmp_1', 'numeric',0.0))
        print(o.get_json())
        o = Attributes(None)
        print(o.get_json())
        '''
        return True

    def test_PostEvent(self):
        '''
        s = self.banner("PostEvent")
        print(s)
        pe = PostEvent(g.session_id,g.audienceID_field_name, g.audienceIDs[0],
                       g.events[0])
        print(pe.get_json())
        attrs = Attributes(('ds_segment',"string","enrico_ds_segment"))
        attrs.add_tuple(('ds_cmp_1', 'numeric',0.0))
        pe.sett_attrs(attrs)
        print(pe.get_json())
        '''
        return True

    def test_Attributeslistcopy(self):

        num_attribute1 = "num_attribute1"
        attr = Attributes(None)

        # attr.add_tuple(("AudienceID", "string", "AudienceID" ))
        # attr.add_tuple(("LRDX_INDX", "numeric", "numeric_default" ))
        attr.add_tuple((num_attribute1 , "numeric", 999))
        attr.add_tuple(("string_attribute1", "string", "val_string_attribute1"))
        attr.add_tuple(("date_attribute1", "numeric", "2018-02-01"))

        # check deep copy works, only copy is changed
        attr2 = attr.deepcopy("changed")
        attr2.set_attribute(num_attribute1, 111)
        g.log.info(attr.left_compare(attr2))
        nr_different = len(attr.left_compare(attr2))
        self.assertEqual(nr_different, 1)
        attr2 = attr.deepcopy() # back to equal

        # add attribute to attr2, not to attr1
        attr2.add_tuple(("num_attribute_extra",555,"numeric"))
        nr_different = len(attr.left_compare(attr2))
        self.assertEqual(nr_different, 0)
        nr_different = len(attr.full_compare(attr2))
        self.assertEqual(nr_different, 1)

        return True

if __name__ == '__main__':
    # unittest.main()

    #import argparse
    #args = argparse.parse_args()
    g.init()
    API_unit_test(g.uaci_params, g.interaction_points[0])



