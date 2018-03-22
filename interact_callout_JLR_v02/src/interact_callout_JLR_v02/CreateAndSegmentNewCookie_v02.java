
package interact_callout_JLR_v02;


import java.sql.*;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Properties;


import com.unicacorp.interact.flowchart.macrolang.storedobjs.CalloutException;
import com.unicacorp.interact.flowchart.macrolang.storedobjs.IAffiniumExternalCallout;
import com.unicacorp.interact.session.AudienceId;

import java.io.File;
import java.nio.file.Files;
import java.nio.file.Paths;

import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Path;
import java.util.*;
import java.util.Map.Entry;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;



class DriverShim implements Driver {
    private Driver driver;
    DriverShim(Driver d) {
        this.driver = d;
    }
    public boolean acceptsURL(String u) throws SQLException {
        return this.driver.acceptsURL(u);
    }
    public Connection connect(String u, Properties p) throws SQLException {
        return this.driver.connect(u, p);
    }
    public int getMajorVersion() {
        return this.driver.getMajorVersion();
    }
    public int getMinorVersion() {
        return this.driver.getMinorVersion();
    }
    public DriverPropertyInfo[] getPropertyInfo(String u, Properties p) throws SQLException {
        return this.driver.getPropertyInfo(u, p);
    }
    public boolean jdbcCompliant() {
        return this.driver.jdbcCompliant();
    }

    @Override
    public java.util.logging.Logger getParentLogger() throws SQLFeatureNotSupportedException {
        return java.util.logging.Logger.getLogger(DriverShim.class.getName());
    }
}



/**
 * This is a sample implementation of the external callout.  
 * The interface IAffiniumExternalCallout may be found in the interact_externalcallout.jar library.
 * 
 * To actually use this implementation, create a reference in the affinum manager configuration for the Runtime server that
 * will execute the callout.  The node is Affinium|Interact|flowchart|External Callouts.
 * within there you must set the name of the class like this:
 * "com.unicacorp.interact.samples.externalcallout.callouttest.SampleExternalCallout".  Please note however, this implementation is just a sample and
 * was not designed to be used in a production environment.
 *
 * 
 * For this example, we will simply return the length of the first argument.   
 * 
 *
 */

public class CreateAndSegmentNewCookie_v02 implements IAffiniumExternalCallout
{

    public CreateAndSegmentNewCookie_v02() {
        this.setStatus_ok(true);
        this.debug_mode = false;
    }


    List<String> errorValue() {
        List<String> errVal = new ArrayList<String>();
        errVal.add(errorReturnValueString);
        return errVal;
    }

    /**
     * Used for debugging jar loading problems
     */
    void printDirs() {
        String s = " --- directories info ---";
        s += "\nworking   dir: " + System.getProperty("user.dir");
        s += "\njava code dir: "+ new File(CreateAndSegmentNewCookie_v02.class.getProtectionDomain().getCodeSource().getLocation().getPath());
        s += "\nclasspath:";
        ClassLoader cl = ClassLoader.getSystemClassLoader();

        URL[] urls = ((URLClassLoader) cl).getURLs();

        for (URL url : urls) {
            String cleanedPath = url.getPath().substring(1).replace("%20"," ");
            Path path = Paths.get(cleanedPath);
            if (!Files.exists(path)) {
                log.error("classpath file or dir does not exist: " + url);
                continue;
            }
            if (Files.isDirectory(path)) {
                s += "\nD: " + url;
                continue;
            }
            if (Files.isReadable(path)) {
                if (!url.getPath().endsWith(".jar")) {
                    log.error("in classpath file that is not .jar: " + url.getPath());
                }
                s += "\nF: " + url;
                continue;
            }
            log.error("should never arrive here");
        }
        log.info(s);
    }


    boolean dynamicLoadJDBCDriver() {
        boolean driverLoaded = false;
        JarFile jarFile = null;
        String driver = "com.microsoft.sqlserver.jdbc.SQLServerDriver";

        log.info("dynamic loading of jdbc driver");
        // posssible thanks to https://stackoverflow.com/questions/14478870/dynamically-load-the-jdbc-driver
        if (this.config_jdbc_driver_path == null
                || this.config_jdbc_driver_path.length() <= 0) {
            return setStatus_ok(false);
        }

        try {
            // write an empty marker file to show where it works >- looks
            Path path = Paths.get(this.config_jdbc_driver_path);
            if (!Files.exists(path) || !Files.isReadable(path)) {
                log.error("not found or unable to open JDBC driver file: " + path +
                        "\ngetName(): " + path.getFileName() + "\nworking dir: " + System.getProperty("user.dir"));
                // create empty file to show working dir
                String timeStamp = new SimpleDateFormat("yyyy-MM-dd_HH-mm-ss").format(new Date());
                File yourFile = new File("delete_me_" + timeStamp);
                yourFile.createNewFile(); // if file already exists will do nothing
                printDirs();
                // throw new CalloutException("jdbc driver not found, see log above for details");
                return setStatus_ok(false);
            }

            jarFile = new JarFile(this.config_jdbc_driver_path);
            Enumeration<JarEntry> e = jarFile.entries();
            URL[] urls = {new URL("jar:file:" + this.config_jdbc_driver_path + "!/")};
            URLClassLoader cl = URLClassLoader.newInstance(urls);
            while (e.hasMoreElements()) {
                JarEntry je = e.nextElement();
                if (je.isDirectory() || !je.getName().endsWith(".class")) {
                    continue;
                }
                // -6 because of .class
                String className = je.getName().substring(0, je.getName().length() - 6);
                className = className.replace('/', '.');
                try {
                    Class c = cl.loadClass(className);
                    log.trace("loaded: " + className);
                    if (className.equals(driver)) {
                        log.info("found and loaded: " + className);
                        Driver d = (Driver) Class.forName(className, true, cl).newInstance();
                        DriverManager.registerDriver(new DriverShim(d));
                        driverLoaded = true;
                    }
                } catch (NoClassDefFoundError ex) {
                    log.warn("NB MIGHT BE IRRELEVANT: not found class: " + className);
                }
            }
        } catch (Exception e) {
            setStatus_ok(false);
            log.error("Exception: ",e);
            printDirs();
            return setStatus_ok(false);
            // throw new CalloutException(e);
        } finally {
            try {
                jarFile.close();
            } catch (Exception e) {
                return setStatus_ok(false);
            }
            return true && getStatus_ok();
        }
    }


    /**
     *  @return
     */
    boolean validateConfig() {
        if (this.config_jdbc_driver_path == null ||this.config_jdbc_driver_path.length() <=0) {
            log.error("unable to set config parameter:this.config_dbpassword");
            setStatus_ok(false);
            // throw new CalloutException("see logs above");
        }
        if (this.config_dbuser == null ||this.config_dbuser.length() <=0) {
            log.error("unable to set config parameter:this.config_dbuser");
            setStatus_ok(false);
            // throw new CalloutException("see logs above");
        }
        if (this.config_dbpassword == null ||this.config_dbpassword.length() <=0) {
            log.error("unable to set config parameter:this.config_dbpassword");
            setStatus_ok(false);
            // throw new CalloutException("see logs above");
        }
        if (this.config_jdbc_url == null ||this.config_jdbc_url.length() <=0) {
            log.error("unable to set config parameter:this.config_dbpassword");
            setStatus_ok(false);
            // throw new CalloutException("see logs above");
        }
        if (this.config_debug_mode == null ||this.config_debug_mode.length() <=0) {
            log.error("unable to set config parameter:this.config_debug_mode");
            setStatus_ok(false);
            // throw new CalloutException("see logs above");
        }
        return getStatus_ok();
    }



    boolean parseConfigMap(  Map<String, String> configurationData) {

        if (configurationData == null) {
            log.error("null Map<String, String> configurationData passed to call out");
            return setStatus_ok(false);
        }

        String s = "";
        for (Entry<String, String> e : configurationData.entrySet()) {
            // checks, check and print all errors, do not stop on first
            if (e.getKey() == null) {
                log.error("null key for configuration param");
                this.setStatus_ok(false);
                continue;
            }
            if (e.getValue() == null) {
                log.error("null value for configuration param: " + e.getKey());
                this.setStatus_ok(false);
                continue;
            }
            // don't risk processing if something went wrong
            if (!getStatus_ok()) {
                return false;
            }

            // after the "defense" above finally get config
            s += "\n" + e.getKey() + "=";
            if (e.getKey().matches(".*p.*w.*d(.*)?")
                    || e.getKey().matches(".*[Dd].*[Bb](.*)?")
                    || e.getKey().matches(".*u.*s.*r(.*)?")) {
                s += "not logging value as it may be user or db related";
            } else {
                s += e.getValue();
            }

            if (false) { // make easier adding elements below
            } else if (e.getKey().equals("jdbc_driver_path")) {
                this.config_jdbc_driver_path = e.getValue();
            } else if (e.getKey().equals("jdbc_url")) {
                this.config_jdbc_url = e.getValue();
            } else if (e.getKey().equals("db_user")) {
                this.config_dbuser = e.getValue();
            } else if (e.getKey().equals("db_password")) {
                this.config_dbpassword = e.getValue();
            } else if (e.getKey().equals("debug_mode")) {
                this.config_debug_mode = e.getValue();
            } else if (config_debug_mode == null || config_debug_mode.toLowerCase().equals("y")) {
                this.debug_mode = false;
            } else {
                log.error("unknown/unmanaged config paramter: " + e.getKey());
            }
        }
        log.info(s + "\nexternalCallout config parameters - end");
        return true;
    }


    /**
     * Initializes the call out.
     * NB. can###NOT### set member data because of the ###peculiarity### of interact call-outs
     * that at every call a NEW object is created.
     * In particular you cannot set here
     * - info to be used in getValue()
     * - status
     * - anything else
     *
     * @param configurationData
     * @throws CalloutException
     */
    public void initialize(Map<String, String> configurationData) throws CalloutException {
        log.info("externalCallout <" + CreateAndSegmentNewCookie_v02.class.getName() + "> initialization");
        if (parseConfigMap(configurationData)) {
            if(validateConfig()) {
                if (dynamicLoadJDBCDriver()) {
                    // everything ok
                    return;
                } else {
                    log.error("failed to load jdbc driver");
                    printDirs();
                }
            } else {
                log.error("failed to validate config map");
            }
        } else {
            log.error("failed to parse config map");
        }
        setStatus_ok(false);
    }

    /**
     * Returns the number of arguments the call out accepts. 
     * @return - the number of arguments
     */
    public int getNumberOfArguments() {
        return 3;
    }

    public boolean callStoredProcedure(String CookieID, String DSEvent, String email)  {
        /**
         * @param DSEvent - ???
         * @param CookieID -
         * @return - ???.
         * @throws nothing now
         */


        // http://www.massapi.com/source/bitbucket/92/88/928859952/sqljdbc_4.0/enu/help/samples/adaptive/executeStoredProcedure.java.html#64
        // https://stackoverflow.com/questions/6113674/how-do-i-execute-a-ms-sql-server-stored-procedure-in-java-jsp-returning-table-d
        // https://docs.oracle.com/cd/E17952_01/connector-j-en/connector-j-usagenotes-statements-callable.html
        java.sql.Connection conn;
        conn = null;
        ResultSet rs = null;

        try {
            if (this.config_jdbc_url == null || this.config_jdbc_url.length() <=0) {
                log.error("jdbc url is null, will use default value");
                this.config_jdbc_url = "jdbc:sqlserver://PRD-JLRINTSQL01:1433;databaseName=JLR_Jigsaw";
            }
            if (this.config_dbuser == null || this.config_dbuser.length() <=0) {
                log.error("dbuser is null, will use default value");
                this.config_dbuser = "sorry_not_in_code";
            }
            if (this.config_dbpassword == null || this.config_dbpassword.length() <=0) {
                log.error("config_dbpassword is null, will use default value");
                this.config_dbpassword = "sorry_not_in_code";
            }

            if (!getStatus_ok()) {
                // not very meaningful as getValue() cannot see invalid state set in initialization
                log.error("status not OK, so avoid calling DB");
                return false;
            }
            conn = DriverManager.getConnection(this.config_jdbc_url, this.config_dbuser, this.config_dbpassword);
            if (conn != null) {
                // code below kept just in case
                if(false && this.debug_mode ) {
                    DatabaseMetaData dm = (DatabaseMetaData) conn.getMetaData();
                    log.debug("Driver name: " + dm.getDriverName());
                    log.debug("Driver version: " + dm.getDriverVersion());
                    log.debug("Product name: " + dm.getDatabaseProductName());
                    log.debug("Product version: " + dm.getDatabaseProductVersion());

                    Statement stmt = conn.createStatement();
                    rs = stmt.executeQuery("SELECT TOP (1) CookieID FROM tblOnlineProfile WHERE CookieID LIKE '4%'");
                    while (rs.next()) {
                        String id = rs.getString("CookieID");
                        log.info("just testing select too cookies, 1 o little more: " + id);
                    }
                }

                CallableStatement cs = conn.prepareCall( "{call dbo.spSetDSSegment(?, ?, ? )}" ) ;
                // CallableStatement cs = conn.prepareCall( "{call dbo.enricoTest(?, ? )}" ) ;

                // -- INPUT PARAMETERS ---
                cs.setString("CookieID", CookieID );
                cs.setString( "DSEvent", DSEvent);
                cs.setString( "EmailAddress", email);
                // --- OUTPUT PARAMETERS ---
                // cstmt.registerOutParameter("intParameter", java.sql.Types.INTEGER);
                // cstmt.registerOutParameter("stringParameter", java.sql.Types.CHAR);

                // Execute the query
                //boolean results = cs.executeQuery();
                boolean results = cs.execute();
                log.info("called stored procedure, status: "+results);
                /* query with results
                rs = cs.executeQuery() ;
                while( rs.next() ) {
                    log.debug(rs.getString("Vorname") + " " + rs.getString("Nachname"));
                    log.debug(rs.getString(1));
                }*/

                // Close the result set, statement and the connection
                conn.commit();

                if (rs != null) rs.close() ;
                cs.close() ;
                conn.close();
           }
        } catch (SQLException ex) {
            log.error("SQL exception, one of possible causes is JDBC driver failed to load");
            log.error(ex);
        } finally {
            try {
                if (conn != null && !conn.isClosed()) {
                    conn.commit();
                    conn.close();
                }
            } catch (SQLException ex) {
                ex.printStackTrace();
            }
        }
        return true;
    }




        /**
         * The call out implementation that accepts arguments for a given audience id and returns a value. The size of the
         * arguments array is guaranteed to be the same as returned by getNumberOfArguments().
         * @param audienceId - the audience id for the call out
         * @param configData - a map with name value pairs of configuration data
         * @param arguments  - arguments for the call out. Argument type checking should be done by the implementation. Each
         *      argument can be String, Double, Date or a List of one of these. A List argument can have null values inside it.
         * @return                 - value returned by the call out, which is a list of strings.
         * @throws CalloutException
         */
    public List<String> getValue(AudienceId audienceId, Map<String, String> configData, Object...arguments) throws CalloutException
    {
        List<String> result = new ArrayList<String>();

        if (!getStatus_ok()) {
            log.error("getValue(): cannot provide reliable values because internal status is not ok");
            return errorValue();
        }
        if (audienceId== null) {
            log.error("getValue() received a null audience id");
            return errorValue();
        }

        log.info("in getValue() "+" AudienceID: "+audienceId.toString());


        parseConfigMap(configData);


        String DSEvent = null;
        String CookieID = null;
        String email = null;
        try {
            // log input arguments
            log.info("getValue() Arguments:");
            int i = 1;
            for(Object arg : arguments) {
                if (arg == null) {
                    log.error("getValue() received a null parameter, param nr: "+i);
                    return errorValue();
                }
                log.info("argument["+i+"] = <"+arg+">");
                switch (i) {
                    case 1: { CookieID = arg.toString();
                        break;
                    }
                    case 2: { DSEvent = arg.toString();
                        break;
                    }
                    case 3: { email = arg.toString();
                        break;
                    }
                    default: {
                        log.error("unmanaged argument, it is arg nr: "+i);
                        setStatus_ok(false);
                        return errorValue();
                        // break;
                    }
                }
                i++;
            }

            // calculate values
            if (DSEvent != null && DSEvent.length() >0
                    && CookieID != null && CookieID.length() > 0
                    && email != null && email.length() > 0
                    ) {
                callStoredProcedure(CookieID, DSEvent, email);
            } else {
                log.error("wrong parameters or failed to unpack them");
                return errorValue();
            }

            // log return values
            log.info("Before existing getValue(), return values");
            i = 1;
            for (String v:  result) {
                log.info("return value["+i+"] = <"+v+">");
                i++;
            }
       }
        catch(Exception e) {
            log.error("Exception in getValue(), retrowing"+ e.toString());
            throw new CalloutException(e);
        }
       return result;
    }

    /**
     * Shuts down the call out.
     * @param configurationData
     * @throws CalloutException
     */
    public void shutdown(Map<String, String> configurationData) throws CalloutException
    {
        try
        {
            // Called at shutdown of the runtime server - for this example, let's just print out the configurationData
            log.debug("Calling the externalCallout shutdown");
            log.debug("Configuration passed into shutdown include");
            for(Entry<String, String> e : configurationData.entrySet()) {
                log.debug(e.getKey()+"="+e.getValue());
            }
            log.debug("externalCallout shutdown complete");
        }  catch(Exception e) {
            log.error("exception caught, will throw another");
            throw new CalloutException(e);
        }
    }

    public boolean setStatus_ok(boolean val) {
        if (!val) {
            log.debug("just to debug");
        }
        this.status = val;
        return this.status;
    }

    public boolean getStatus_ok() {
        if (!this.status) {
            log.info("status not ok, entering debug mode");
            this.debug_mode = true;
        }
        return this.status;
    }

    public static void main(String[] args) {

        CreateAndSegmentNewCookie_v02 co = new CreateAndSegmentNewCookie_v02();

        co.callStoredProcedure("44021460493888055239189", "DS_O", "unica_ev01@gmail.com");
    }

    // Unica Configuration parameters
    String config_dbuser;
    String config_dbpassword;
    String config_jdbc_driver_path;
    String config_jdbc_url;
    String config_debug_mode;

    static final String errorReturnValueString = "98765";
    boolean status = true;
    boolean debug_mode = false;
    final static org.apache.log4j.Logger log = org.apache.log4j.Logger.getLogger(CreateAndSegmentNewCookie_v02.class);
}