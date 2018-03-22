#!/usr/bin/env python

''' Scratchpad of little functions to test interact reactions

Not verified properly but
probably none of the code in here is  part of the final delivery code
and this file could be delited,
kept just 'in case'
'''


import globals as g
import InteractAPIUtils as IA


def startSession_trigger_stored_procedure():
    try:
        ok = True

        pars = g.uaci_params.deepcopy()
        pars.set_audience_ID(IA.tstampAudienceID())
        # pars.set_channel("EV_Testing")

        attrs = g.prof01.deepcopy()

        g.log.error("(for this test we only need to set an attribute)")
        attrs.set_attribute("ds_segment","enrico_segment",strict = True)
        ss = IA.StartSession(pars, attrs, "false")
        sent_attributes = ss.get_send_attributes("Profile sent by startsession")
        ss.call(True)
        # ss.dump()

        g.log.info("\ncall getProfile")
        profile = IA.GetProfile(pars)
        ret = profile.call(True)
        returned_attrs = profile.create_Attributes()
        diffs = sent_attributes.left_compare(returned_attrs)
        g.log.info("\n")
        sent_attributes.compare_values(returned_attrs, diffs)
        g.log.info("\n")
        sent_attributes.left_print_side_2_side(returned_attrs)

    finally:
        IA.EndSession(g.uaci_params)


def startSession_fails_missing_audience_id_are_attributes_set():
    try:
        ok = True

        g.log.info(verification_header.format("startSession profile attributes  test; steps:"))
        g.log.info("1 call startSession with non-existing audience ID, setting several attributes (not all), it will fail")
        g.log.info("2 call getProfile")
        g.log.info("3 check if attributes from getProfile have values set in previous failed startSession")

        pars = g.uaci_params.deepcopy()
        pars.set_audience_ID(IA.tstampAudienceID())

        # g.log.info("call start Session with non-existing cookie")
        ss = IA.StartSession(pars, g.prof01, "false")
        sent_attributes = ss.get_send_attributes("Profile sent by startsession")
        # sent_attributes.dump()
        ss.call(True)
        # ss.dump()

        g.log.info("call getProfile for non-existing cookie")
        profile = IA.GetProfile(pars)
        ret = profile.call(True)
        returned_attrs = profile.create_Attributes()
        diffs = sent_attributes.left_compare(returned_attrs)
        sent_attributes.compare_values(returned_attrs, diffs)
        sent_attributes.left_print_side_2_side(returned_attrs)

        g.log.info("\n\nProfile Dump -------------------")
        profile.dump()

    finally:
        IA.EndSession(g.uaci_params)


def startSession_fails_do_offers_work():
    try:
        ok = True

        pars = g.uaci_params.deepcopy()
        pars.set_channel("EV_Testing")

        attrs = g.prof01.deepcopy()
        pars.set_audience_ID(IA.tstampAudienceID())
        g.log.info(g.verification_header.format("startSession profile attributes  test; steps:"))
        # g.log.info("1 call startSession with non-existing audience ID, setting several attributes (not all), it will fail")
        ss = IA.StartSession(pars, attrs, "false")
        ok = ss.call(True)
        if ok:
            g.log.error("###### ERROR: startSession, expected to fall, succeeded")
            # return False

        # --- 2nd call, after 1st failed, startSession setting things up for new cookie
        g.log.info("OK, startSession, expected to fail, failed, it means we have new cookie")
        g.log.info("\n2nd startSession call, after 1st failed as expected, setting things up for new cookie")
        g.log.error("(for this test we only need to set an attribute)")
        attrs.set_attribute("ds_segment","enrico_segment",strict = True)
        ss = IA.StartSession(pars, attrs, "false")
        sent_attributes = ss.get_send_attributes("Profile sent by startsession")
        ss.call(True)
        # ss.dump()

        g.log.info("\ncall getProfile, not strictly necessary, just to verify attributes of startSession have been set correctly")
        profile = IA.GetProfile(pars)
        ret = profile.call(True)
        returned_attrs = profile.create_Attributes()
        diffs = sent_attributes.left_compare(returned_attrs)
        g.log.info("\n")
        sent_attributes.compare_values(returned_attrs, diffs)
        # sent_attributes.left_print_side_2_side(returned_attrs)

        g.log.info("call getOffers")
        getOffers = IA.GetOffers(pars, "ip01")
        ok = getOffers.call(False)
        g.log.info("\nDump getOffers response")
        getOffers.dump(True)
        pass

    finally:
        IA.EndSession(g.uaci_params)


if __name__ == '__main__':
    g.init(unitTestRun=True)
    startSession_trigger_stored_procedure()
    startSession_fails_missing_audience_id_are_attributes_set()
    startSession_fails_do_offers_work()