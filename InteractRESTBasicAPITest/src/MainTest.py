#!/usr/bin/env python

import globals as g
import EVNetUtils as nu
import testSession as jt


def main():
    """
    The main entry point of the application
    """

    g.init()
    nu.setFiddler(True, g.fiddlerProxy,g.uaci_params.get_url())

    success = True

    # jdb.dbGetAudIDRow('enricop 0302 183439 726',500, True)
    # jdb.dbGetAudIDRows("enrico%",500, True)

    #InteractAPIUtils.API_unit_test( g.uaci_params,g.interaction_points[1])
    #v.startSession_fails_missing_audience_id_are_attributes_set()
    # v.startSession_fails_do_offers_work()
    #v.startSession_trigger_stored_procedure()
    #
    nr_test_cookies= 10
    nr_repetitions =  2
    # success = success and jt.session_web01_test(nr_test_cookies, nr_repetitions, verbose = False, dumpCalls= False)
    success = success and jt.session_web01_test(nr_test_cookies, nr_repetitions, verbose = True, dumpCalls= True)
    #jt.stress_test_developing()
    # jt.testPersistSessionData()
    # jt.testEvents()
    if not success:
        g.log.error("\n\n##### Test FAILED #####")
    else:
        g.log.info("test succeeded")

if __name__ == "__main__":
    main()
