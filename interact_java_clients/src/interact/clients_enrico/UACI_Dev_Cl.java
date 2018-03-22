package interact.clients_enrico;


import com.unicacorp.interact.api.*;
import com.unicacorp.interact.api.jsoverhttp.InteractAPI;
import org.apache.log4j.Logger;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.rmi.RemoteException;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;

public class UACI_Dev_Cl
{
	private static NameValuePairImpl[] createInitialAudienceId() {
        NameValuePairImpl custId = new NameValuePairImpl();
        custId.setName("CookieID");
        custId.setValueAsString("41131479893043143515320");
        custId.setValueDataType(NameValuePair.DATA_TYPE_STRING);
        NameValuePairImpl[] initialAudienceId = { custId };
        return initialAudienceId;
	}

	/*
	 * Create the new audience ID components used in setAudience method call
	 * to change the audience ID of an existing session
	 */
	private static NameValuePairImpl[] createNewAudienceId() {
		NameValuePairImpl custId2 = new NameValuePairImpl();
		custId2.setName("CookieID");
		custId2.setValueAsString("44011496161028057645286");
            custId2.setValueDataType(NameValuePair.DATA_TYPE_STRING);

		NameValuePairImpl[] newAudienceId = { custId2 };
		return newAudienceId;
	}

	/*
	 * Create the initial parameters used for starting a new session
	 */
	private static NameValuePairImpl[] buildInitialParameters() {


		NameValuePairImpl parm1 = new NameValuePairImpl();
		parm1.setName("SearchString");
		parm1.setValueAsString("");
		parm1.setValueDataType(NameValuePair.DATA_TYPE_STRING);

		NameValuePairImpl parm2 = new NameValuePairImpl();
		parm2.setName("TimeStamp");
		parm2.setValueAsDate(new Date());
		parm2.setValueDataType(NameValuePair.DATA_TYPE_DATETIME);

		NameValuePairImpl parm3 = new NameValuePairImpl();
		parm3.setName("Browser");
		parm3.setValueAsString("IE6");
		parm3.setValueDataType(NameValuePair.DATA_TYPE_STRING);

		NameValuePairImpl parm4 = new NameValuePairImpl();
		parm4.setName("FlashEnabled");
		parm4.setValueAsNumeric(1.0);
		parm4.setValueDataType(NameValuePair.DATA_TYPE_NUMERIC);

		NameValuePairImpl parm5 = new NameValuePairImpl();
		parm5.setName("TxAcctValueChange");
		parm5.setValueAsNumeric(0.0);
		parm5.setValueDataType(NameValuePair.DATA_TYPE_NUMERIC);

		NameValuePairImpl parm6 = new NameValuePairImpl();
		parm6.setName("PageTopic");
		parm6.setValueAsString("");
		parm6.setValueDataType(NameValuePair.DATA_TYPE_STRING);

		NameValuePairImpl[] initialParameters = { parm1, parm2, parm3, parm4, parm5, parm6 };

		return initialParameters;
	}

	/*
	 * Create the parameters used for posting an event against and existing session
	 */
	private static NameValuePairImpl[] buildEventParameters() {
		NameValuePairImpl parmB1 = new NameValuePairImpl();
		parmB1.setName("SearchString");
		parmB1.setValueAsString("mortgage");
		parmB1.setValueDataType(NameValuePair.DATA_TYPE_STRING);

		NameValuePairImpl parmB2 = new NameValuePairImpl();
		parmB2.setName("TimeStamp");
		parmB2.setValueAsDate(new Date());
		parmB2.setValueDataType(NameValuePair.DATA_TYPE_DATETIME);

		NameValuePairImpl parmB3 = new NameValuePairImpl();
		parmB3.setName("Browser");
		parmB3.setValueAsString("IE6");
		parmB3.setValueDataType(NameValuePair.DATA_TYPE_STRING);

		NameValuePairImpl parmB4 = new NameValuePairImpl();
		parmB4.setName("FlashEnabled");
		parmB4.setValueAsNumeric(1.0);
		parmB4.setValueDataType(NameValuePair.DATA_TYPE_NUMERIC);

		NameValuePairImpl parmB5 = new NameValuePairImpl();
		parmB5.setName("TxAcctValueChange");
		parmB5.setValueAsNumeric(0.0);
		parmB5.setValueDataType(NameValuePair.DATA_TYPE_NUMERIC);

		NameValuePairImpl parmB6 = new NameValuePairImpl();
		parmB6.setName("PageTopic");
		parmB6.setValueAsString("");
		parmB6.setValueDataType(NameValuePair.DATA_TYPE_STRING);


		NameValuePairImpl[] postEventParameters = { parmB1, parmB2, parmB3, parmB4, parmB5, parmB6 };
		return postEventParameters;
	}

	private static GetOfferRequest[] createGetOffersRequests() {
		
		String[] interactionPoint = new String[] {"ip1", "ip2"};
		// int[] numberRequested = new int[] {3, 5};
        int[] numberRequested = new int[] {1, 1};
        int[] duplicationPolicy = new int[] {GetOfferRequest.ALLOW_DUPLICATION, GetOfferRequest.NO_DUPLICATION};
		
		GetOfferRequest request1 = new GetOfferRequest(numberRequested[0], duplicationPolicy[0]);
		request1.setIpName(interactionPoint[0]);
		OfferAttributeRequirements offerAttributes1 = new OfferAttributeRequirements();
		offerAttributes1.addAttributes(
				new NameValuePair[] {
						new NameValuePairImpl("attribute1", NameValuePair.DATA_TYPE_STRING, "attr1_value"),
						new NameValuePairImpl("attribute2", NameValuePair.DATA_TYPE_NUMERIC, Double.valueOf("1.23"))
				});
		OfferAttributeRequirements childRequirement = new OfferAttributeRequirements();
		childRequirement.addAttributes(new NameValuePair[] {
				new NameValuePairImpl("attribute3", NameValuePair.DATA_TYPE_DATETIME, new Date())});
		offerAttributes1.addChildRequirement(childRequirement);
		request1.setOfferAttributes(offerAttributes1);
		
		GetOfferRequest request2 = new GetOfferRequest(numberRequested[1], duplicationPolicy[1]);
		request2.setIpName(interactionPoint[1]);
		OfferAttributeRequirements offerAttributes2 = new OfferAttributeRequirements();
		offerAttributes2.addAttributes(
				new NameValuePair[] {
						new NameValuePairImpl("attribute4", NameValuePair.DATA_TYPE_STRING, "value_of_attr4")});
		offerAttributes2.addChildRequirement(childRequirement);
		request2.setOfferAttributes(offerAttributes2);
		GetOfferRequest[] requests = {request1, request2};
		return requests;
	}
	/**********************************************************************************
	 * start a new session 
	 *********************************************************************************/
	private static Response sendStartSessionRequest(InteractAPI api,
													String audienceLevel,
													String sessionId,
													boolean relyOnExistingSession,
													boolean initialDebugFlag,
													String interactiveChannel)
											throws RemoteException {
        
        /**
         * The visitor for the session needs to be identified with an audience id and audience level. 
         * Audience level is simply a string while audience id is an array of name value pairs where
         * the names must match the physical column names of any table containing the audience id.
         * 
         * In this example, the audienceLevel is "Customer" and the audienceId is comprised of just
         * one column called "CookieID" with data type numeric.
         */
        
        NameValuePair[] initialAudienceId = createInitialAudienceId();
       
        /**
         * Any additional parameters that describe the visitors current state can be passed along in the startSession
         * to be fed into the segmentation logic.  Similar to an audienceId, this would be an array of NameValuePair
         * objects.  For this example, we will pass in:
         *  SearchString,"",string;
         *  TimeStamp,currentDate,datetime;
         *  Browser,"IE6",string;
         *  FlashEnabled,1,numeric;
         *  TxAcctValueChange,0,numeric;
         *  PageTopic,"",string
         */
        NameValuePairImpl[] initialParameters = buildInitialParameters();
        
        /**
         * Make the call
         */
        Response response = api.startSession(sessionId, relyOnExistingSession, initialDebugFlag, interactiveChannel, initialAudienceId, audienceLevel, initialParameters);

        return response;
	}

    /*********************************************************************************
     * get offers for a specific interaction point
     * an existing session is required to make this method call
     *********************************************************************************/
	private static Response sendGetOffersRequest(InteractAPI api, String sessionId, String interactionPoint, int numberRequested) throws RemoteException {
		Response response = api.getOffers(sessionId, interactionPoint, numberRequested);
		return response;
	}

    /*********************************************************************************
     * get offers for multiple interaction points at the same time
     * if the duplication policy is 2 (ALLOW_DUPLICATION), this method behaves like 
     * a wrapper of multiple calls of getOffers for those interaction points
     * on the other hand, if duplicate policy is 1 (NO_DUPLICATION) is used for 
     * one or more interaction points, de-dupe action will be performed on those IPs.
     * 
     * an existing session is required to make this method call
     **********************************************************************************/
	private static Response sendGetOffersForMultipleInteractionPointsRequest(InteractAPI api, String sessionId) throws RemoteException {
		
		GetOfferRequest[] requests = createGetOffersRequests();
		
		Response response = api.getOffersForMultipleInteractionPoints(sessionId, requests);
		return response;
	}

	/*********************************************************************************
	 * post an event against an existing session
	 * an existing session is required to make this method call
	 **********************************************************************************/
	private static Response sendPostEventRequest(InteractAPI api, String sessionId, String eventName) throws RemoteException {
       
        /**
         * Similar to the startSession, the client may submit parameters describing the current
         * state of the visit.  For this example, the parms are the same except the "searchString"
         * parameter has a value in it:
         * SearchString,"mortgage",string;
         * TimeStamp,current date,datetime;
         * Browser,"IE6",string;
         * FlashEnabled,1,numeric;
         * TxAcctValueChange,0,numeric;
         * PageTopic,"",string
         * 
         * And of course, it would be more efficient to not bother passing along parameters that haven't
         * changed.  but for this example, we'll go ahead and submit the same parameters again.
         */
        
        NameValuePairImpl[] postEventParameters = buildEventParameters();
        
        /**
         * make the call ( reuse the session Id from above )
         */
        Response response = api.postEvent(sessionId, eventName, postEventParameters);
		return response;
	}
	

	/*********************************************************************************
     * get the audience profile associated with the specified session
     * an existing session is required to make this method call
     **********************************************************************************/
	private static Response sendGetProfileRequest(InteractAPI api, String sessionId) throws RemoteException {
		Response response = api.getProfile(sessionId);
		return response;
	}
	
	/*********************************************************************************
	 * change the audience of an existing session
	 * an existing session is required to make this method call
	 **********************************************************************************/
	private static Response sendSetAudienceRequest(InteractAPI api, String audienceLevel, String sessionId) throws RemoteException {
        
        /**
         * For this example, let's keep the same audience level, but change the id associated
         * (a real life example would be the anonymous user logs in and becomes known)
         */
        NameValuePairImpl custId2 = new NameValuePairImpl();
        custId2.setName("CookieID");
        custId2.setValueAsString("44051480079295031218685");
        custId2.setValueDataType(NameValuePair.DATA_TYPE_STRING);
        
        NameValuePairImpl[] newAudienceId = { custId2 };
        
        /**
         * Similar to the startSession, parameters can be passed in as well.  For this example
         * we could just pass in null;
         */
        NameValuePairImpl[] noParameters=null;
        
        /**
         * make the call - reuse sessionId and audienceLevel from above
         */
        Response response = api.setAudience(sessionId, newAudienceId, audienceLevel, noParameters);
        return response;
	}
	
	/*********************************************************************************
	 * change the debug flag of the specified session 
	 * an existing session is required to make this method call
	 **********************************************************************************/
	private static Response sendSetDebugRequest(InteractAPI api, String sessionId, boolean newDebugFlag) throws RemoteException {
        
        /**
         * make the call - reuse sessionId from above
         */
        Response response = api.setDebug(sessionId, newDebugFlag);
        return response;
	}

	/*********************************************************************************
     * get the version of this running Interact instance
     * an existing session is required to make this method call
     **********************************************************************************/
	public static Response sendGetVersionRequest(InteractAPI api) throws RemoteException {
		Response response = api.getVersion();
		return response;
	}
	
	/*********************************************************************************
     * close the specified session
     * an existing session is required to make this method call
     **********************************************************************************/
	private static Response sendEndSessionRequest(InteractAPI api, String sessionId) throws RemoteException {
		Response response = api.endSession(sessionId);
		return response;
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
			config.put("interact_endpoint", prop.getProperty("interact_endpoint"));
			config.put("interact_channel", prop.getProperty("interact_channel"));
			config.put("interact_audience_level", prop.getProperty("interact_audience_level"));
			config.put("interact_interaction_point", prop.getProperty("interact_interaction_point"));
			config.put("interact_nr_offers", prop.getProperty("interact_nr_offers"));
			config.put("interact_event", prop.getProperty("interact_event"));

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



	public static void main(String args[]) throws Exception
    {

		Map<String,String> cfgMap = configDataMap();

		InteractAPI api = InteractAPI.getInstance(cfgMap.get("interact_endpoint"));

		/**
         * The visitor for the session needs to be identified with an audience id and audience level. 
         * Audience level is simply a string while audience id is an array of name value pairs where
         * the names must match the physical column names of any table containing the audience id.
         * 
         * In this example, the audienceLevel is "Customer" and the audienceId is comprised of just
         * one column called "CookieID" with data type numeric.
         */
        // String audienceLevel="Customer";
        String audienceLevel=cfgMap.get("interact_audience_level");

        
        /**
         * When calling the startSession method, the client has the option to either force the server to 
         * create a brand new session with the specified sessionId, OR, for optimization purposes, request
         * that the server attempt to rely on any existing session already created (and not expired) for
         * the specified session id.  To control this behavior, the relyOnExistingSession can be set to either
         * true or false.
         */
        boolean relyOnExistingSession=false;
        
        
        /**
         * In most production systems, the verbosity level is low.  If the client wanted to turn up the
         * verbosity level (ie. to debug) just for the code path of the current session, the debug can be set
         * to true.  Otherwise, false to not have the verbosity level changed on the server side.
         */
        boolean initialDebugFlag=true;
        String interactiveChannel=cfgMap.get("interact_channel");


        String interactionPoint = cfgMap.get("interact_interaction_point");

        //  Client also needs to specify how many offers to return
        int numberRequested= Integer.valueOf(cfgMap.get("interact_nr_offers"));
        
        /**
         * When posting an event, an event name needs to be specified.  Similar to the Interaction
         * Point, the event must be defined in the interact runtime server
         */
        String eventName = cfgMap.get("interact_event");
        
        /**
         * For this example we can turn on the debug call - performs the same debug toggle
         * as the startSession call
         */
        boolean newDebugFlag=false;
        
        /**
         * All methods (except for executeBatch) will return a Response object.
         * 
         * The response object contains a super set of data that supports all the
         * methods.  Depending on the method you call, the appropriate data items
         * in the response object will be populated.
         * 
         * ExecuteBatch returns a BatchResponse, which is merely an array of Response
         * objects, one corresponding to each specified command in the executeBatch call.
         * 
         */
        Response response = null;
        
        /*********************************************************************************
         * Method: startSession 
         **********************************************************************************/
        
        /**
         * To define what makes an Interact "session" a session id has to be specified.  This value 
         * is managed by the client.  All method calls for the same session id has to be synchronized
         * by the client.  Otherwise, the behavior for concurrent api calls with the same session id is 
         * undefined.
         */
        String time=""+(new Date()).getTime();
        String sessionId=time;
        
        for(int x=0;x<5;x++) {
        	
        	/**
        	 * create a unique ID for this session
        	 */
        	sessionId=time+"_"+x;
        	System.out.println("XXXXXXXXXXXXXXXXX"+sessionId);
        	
        	/**
             * make the call - reuse sessionId and audienceLevel from above
             */
	        response = sendStartSessionRequest(api, audienceLevel, sessionId, relyOnExistingSession, initialDebugFlag, interactiveChannel);
	        
	        /**
	         * Now process the response appropriately
	         */
	        processStartSessionResponse(response);

	        /*********************************************************************************
	         * Method: getOffers
	         **********************************************************************************/

	     //  Thread.sleep(1000);
	        /**
	         * make the call ( reuse the session Id from above )
	         */
	        response = sendGetOffersRequest(api, sessionId, interactionPoint, numberRequested);

	        /**
	         * Now process the response appropriately
	         */
	        processGetOffersResponse(response);
        
	        /*********************************************************************************
	         * Method: getOffersForMultipleInteractionPoints
	         **********************************************************************************/
	    	response = sendGetOffersForMultipleInteractionPointsRequest(api, sessionId);

	    	processGetOffersForMultipleInteractionPointsResponse(response);
	    	
	        /*********************************************************************************
	         * Method: postEvent
	         **********************************************************************************/
	       
	        response = sendPostEventRequest(api, sessionId, eventName);
	        
	        /**
	         * Now process the response appropriately
	         */
	        processPostEventResponse(response);
	        
	        /*********************************************************************************
	         * Method: getProfile
	         **********************************************************************************/
	       
	        /**
	         * make the call ( reuse the session Id from above )
	         */
	        response = sendGetProfileRequest(api, sessionId);
	        
	        /**
	         * Now process the response appropriately
	         */
	        processGetProfileResponse(response);
	       
	        
	        /*********************************************************************************
	         * Method: setAudience
	         **********************************************************************************/
	       
	        /**
	         * make the call - reuse sessionId and audienceLevel from above
	         */
	        response = sendSetAudienceRequest(api, audienceLevel, sessionId);
	        
	        /**
	         * Now process the response appropriately
	         */
	        processSetAudienceResponse(response);
	
	        
	        /*********************************************************************************
	         * Method: setDebug 
	         **********************************************************************************/
	        
	        /**
	         * make the call - reuse sessionId from above
	         */
	        response = sendSetDebugRequest(api, sessionId, newDebugFlag);
	        
	        /**
	         * Now process the response appropriately
	         */
	        processSetDebugResponse(response);
	
	        
	        /*********************************************************************************
	         * Method: getVersion
	         **********************************************************************************/
	
	        /**
	         * make the call - this call does not need a valid sessionId
	         */
	        response = sendGetVersionRequest(api);
	        
	        /**
	         * Now process the response appropriately
	         */
	        processGetVersionResponse(response);
	
	       
	        /*********************************************************************************
	         * Method: endSession
	         **********************************************************************************/
	        /**
	         * make the call - reuse sessionId from above
	         */
	        response = sendEndSessionRequest(api, sessionId);
	        
	        /**
	         * Now process the response appropriately
	         */
	        processEndSessionResponse(response);
	    }
        
        
        /*********************************************************************************
         * Method: executeBatch 
         **********************************************************************************/

        /**
         * For this example, lets combine all the above calls in one by calling the executeBatch command.
         * The advantage of this is so that we can minimize the number of trips to the server.
         * To accomplish all the above calls under one executeBatch (and yes this scenario would be an unrealistic
         * use case) we could do the following.  Note that each parameter for the above methods have matching
         * setters in the Command object - except for sessionId.
         */
        
        /*
         * build the startSession command
         */
        Command startSessionCommand = new CommandImpl();
        startSessionCommand.setMethodIdentifier(Command.COMMAND_STARTSESSION);
        startSessionCommand.setInteractiveChannel(interactiveChannel);
        startSessionCommand.setAudienceID(createInitialAudienceId());
        startSessionCommand.setAudienceLevel(audienceLevel);
        startSessionCommand.setEventParameters(buildInitialParameters());
        startSessionCommand.setDebug(initialDebugFlag);
        startSessionCommand.setRelyOnExistingSession(relyOnExistingSession);
        
        /*
         * build the getOffers command
         */
        Command getOffersCommand = new CommandImpl();
        getOffersCommand.setMethodIdentifier(Command.COMMAND_GETOFFERS);
        getOffersCommand.setInteractionPoint(interactionPoint);
        getOffersCommand.setNumberRequested(numberRequested);

        /*
         * build the getOffersForMultipleInteractionPoints command
         */
        Command getOffersForMultiIPsCommand = new CommandImpl();
        getOffersForMultiIPsCommand.setMethodIdentifier(Command.COMMAND_GETOFFERS_MULTI_IP);
        GetOfferRequest[] requests = createGetOffersRequests();
        getOffersForMultiIPsCommand.setGetOfferRequests(requests);
        
        /*
         * build the postEvent command
         */
        Command postEventCommand = new CommandImpl();
        postEventCommand.setMethodIdentifier(Command.COMMAND_POSTEVENT);
        postEventCommand.setEventParameters(buildEventParameters());
        postEventCommand.setEvent(eventName);
        
        /*
         * build the getProfile command
         */
        Command getProfileCommand = new CommandImpl();
        getProfileCommand.setMethodIdentifier(Command.COMMAND_GETPROFILE);
        
        /*
         * build the setAudience command
         */
        Command setAudienceCommand = new CommandImpl();
        setAudienceCommand.setMethodIdentifier(Command.COMMAND_SETAUDIENCE);
        setAudienceCommand.setAudienceID(createNewAudienceId());
        setAudienceCommand.setAudienceLevel(audienceLevel);
        
        /*
         * build the setDebug command
         */
        Command setDebugCommand = new CommandImpl();
        setDebugCommand.setMethodIdentifier(Command.COMMAND_SETDEBUG);
        setDebugCommand.setDebug(newDebugFlag);

        /*
         * build the getVersion command
         */
        Command getVersionCommand = new CommandImpl();
        getVersionCommand.setMethodIdentifier(Command.COMMAND_GETVERSION);
        
        /*
         * build the endSession command
         */

        Command endSessionCommand = new CommandImpl();
        endSessionCommand.setMethodIdentifier(Command.COMMAND_ENDSESSION);
     
        /**
         * Build command array
         */
        Command[] commands = 
        { 
                startSessionCommand,
                getOffersCommand,
                getOffersForMultiIPsCommand,
                postEventCommand,
                getProfileCommand,
                setAudienceCommand,
                setDebugCommand,
                getVersionCommand,
                endSessionCommand
        };
        
        /**
         * make the call - reuse above sessionId
         */
        BatchResponse batchResponse = api.executeBatch(sessionId, commands);
        
        /**
         * Now process the response appropriately
         */
        processExecuteBatchResponse(batchResponse);
    }
    
    /**
     * Handle the response of a startSession call
     * @param response
     */
    public static void processStartSessionResponse(Response response)
    {
        // check if response is successful or not
        if(response.getStatusCode() == Response.STATUS_SUCCESS)
        {
            System.out.println("startSession call processed with no warnings or errors");
        }
        else if(response.getStatusCode() == Response.STATUS_WARNING)
        {
            System.out.println("startSession call processed with a warning");
        }
        else
        {
            System.out.println("startSession call processed with an error");
        }
        
        // For any non-successes, there should be advisory messages explaining why
        if(response.getStatusCode() != Response.STATUS_SUCCESS)
            printDetailMessageOfWarningOrError("StartSession",response.getAdvisoryMessages());
        
        // All responses will return the sessionId that was passed into the calling method (except
        // for getVersion, which does not require a sessionId
        System.out.println("This response pertains to sessionId:"+response.getSessionID());
    }

    /**
     * Help method for printing out the details of delivered offers
     * @param offerList
     */
    private static void printRecommendedOffers(OfferList offerList) {
        if(offerList.getRecommendedOffers() != null)
        {
        	int offerCount = offerList.getRecommendedOffers().length;
        	System.out.println("For interaction point " + offerList.getInteractionPointName() + ", the following " + offerCount + " will be delivered:");
        	
        	for (int idx=0; idx<offerCount; idx++) {
        		Offer offer = offerList.getRecommendedOffers()[idx];
            
                // print offer
                System.out.println("Offer Name:"+offer.getOfferName());
                
                System.out.println("Offer Desc:"+offer.getDescription());
                
                System.out.println("Offer score:"+offer.getScore());
                
                // the treatment code needs to be returned via the postEvent call for any
                // contact or response events
                System.out.println("Offer treatmentcode:"+offer.getTreatmentCode());
                
                // Let's iterate through the offerAttributes
                for(NameValuePair offerAttribute : offer.getAdditionalAttributes())
                {                        
                    // now let's pick out the effective date if it exists just for fun
                    if(offerAttribute.getName().equalsIgnoreCase("effectiveDate"))
                    {
                        System.out.println("Found effective date");
                    }
                    // now let's pick out the expiration date if it exists just for fun
                    else if(offerAttribute.getName().equalsIgnoreCase("expirationDate"))
                    {
                        System.out.println("Found expiration date");
                    }
                  
                    printNameValuePair(offerAttribute);
                }
            }
        }
        else {
        	// count on the default Offer String
        	System.out.println("Default offer:"+offerList.getDefaultString());
        }
    }
    
    /**
     * Handle the response of a getOffers call
     * @param response
     */
    public static void processGetOffersResponse(Response response)
    {
        // check if response is successful or not
        if(response.getStatusCode() == Response.STATUS_SUCCESS)
        {
            System.out.println("getOffers call processed with no warnings or errors");
            
            /**
             * Now check to see if there are any offers
             */
            OfferList offerList=response.getOfferList();
            printRecommendedOffers(offerList);
        }
        else if(response.getStatusCode() == Response.STATUS_WARNING)
        {
            System.out.println("ZZZZZZZZZZZZZZZZZZZZZZZZZgetOffers call processed with a warning");
        }
        else
        {
            System.out.println("getOffers call processed with an error");
        }
        
        // For any non-successes, there should be advisory messages explaining why
        if(response.getStatusCode() != Response.STATUS_SUCCESS)
            printDetailMessageOfWarningOrError("getOffers",response.getAdvisoryMessages());
    }

    /**
     * Handle the response of a getOffersForMultipleInteractionPointsResponse call
     * @param response
     */
    public static void processGetOffersForMultipleInteractionPointsResponse(Response response)
    {
        // check if response is successful or not
        if(response.getStatusCode() == Response.STATUS_SUCCESS)
        {
            System.out.println("getOffersForMultipleInteractionPointsResponse call processed with no warnings or errors");
            
            /**
             * Now check to see if there are any offers
             */
            OfferList[] offerLists = response.getAllOfferLists();
            int totalNumberOfOfferLists = offerLists.length;
            for (int idx=0; idx<totalNumberOfOfferLists; idx++) {
            	OfferList ol = offerLists[idx];
            	printRecommendedOffers(ol);
            }
        }
        else if(response.getStatusCode() == Response.STATUS_WARNING)
        {
            System.out.println("ZZZZZZZZZZZZZZZZZZZZZZZZZgetOffers call processed with a warning");
        }
        else
        {
            System.out.println("getOffers call processed with an error");
        }
        
        // For any non-successes, there should be advisory messages explaining why
        if(response.getStatusCode() != Response.STATUS_SUCCESS)
            printDetailMessageOfWarningOrError("getOffers",response.getAdvisoryMessages());
    }

    /**
     * Handle the response of a postEvent call
     * @param response
     */
    public static void processPostEventResponse(Response response)
    {
        // check if response is successful or not
        if(response.getStatusCode() == Response.STATUS_SUCCESS)
        {
            System.out.println("postEvent call processed with no warnings or errors");
        }
        else if(response.getStatusCode() == Response.STATUS_WARNING)
        {
            System.out.println("postEvent call processed with a warning");
        }
        else
        {
            System.out.println("postEvent call processed with an error");
        }
        
        // For any non-successes, there should be advisory messages explaining why
        if(response.getStatusCode() != Response.STATUS_SUCCESS)
            printDetailMessageOfWarningOrError("postEvent",response.getAdvisoryMessages());
    }
    

    /**
     * Handle the response of a getProfile call
     * @param response
     */
    public static void processGetProfileResponse(Response response)
    {
        // check if response is successful or not
        if(response.getStatusCode() == Response.STATUS_SUCCESS)
        {
            System.out.println("getProfile call processed with no warnings or errors");
            
            // now print the profile - its just an array of NameValuePair objects
            for(NameValuePair nvp : response.getProfileRecord())
            {
                if (nvp == null) {
                    System.out.println("Name value pair is NULL skipping name value pair");
                    continue;
                }
                if (nvp.getName() == null) {
                    System.out.println("Name value pair has NULL NAME skipping name value pair");
                    continue;
                } else {
                    System.out.println("Name:"+nvp.getName());
                }
                if (nvp.getValueDataType() == null) {
                    System.out.println("Name value pair has NULL nvp.getValueDataType() skipping name value pair");
                    continue;
                }
                if(nvp.getValueDataType().equals(NameValuePair.DATA_TYPE_DATETIME))
                {
                    if (nvp.getValueAsDate() != null) {
                        System.out.println("Value:" + nvp.getValueAsDate());
                    } else {
                        System.out.println("Value:" + " is NULL");
                    }
                }
                else if(nvp.getValueDataType().equals(NameValuePair.DATA_TYPE_NUMERIC))
                {
                    System.out.println("Value:"+nvp.getValueAsNumeric());
                }
                else
                {
                    if (nvp.getValueAsString() != null) {
                        System.out.println("Value:" + nvp.getValueAsString());
                    } else {
                        System.out.println("Value:" + " is NULL");
                    }
                }
               
            }
            
        }
        else if(response.getStatusCode() == Response.STATUS_WARNING)
        {
            System.out.println("getProfile call processed with a warning");
        }
        else
        {
            System.out.println("getProfile call processed with an error");
        }
        
        // For any non-successes, there should be advisory messages explaining why
        if(response.getStatusCode() != Response.STATUS_SUCCESS)
            printDetailMessageOfWarningOrError("getProfile",response.getAdvisoryMessages());    
        
        // now let's print out the profile record, if any
        if(response.getProfileRecord() != null)
            for( NameValuePair variable : response.getProfileRecord())
            {
                printNameValuePair(variable);
            }
    }
    
    /**
     * Handle the response of a setAudience call
     * @param response
     */
    public static void processSetAudienceResponse(Response response)
    {
        // check if response is successful or not
        if(response.getStatusCode() == Response.STATUS_SUCCESS)
        {
            System.out.println("setAudience call processed with no warnings or errors");
        }
        else if(response.getStatusCode() == Response.STATUS_WARNING)
        {
            System.out.println("setAudience call processed with a warning");
        }
        else
        {
            System.out.println("setAudience call processed with an error");
        }
        
        // For any non-successes, there should be advisory messages explaining why
        if(response.getStatusCode() != Response.STATUS_SUCCESS)
            printDetailMessageOfWarningOrError("setAudience",response.getAdvisoryMessages());
    }
    
    /**
     * Handle the response of a setDebug call
     * @param response
     */
    public static void processSetDebugResponse(Response response)
    {
        // check if response is successful or not
        if(response.getStatusCode() == Response.STATUS_SUCCESS)
        {
            System.out.println("setDebug call processed with no warnings or errors");
        }
        else if(response.getStatusCode() == Response.STATUS_WARNING)
        {
            System.out.println("setDebug call processed with a warning");
        }
        else
        {
            System.out.println("setDebug call processed with an error");
        }
        
        // For any non-successes, there should be advisory messages explaining why
        if(response.getStatusCode() != Response.STATUS_SUCCESS)
            printDetailMessageOfWarningOrError("setDebug",response.getAdvisoryMessages());
    }
    
    /**
     * Handle the response of a getVersion call
     * @param response
     */
    public static void processGetVersionResponse(Response response)
    {
        // check if response is successful or not
        if(response.getStatusCode() == Response.STATUS_SUCCESS)
        {
            System.out.println("getVersion call processed with no warnings or errors");
        }
        else if(response.getStatusCode() == Response.STATUS_WARNING)
        {
            System.out.println("getVersion call processed with a warning");
        }
        else
        {
            System.out.println("getVersion call processed with an error");
        }
        
        // For any non-successes, there should be advisory messages explaining why
        if(response.getStatusCode() != Response.STATUS_SUCCESS)
            printDetailMessageOfWarningOrError("getVersion",response.getAdvisoryMessages());
    }
    
    
    /**
     * Handle the response of a endSession call
     * @param response
     */
    public static void processEndSessionResponse(Response response)
    {
        // check if response is successful or not
        if(response.getStatusCode() == Response.STATUS_SUCCESS)
        {
            System.out.println("endSession call processed with no warnings or errors");
        }
        else if(response.getStatusCode() == Response.STATUS_WARNING)
        {
            System.out.println("endSession call processed with a warning");
        }
        else
        {
            System.out.println("endSession call processed with an error");
        }
        
        // For any non-successes, there should be advisory messages explaining why
        if(response.getStatusCode() != Response.STATUS_SUCCESS)
            printDetailMessageOfWarningOrError("endSession",response.getAdvisoryMessages());
    }
    
    
    public static void processExecuteBatchResponse(BatchResponse batchResponse)
    {
        // Top level status code is a short cut to determine if there are any Non successes in
        // the array of Response objects
        if(batchResponse.getBatchStatusCode() == Response.STATUS_SUCCESS)
        {
            System.out.println("ExecuteBatch ran perfectly!");
        }
        else if(batchResponse.getBatchStatusCode() == Response.STATUS_WARNING)
        {
            System.out.println("ExecuteBatch call processed with at least one warning");
        }
        else
        {
            System.out.println("ExecuteBatch call processed with at least one error");
        }
        
        
        // Iterate through the array, and print out the message for any non-successes
        for(Response response : batchResponse.getResponses())
        {
            if(response.getStatusCode()!=Response.STATUS_SUCCESS)
            {
                printDetailMessageOfWarningOrError("executeBatchCommand",response.getAdvisoryMessages());
            }
        }
    }
    
    /**
     * convenience method to print out the advisory message.   In production systems
     * this info should go to a monitoring or logging service.  For this example,
     * we will just print to standard out.
     */
    public static void printDetailMessageOfWarningOrError(String command,AdvisoryMessage[] messages)
    {
        System.out.println("Calling "+command);
        for(AdvisoryMessage msg : messages)
        {
            System.out.println(msg.getMessage());
            // Some advisory messages may have additional detail:
            System.out.println(msg.getDetailMessage());
            
            // All advisory messages have a code that will allow the client to implement different
            // behavior based on the type of warning/error
            if(msg.getMessageCode()==AdvisoryMessageCodes.INVALID_INTERACTIVE_CHANNEL)
            {
                System.out.println("IC passed in is not valid!!");
            }
            else if(msg.getMessageCode()==AdvisoryMessageCodes.INVALID_INTERACTION_POINT)
            {
                System.out.println("IP name passed in is not valid!!");
            } // and so on...
            else  // a catch all
            {
                System.out.println("Method call failed!");
            }
        }
    }
    
    /**
     * convenience method to print out a NameValuePair object
     * @param nvp
     */
    public static void printNameValuePair(NameValuePair nvp)
    {
        // print out the name:
        System.out.println("Name:"+nvp.getName());
        
        // based on the datatype, call the appropriate method to get the value
        if(nvp.getValueDataType()==NameValuePair.DATA_TYPE_DATETIME)
            System.out.println("DateValue:"+nvp.getValueAsDate());
        else if(nvp.getValueDataType()==NameValuePair.DATA_TYPE_NUMERIC)
            System.out.println("NumericValue:"+nvp.getValueAsNumeric());
        else
            System.out.println("StringValue:"+nvp.getValueAsString());
    }


	final static Logger log = Logger.getLogger(UACI_Dev_Cl.class);
}
