package interact_callout_JLR_V02_test;

import com.unicacorp.interact.flowchart.macrolang.storedobjs.CalloutException;
import com.unicacorp.interact.session.AudienceId;
import org.apache.log4j.Logger;

import java.io.File;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.*;

import interact_callout_JLR_v02.*;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;


public class Interact_callout_JLR_V02_test {

    public static void main(String[] args) {

        Interact_callout_JLR_V02_test test = new Interact_callout_JLR_V02_test();
        // test.testRobustness();
        // test.testStoredProcedure();
        test.testNormalFunctionality();
    }

    
    public  Map<String, String> configDataMap() {
        /** to easily test without ddeploying
         * fill map for start-up shut-down config
         * @return configuration map
         */
        Map<String, String> config = new HashMap<String, String>();
        Properties prop = new Properties();
        InputStream input = null;
        //String propFilePath = "..\\..\\..\\dev_data\\jlr\\java_callout.properties";
        String propFileDir = "../../../dev_data/jlr";
        String propFilePath = propFileDir+"/java_callout.properties";

        try {
            input = new FileInputStream(propFilePath);
            // load a properties file
            prop.load(input);

            config.put("jdbc_driver_path", prop.getProperty("jdbc_driver_path"));
            //config.put("jdbc_driver_path", null);
            config.put("db_user",prop.getProperty("db_user"));
            // config.put("db_user", null);
            config.put("jdbc_url",prop.getProperty("db_url"));
            //config.put("jdbc_url",null);
            config.put("db_password", prop.getProperty("db_pwd"));
            // config.put("db_password", null);
            config.put("debug_mode","y");
            // config.put("debug_mode", null);

            // copied from python config, not used in Java, at least now
            //prop.getProperty("db_server"));
            // prop.getProperty("db_name"));

        } catch (IOException ex) {
            ex.printStackTrace();
        } finally {
            if (input != null) {
                try {
                    input.close();
                } catch(Exception e) {
                    log.error(e);
                }
            }
        }
        return config;
    }


    /**
     * To test resilience to missing config
     * will turn out to be less useful as this as less importance
     * @return
     */
    public static Map<String, String> corruptConfigDataMap() {

        Map<String, String> map = new HashMap<String, String>();

        map.put("config_1_key",null);
        map.put("config_2_key",null);
        map.put("config_3_key",null);
        map.put("config_4_key",null);
        map.put("config_5_key",null);

        return map;
    }


    /**
     * useful only in initial stages
     */
     void testStoredProcedure() {

        AudienceId audienceId = new AudienceId("TestAudienceID");
        Map<String, String> map = new HashMap<String, String>();
        Map<String, String> config = configDataMap();

        CreateAndSegmentNewCookie_v02 co = new CreateAndSegmentNewCookie_v02();
        co.callStoredProcedure("44021460493888055239189", "DS_O", "unica01.ev01@gmail.com");
    }


    void testRobustness() {

        AudienceId audienceId = new AudienceId("TestAudienceID");
        Map<String, String> map = new HashMap<String, String>();
        Map<String, String> config = configDataMap();

        CreateAndSegmentNewCookie_v02 co = new CreateAndSegmentNewCookie_v02();

        try {
            // -- INIT
            // wrong, test resilience
            co.initialize(null); // just to make it a bit robust
            log.info("getValue() after wrong initialization returns: " +
                    co.getValue(audienceId,config,"param1","param2", null).get(0));
            co.setStatus_ok(true);

            // wrong, test resilience
            co.initialize(corruptConfigDataMap());
            log.info("getValue() after wrong initialization returns: " +
                    co.getValue(audienceId,config,"param1","param2", null).get(0));
            co.setStatus_ok(true);
            // correct
            co.initialize(config);

            // -- NR ARGUMENTS
            log.info("Call Out Takes nr arguments: "+ co.getNumberOfArguments());

            // --- GET VALUE
            // test with null params
            //  printing to verify we get an error string rather than a null
            log.info("getValue() with wrong params returns: " +
                    co.getValue(null, null,null, null, null).get(0));
            co.setStatus_ok(true);

            log.info("getValue() with wrong params returns: " + co.getValue(audienceId, config,null, null, null).get(0));
            co.setStatus_ok(true);

            log.info("getValue() with wrong params returns: " + co.getValue(audienceId,config,"param1",null, null).get(0));
            co.setStatus_ok(true);

            log.info("getValue() with wrong params returns: " + co.getValue(audienceId,config,"param1","param2", null).get(0));
            co.setStatus_ok(true);

            // correct call
            List<String> ret = co.getValue(audienceId, null
                    , "dbo_tblonlineprofile.CookieID" , "dbo_tblonlineprofile.DS_SEGMENT");
            log.info("\n ----- Call Out returned value(s) ------");
            for (String s : ret) {
                log.info("value = "+s);
            }
        } catch (CalloutException e) {
            log.error(e);
        }
    }

    static String sqlQueryForCookie(String cookie) {
        return "    SELECT * " +
                "  FROM [JLR_Jigsaw].[dbo].[tblOnlineProfile] " +
                "  where CookieID = '"+cookie+"'";
    }

    void testNormalFunctionality() {

        AudienceId audienceId = new AudienceId("TestAudienceID");
        Map<String, String> config = configDataMap();
        CreateAndSegmentNewCookie_v02 co = new CreateAndSegmentNewCookie_v02();

        // todo move better place
        String[] attributes = {
                "DS_O",
                "DS_VRS_1",
                "DS_VRS_2",
                "DS_PRM_1",
                "DS_PRM_2",
                "DS_CPB_1",
                "DS_CPB_2",
                "DS_CMP_1",
                "DS_CMP_2",
                "DS_REG_1",
                "LRDX_INDX",

                // below here INTENTIONALLY BAD and repeated
                "AM_BAD_OK", // See what happens
                "DS_CPB_2",  // Repeated, delete it
        };

        try {
            co.initialize(config);

            String cookieID = generateCookieID();
            //String cookieID = "testnospaces";
            log.info("start test cookie: "+cookieID);

            // test attributes
            for (int startIdx = 0; startIdx < attributes.length; startIdx++) {

                int i = startIdx;
                log.info("--- test all attrs starting from: "+i+" "+attributes[i]);
                for (int countAttrs = 0; countAttrs < attributes.length; countAttrs++) {
                    log.info("sending attr["+ i+"], "+attributes[i]);

                    // --- call getValue
                    for (int repeat = 0; repeat < 1; repeat++) {
                        List<String> ret = co.getValue(audienceId, config, cookieID, attributes[i],"unica.ev01@gmail.com");
                        for (int v = 0; v < ret.size(); v++) {
                            log.info("getValue()[" + v + "] =" + ret.get(v));
                        }
                    }
                    i++;
                    i = (i >= attributes.length) ? 0 : i;
                }
            }
            log.info("end test cookie: '"+cookieID+"'  sql query text:\n"
                    +sqlQueryForCookie(cookieID));
            // shutDown
            co.shutdown(config);

        } catch (Exception e) {
            log.error(e);
        }
    }

    static String generateCookieID() {
        String pattern = "MMdd HH:mm:ss";
        DateFormat df = new SimpleDateFormat(pattern);
        Date d = new java.util.Date();
        String s = "enricoj "+df.format(d);
        if (s.length() > 30-4)
            if (s.length() > 30) {
                log.error("cookie ID too long");
                System.exit(1);
            }
            else
                log.warn("long cookieID, cannot append much, length: "+ s.length());
        return s;
    }


    // --- DATA ---
    Map<String, String> configData = null;

    final static Logger log = Logger.getLogger(Interact_callout_JLR_V02_test.class);
}


