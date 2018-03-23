#!/usr/bin/env python

import datetime
import time
import interactCommands as IA
import globals as g
import EVNetUtils as ut
import db_little_functs as jdb


def pageActionLog(action, logit = True):
    '''
    Just print page action being executed
    used by tests
    :param action:
    :param logit:
    :return:
    '''
    n = 20
    leftPadding = " "*(25-n)

    s = "\n"+leftPadding+"#"*50+"\n"
    s += leftPadding+"#"*n+" {} ".format(action)+"#"*n
    s += "\n"+leftPadding+"#"*50
    if logit:
        g.log.info(s)
    return s


def apiActionLog(action, logit = True):
    '''
    Just print API action being executed
    used by tests
    :param action:
    :param logit:
    :return:
    '''
    n = 10
    s = "\n" +" "*(25-n)+"-"*n+" {} ".format(action)+"-"*n
    if logit:
        g.log.info(s)
    return s


def timeStamp():
    s = datetime.datetime.utcnow().strftime('%m%d %H:%M:%S.%f')[:-3]
    return s


def tstampAudienceID():
    return "RegI p "+timeStamp()


def genAudienceIDs(n):
    ids = []
    for i in range(1,n+1):
        nr =  '{nr:03d}'.format(nr=i)
        id = tstampAudienceID()+"-"+nr
        ids.append(id)
    return ids


def session_web01_test(nr_test_cookies, nr_repetitions = 1, verbose = False, dumpCalls = False):
    '''
    Trying to mirror the specs
    :return:
    '''

    try:
        ok = True
        pars = g.uaci_params.deepcopy()
        new_vistor_attrs = g.new_vistor_profile_attrs.deepcopy()

        cookies = genAudienceIDs(nr_test_cookies)

        for iterCount, cookie in enumerate(cookies):
            # cookie_known = None
            pars.set_audience_ID(cookie)
            ut.logBanner("TEST for AudienceID: <{}>".format(cookie))

            for rep in range(1,1+nr_repetitions):
                g.log.info("cookie <{}> repetition {}".format(cookie,rep))

                for event_nr, event in enumerate(g.events):

                    pageActionLog("PageLoad")

                    ### START SESSION
                    apiActionLog("START SESSION")
                    ss = IA.StartSession(pars, None, "false")
                    ok2 = ss.call(verbose)
                    if not ok2:
                        cookie_known = False
                        g.log.info("\n<{}> is new visitor, setting profile with second startSession".format(cookie))
                        ss.set_attributes(new_vistor_attrs,True)
                        apiActionLog("START SESSION (SECOND, to set new visitor profile, this also will give error but it's ok)")
                        ok2 = ss.call(verbose, dumpAttributes=False)
                    else:
                        g.log.info("### <"+cookie + "> is NOT new ###")
                        cookie_known = True

                    ### GET PROFILE
                    apiActionLog("GET PROFILE ### Only useful/needed if cookie is known/exists ###")
                    profile = IA.GetProfile(pars)
                    ok = ok and profile.call(verbose)
                    attrs_before_evt = profile.create_Attributes("before event")

                    ### POST EVENTs
                    # keep event and corresp attribute name in a tuple
                    event_name, attribute_name = event
                    attribute_name = attribute_name.lower()
                    attr_value_before = attrs_before_evt.get_attribute_value(attribute_name)
                    po = IA.PostEvent(pars,event_name)
                    if (event_name == "ds_registeryourinterest"):
                        email = "test_{}@example.com".format(cookie)
                        attrs = IA.Attributes("Post Event Attributes")
                        attrs.add_tuple(('Command_Payload',"string",email))
                        po.sett_attrs(attrs)

                    #g.log.info("before post event:  {}={}".format(attribute_name, attr_value_before))
                    apiActionLog("POST EVENT  event: [{}]  (on db should correspond to [{}])".format(event_name, attribute_name))
                    ok = ok and po.call(verbose, dumpAttributes = dumpCalls)

                    ### GET PROFILE - INTERNAL, DISABLE
                    # apiActionLog("GET PROFILE, ### INTERNAL ###, just to demonstrate Interact does not realize DB update")
                    # ret = profile.call(verbose)
                    # attrs_after_evt  = profile.create_Attributes("after event")
                    # attr_value_after = attrs_after_evt.get_attribute_value(attribute_name)
                    # g.log.info("after post event [{}]:  <{}> = {}".format(event_name,attribute_name, attr_value_after))
                    # # check on DB
                    # row = jdb.dbGetProfileCol(cookie,attribute_name)
                    # if row is not None:
                    #     g.log.info("<{}> value on DB =  {}".format(attribute_name,row[attribute_name]))
                    # else:
                    #     g.log.error(cookie+" not found in db")


                    apiActionLog("to make interact aware of attribute update on DB we have to perform now:"+
                                 "\nendSession + startSession + getProfile"
                                 "\nwith current interact version endSession and getProfile unneeded, just startSession is enough+"
                                 "\nbut let's do things properly with all the 3, may send them singularly or together in one batch")
                    batchThem = ((iterCount+rep+event_nr) % 2) == 1
                    if batchThem:
                        g.log.info("This time will send them in BATCH")
                        endSession = IA.EndSession(pars)
                        ss.set_attributes(None, overwrite=True)
                        batchCommands = IA.BatchCmds(pars)
                        batchCommands.append(endSession).append(ss).append(profile)
                        ok = ok and batchCommands.call(verbose,True,dumpCalls)
                        g.log.info(batchCommands.get_rsp_json())
                    else:
                        g.log.info("This time will send them one by one")
                        apiActionLog("END SESSION --- to restart and read values on DB")
                        es = IA.EndSession(pars)
                        ok = ok and es.call(verbose)
                        apiActionLog("START SESSION  --- restart to read attributes from DB")
                        ss.set_attributes(None, overwrite=True)
                        ok = ok and  ss.call(verbose)
                        apiActionLog("GET PROFILE --- check if interact session now got from DB attributes set from previous post event")
                        ok = ok and profile.call(verbose)

                    attrs_after_evt  = profile.create_Attributes("after event")
                    attr_value_after_batch = attrs_after_evt.get_attribute_value(attribute_name)
                    g.log.info("\nafter post event and Batch:  {} = {}".format(attribute_name, attr_value_after_batch))
                    # check on DB
                    row = jdb.dbGetProfileCol(cookie, attribute_name)
                    if row is not None:
                        # compare attribute values
                        if (attribute_name in row):
                            g.log.info("query on DB:       {} = {}".format(attribute_name,str(row[attribute_name])))
                            dbAttrNum = row[attribute_name] #int(row[attribute_name])
                            profAttrNum = attr_value_after_batch
                            if (dbAttrNum != profAttrNum):
                                g.log.info("test failed, attr values not equal: profile ={}  DB ={}"
                                           .format(profAttrNum,dbAttrNum))
                                return False
                            else:
                                pass
                        else:
                            g.log.error("test failed, did not find in table attr: {}"
                                        .format(attribute_name))
                    else:
                        g.log.error("failed query: cannot find on db attribute: {}".format(attribute_name))


                    pageActionLog("PageExit")
                    g.log.info(""); g.log.info("")
                    apiActionLog("HERE, BEFORE ENDSESSION  WE WOULD NEED TO COMMANDED, BY WEB CODE, VIA AN EVENT, TO SAVE PROFILE TO DB")
                   ### END SESSION
                    apiActionLog("END SESSION")
                    es = IA.EndSession(pars)
                    if es.call(verbose): # workaround failure of endSession if we sent batch previously
                        if batchThem:
                            g.log.error("endSession did NOT fail after a batch, usually it fails")
                    else:
                        if batchThem:
                            g.log.warn("endSession failed, always does if we previous sent batch")
                            pass # for unknown reasons fails if we sent batch previously
                            # so consider this ok and continue to test
                        else:
                            # no Batch, so real failure
                            ok = False
                    if not ok:
                        g.log.error("failed endSession, cookie: {} sessionId: {}".format(cookie,pars.get_session_id()))
                    g.log.info("SESSION ENDED for cookie <{}>\n\n".format(cookie))
                g.log.info(" ----- cookie '{}' TEST ENDED ------\n".format(cookie))
                g.log.info(jdb.dbGetAudIDRow(cookie, 0, verbose = False))
                g.log.info("SQL for query: \n" + jdb.generateSQLForAudID(cookie))

    # except Exception as exc:
    #    g.log.error("Generic Error")
    finally:
        # IA.EndSession(pars).call()
        pass
    return ok


def testPersistSessionData():
    '''
    Test sending an event that causes storage of session data to DB
    by setting appropriately an attribute value e sending an even that will
    trigger resegmentation (and a flowchart will test for attribute value and
    call the snapshot
    :return:
    '''

    pars = g.uaci_params.deepcopy()

    try:
        cookie = genAudienceIDs(1)[0]
        pars.set_audience_ID(cookie)
        attrs = g.new_vistor_profile_attrs.deepcopy()

        ### START SESSION
        apiActionLog("START SESSION")
        ss = IA.StartSession(pars, None, "false")
        ok = ss.call(False)
        if not ok:
            g.log.info("<{}> is new visitor, setting profile with second startSession".format(cookie))
            ss.set_attributes(attrs ,True)
            apiActionLog("START SESSION (SECOND, to set new visitor profile)")
            ok = ss.call(verbose=False, dumpAttributes=False)
        else:
            g.log.info("### "+cookie + " is NOT new ###")

        ### POST EVENTs
        # Event
        po = IA.PostEvent(pars,evt = "Command_Via_Param_DoSeg")
        # Attribute that specifies command
        persistSessionAttr = IA.Attributes("Identifies command to execute")
        persistSessionAttr.set_attribute("Command_Name","CreateCookie", strict = False)
        po.sett_attrs(persistSessionAttr)

        ok = po.call(verbose = True, dumpAttributes = True)
        # EV here should check attribute with last update timestamp ?
        row = jdb.dbGetProfileCol(cookie, "DateModified")
        g.log.info("profile updated at: {}\n".format(row)
                 + "current time:       {}".format(datetime.datetime.now()))
        pass
    except Exception as e:
        g.log.error(e)
    finally:
        IA.EndSession(pars).call()


def testEvents(cookiePar = None):
    '''
    Trying to mirror the specs
    :return:
    '''
    global nr_test_cookies

    cookie = genAudienceIDs(1)[0] if (cookiePar is None) else cookiePar
    verbose = False
    pars = g.uaci_params.deepcopy()
    new_vistor_attrs = g.new_vistor_profile_attrs.deepcopy()
    pars.set_audience_ID(cookie)

    try:
        ok = True
        ut.logBanner("TEST attributes for AudienceID: <{}>".format(cookie))
        for rep in range(1,3):
            g.log.info("cookie <{}> repetition {}".format(cookie,rep))
            for event in g.events:
                # pageActionLog("PageLoad")
                ### START SESSION
                # apiActionLog("START SESSION")
                ss = IA.StartSession(pars, None, "false")
                ok = ss.call(verbose)
                if not ok:
                    g.log.info("<{}> is new visitor, setting profile with second startSession".format(cookie))
                    ss.set_attributes(new_vistor_attrs,True)
                    # apiActionLog("START SESSION (SECOND, to set new visitor profile)")
                    ok = ss.call(verbose=True, dumpAttributes=True)
                else:
                    g.log.info("### "+cookie + " is NOT new ###")
                    pass

                ### GET PROFILE
                apiActionLog("GET PROFILE (NOT in specs, for internal use)")
                profile = IA.GetProfile(pars)
                ret = profile.call(verbose = False)
                attrs_before_evt = profile.create_Attributes("before event")

                ### POST EVENTs
                # keep event and corresp attribute name in a tuple
                event_name, attribute_name = event
                attribute_name = attribute_name.lower()
                attr_value_before = attrs_before_evt.get_attribute_value(attribute_name)

                #g.log.info("before post event:  {}={}".format(attribute_name, attr_value_before))
                apiActionLog("POST EVENT  event: [{}]  (on db should correspond to [{}])".format(event_name, attribute_name))
                po = IA.PostEvent(pars,event_name)
                # add a couple of attrributes
                # attrs = IA.Attributes(('ds_segment',"string",event))
                # attrs.add_tuple(('ds_cmp_1', 'numeric',0.0))
                # po.sett_attrs(attrs)
                ok = po.call(verbose = False, dumpAttributes = False)

                #time.sleep(1)
                ### GET PROFILE
                # apiActionLog("GET PROFILE")
                ret = profile.call(verbose)
                attrs_after_evt  = profile.create_Attributes("after event")
                attr_value_after = attrs_after_evt.get_attribute_value(attribute_name)
                # g.log.info("after post event {}:  {} = {}".format(event_name,attribute_name, attr_value_after))
                # check on DB
                row = jdb.dbGetProfileCol(cookie, attribute_name)
                if row is not None:
                    #g.log.info("query on DB:       {} = {}".format(attribute_name,row[attribute_name]))
                    pass
                else:
                    g.log.error(cookie+"not found in db")
                #diffs = attrs_after_evt.full_compare(attrs_before_evt)
                #attrs_after_evt.compare_values(attrs_before_evt, diffs)
                # attrs_before_evt.left_print_side_2_side(attrs_after_evt)
                #g.log.info("after post event {} = ".format(attrs_after_evt.get_attribute_value(event(2))))
                # apiActionLog("END SESSION --- to restart and read values on DB")
                ok = IA.EndSession(pars)
                ss.set_attributes(None, overwrite=True)
                # apiActionLog("START SESSION  --- restart to read attributes from DB")
                ok = ss.call(verbose)
                # apiActionLog("GET PROFILE --- check if we got from DB attributes from post event")
                ret = profile.call(verbose)
                attrs_after_evt  = profile.create_Attributes("after event")
                attr_value_after = attrs_after_evt.get_attribute_value(attribute_name)
                g.log.info("after post event (endSession, startSession, getProfile):  {} = {}".format(attribute_name, attr_value_after))
                # check on DB
                row = jdb.dbGetProfileCol(cookie, attribute_name)
                if row is not None:
                    g.log.info("query on DB:       {} = {}".format(attribute_name,row[attribute_name]))
                else:
                    g.log.error(cookie+"not found in db")

                # pageActionLog("PageExit")
                ### END SESSION
                # apiActionLog("END SESSION")
                ok = IA.EndSession(pars)
                if not ok:
                    g.log.error("failed endSession, cookie: {} sessionId: {}".format(cookie,pars.get_session_id()))
                    g.log.info("SESSION ENDED for cookie <{}>\n\n".format(cookie))
                    g.log.info("cookie '{}' Test ended\n".format(cookie))
    except Exception as exc:
        g.log.error("Generic Error")
        g.log.error("Generic Error")
    finally:
        IA.EndSession(pars).call()
    return True

def stress_test_developing():
    '''
    Trying to mirror the specs
    :return:
    '''
    nr_stress_cookies = 1000
    pars = g.uaci_params.deepcopy()
    new_vistor_attrs = g.new_vistor_profile_attrs.deepcopy()
    cookies = genAudienceIDs(nr_stress_cookies)
    start_time = time.time()
    verbose = False
    try:
        ok = True

        for cookie in cookies:
            pars.set_audience_ID(cookie)
            #ut.logBanner("TEST for AudienceID: <{}>".format(cookie))

            for rep in range(1,2):
                # g.log.info("cookie <{}> repetition {}".format(cookie,rep))
                for event in g.events:

                    # pageActionLog("PageLoad")

                    ### START SESSION
                    #apiActionLog("START SESSION")
                    ss = IA.StartSession(pars, None, "false")
                    ok = ss.call(verbose)
                    if not ok:
                        #g.log.info("<{}> is new visitor, setting profile with second startSession".format(cookie))
                        ss.set_attributes(new_vistor_attrs,True)
                        #apiActionLog("START SESSION (SECOND, to set new visitor profile, this also will give error but it's ok)")
                        ok = ss.call(verbose=False, dumpAttributes=False)
                    else:
                        #g.log.info("### "+cookie + " is NOT new ###")
                        pass
                    ### GET PROFILE
                    # apiActionLog("GET PROFILE (NOT in specs, for internal use)")
                    profile = IA.GetProfile(pars)
                    ret = profile.call(verbose)
                    attrs_before_evt = profile.create_Attributes("before event")

                    ### POST EVENTs
                    # keep event and corresp attribute name in a tuple
                    event_name, attribute_name = event
                    attribute_name = attribute_name.lower()
                    attr_value_before = attrs_before_evt.get_attribute_value(attribute_name)

                    #g.log.info("before post event:  {}={}".format(attribute_name, attr_value_before))
                    #apiActionLog("POST EVENT  event: [{}]  (on db should correspond to [{}])".format(event_name, attribute_name))
                    po = IA.PostEvent(pars,event_name)
                    # add a couple of attrributes
                    # attrs = IA.Attributes(('ds_segment',"string",event))
                    # attrs.add_tuple(('ds_cmp_1', 'numeric',0.0))
                    # po.sett_attrs(attrs)
                    ok = po.call(verbose = False, dumpAttributes = False)

                    #time.sleep(1)
                    ### GET PROFILE
                    #apiActionLog("GET PROFILE, ### INTERNAL ###, just to demonstrate Interact does not realize DB update")
                    ret = profile.call(verbose)
                    attrs_after_evt  = profile.create_Attributes("after event")
                    attr_value_after = attrs_after_evt.get_attribute_value(attribute_name)
                    # g.log.info("after post event {}:  {} = {}".format(event_name,attribute_name, attr_value_after))
                    # check on DB
                    row = jdb.dbGetProfileCol(cookie, attribute_name)
                    if row is not None:
                        #g.log.info("query on DB:       {} = {}".format(attribute_name,row[attribute_name]))
                        pass
                    else:
                        #g.log.error(cookie+"not found in db")
                        pass
                    #diffs = attrs_after_evt.full_compare(attrs_before_evt)
                    #attrs_after_evt.compare_values(attrs_before_evt, diffs)
                    # attrs_before_evt.left_print_side_2_side(attrs_after_evt)
                    #g.log.info("after post event {} = ".format(attrs_after_evt.get_attribute_value(event(2))))


                    #apiActionLog("to make interact aware of attribute update on DB we have to perform now"+
                    #             "\nendSession + startSession + getProfile"
                    #             + "\n(here sent individually, batch command should improve performance, not tested)"+
                    #             "\nprobably endSession and getProfile unneeded, just startSession may suffice, but be safe")

                    #apiActionLog("END SESSION --- to restart and read values on DB")
                    es = IA.EndSession(pars)
                    es.call()

                    #apiActionLog("START SESSION  --- restart to read attributes from DB")
                    ss.set_attributes(None, overwrite=True)
                    ok = ss.call(verbose)
                    #apiActionLog("GET PROFILE --- check if interact now got from DB attributes from post event")
                    ret = profile.call(verbose)
                    attrs_after_evt  = profile.create_Attributes("after event")
                    attr_value_after = attrs_after_evt.get_attribute_value(attribute_name)
                    #g.log.info("after post event:  {} = {}".format(attribute_name, attr_value_after))
                    # check on DB
                    row = jdb.dbGetProfileCol(cookie, attribute_name)
                    if row is not None:
                        #g.log.info("query on DB:       {} = {}".format(attribute_name,row[attribute_name]))
                        pass
                    else:
                        pass
                        #g.log.error(cookie+"not found in db")


                    # pageActionLog("PageExit")
                    # g.log.info("")
                    #g.log.info("")
                    #pageActionLog("HERE, BEFORE ENDSESSION  WE WOULD NEED TO COMMANDED, BY WEB CODE, VIA AN EVENT, TO SAVE PROFILE TO DB")
                    ### END SESSION
                    #apiActionLog("END SESSION")
                    ok = IA.EndSession(pars)
                    if not ok:
                        pass
                        g.log.error("failed endSession, cookie: {} sessionId: {}".format(cookie,pars.get_session_id()))
                    #g.log.info("SESSION ENDED for cookie <{}>\n\n".format(cookie))
                #g.log.info("cookie '{}' Test ended\n".format(cookie))
                #g.log.info( jdb.dbGetAudIDRow(cookie,0, verbose = False))
                #g.log.info("SQL for query: \n"+generateSQLForAudID(cookie))

        end_time = time.time()
        duration_msecs = (end_time - start_time)*1000
        g.log.info("processed {} cookies in {}".format(nr_stress_cookies,duration_msecs*1000))


    # except Exception as exc:
    #    g.log.error("Generic Error")
    finally:
        IA.EndSession(pars)
    return True

