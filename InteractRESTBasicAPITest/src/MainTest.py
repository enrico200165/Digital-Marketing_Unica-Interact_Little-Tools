#!/usr/bin/env python

import globals as g
import testSession as jt
import EVNetUtils as nu


def main():
    """
    The main entry point of the application
    """

    g.init()
    #
    nu.setFiddler(True, g.fiddlerProxy,g.uaci_params.get_url())

    success = True

    # jdb.dbGetAudIDRow('enricop 0302 183439 726',500, True)
    # jdb.dbGetAudIDRows("enrico%",500, True)

    # API Test, normally should not be necessary
    if False:
        jt.API_unit_test(g.uaci_params,  g.interaction_points[0])

    nr_test_cookies = 1
    nr_repetitions = 1

    inIntranet = not ("nfinit" in g.uaci_params.get_url())
    checkOnDB = not inIntranet
    # success = success and jt.session_web01_test(nr_test_cookies, nr_repetitions, verbose = False, dumpCalls= False)
    success = success and jt.session_web01_test(nr_test_cookies, nr_repetitions, True, True,checkOnDB)
    #jt.stress_test_developing()
    # jt.testPersistSessionData()
    # jt.testEvents()
    if not success:
        g.log.error("\n\n##### Test FAILED #####")
    else:
        g.log.info("test succeeded")

if __name__ == "__main__":
    main()
