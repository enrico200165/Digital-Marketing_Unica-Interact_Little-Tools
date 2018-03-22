
package interact.clients_enrico;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.*;

import org.apache.commons.json.JSONException;

import com.unicacorp.interact.api.BatchResponse;
import com.unicacorp.interact.api.Command;
import com.unicacorp.interact.api.CommandImpl;
import com.unicacorp.interact.api.NameValuePair;
import com.unicacorp.interact.api.NameValuePairImpl;
import com.unicacorp.interact.api.rest.RestClientConnector;
import com.unicacorp.interact.testclient.JavaPrintUtil;
import org.apache.log4j.Logger;


public class UACI_Dev_RestClient {

	public static void setFiddler(boolean active){
		if(active){
			System.setProperty("http.proxyHost","127.0.0.1");
			System.setProperty("http.proxyPort","8888");

			System.setProperty("https.proxyHost","127.0.0.1");
			System.setProperty("https.proxyPort","8888");

			// per fiddler SSL
//			System.setProperty("proxySet","true");
//			System.setProperty("javax.net.ssl.trustStore","V:\\programs\\Java\\jdk1.7.0_79\\jre\\lib\\security\\FiddlerKeystore");
//			System.setProperty("javax.net.ssl.trustStorePassword","changeit");
//			System.setProperty("java.net.useSystemProxies", "true");
		}
	}


	static Map<String, String> configDataMap() {
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
			config.put("interact_REST_endpoint", prop.getProperty("interact_REST_endpoint"));
			config.put("interact_channel", prop.getProperty("interact_channel"));
			config.put("interact_audience_level", prop.getProperty("interact_audience_level"));
			config.put("interact_interaction_point", prop.getProperty("interact_interaction_point"));
			config.put("interact_nr_offers", prop.getProperty("interact_nr_offers"));
			// config.put("", prop.getProperty(""));

			//config.put("jdbc_driver_path", null);
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



	public static void main(String[] args) throws IOException, JSONException {

		try {
			// Locale.setDefault(new Locale("en_US"));

			setFiddler(true);

			log.info("working dir: "+System.getProperty("user.dir"));

			Map<String,String> cfgMap = configDataMap();

			String url = cfgMap.get("interact_REST_endpoint");
			String sessionId = String.valueOf(System.currentTimeMillis());
			String icName = cfgMap.get("interact_channel");
			String audienceLev = cfgMap.get("interact_audience_level");
			String ipName =  cfgMap.get("interact_interaction_point");
			int numberRequested = Integer.valueOf(cfgMap.get("interact_nr_offers"));

			int i = 0;
			List<Command> cmds = new ArrayList<Command>();
			cmds.add(i++, createStartSessionCommand(audienceLev, icName));
			cmds.add(i++, createGetOffersCommand(ipName, numberRequested));
			cmds.add(i++, createGetProfileCommand());
			cmds.add(i++, createEndSessionCommand());

			RestClientConnector.initialize();
			RestClientConnector connector = new RestClientConnector(url);
			BatchResponse response = connector.executeBatch(sessionId, cmds.toArray(new Command[0]), null, null);
			JavaPrintUtil.printBatchResponse(response);
		} catch(Exception e) {
			System.out.println(e);
		}
	}
	
	private static Command createStartSessionCommand(String audienceLev, String icName) throws JSONException {
		CommandImpl cmd = new CommandImpl();
		cmd.setMethodIdentifier(Command.COMMAND_STARTSESSION);
		cmd.setInteractiveChannel(icName);
		cmd.setAudienceLevel(audienceLev);
		cmd.setAudienceID(new NameValuePairImpl[] {new NameValuePairImpl("CookieID", NameValuePair.DATA_TYPE_STRING, "41131479893043143515320")});
		return cmd;
	}
	
	private static Command createGetOffersCommand(String ipName, int numberRequested) throws JSONException {
		CommandImpl cmd = new CommandImpl();
		cmd.setMethodIdentifier(Command.COMMAND_GETOFFERS);
		cmd.setInteractionPoint(ipName);
		cmd.setNumberRequested(numberRequested);
		return cmd;
	}

	private static Command createGetProfileCommand() throws JSONException {
		CommandImpl cmd = new CommandImpl();
		cmd.setMethodIdentifier(Command.COMMAND_GETPROFILE);
		return cmd;
	}
	
	private static Command createEndSessionCommand() throws JSONException {
		CommandImpl cmd = new CommandImpl();
		cmd.setMethodIdentifier(Command.COMMAND_ENDSESSION);
		return cmd;
	}

	final static Logger log = Logger.getLogger(UACI_Dev_RestClient.class);
}	