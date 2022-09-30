/*
 The integration developer needs to create the method processData 
 This method takes Message object of package com.sap.gateway.ip.core.customdev.util 
which includes helper methods useful for the content developer:
The methods available are:
    public java.lang.Object getBody()
	public void setBody(java.lang.Object exchangeBody)
    public java.util.Map<java.lang.String,java.lang.Object> getHeaders()
    public void setHeaders(java.util.Map<java.lang.String,java.lang.Object> exchangeHeaders)
    public void setHeader(java.lang.String name, java.lang.Object value)
    public java.util.Map<java.lang.String,java.lang.Object> getProperties()
    public void setProperties(java.util.Map<java.lang.String,java.lang.Object> exchangeProperties) 
    public void setProperty(java.lang.String name, java.lang.Object value)
    public java.util.List<com.sap.gateway.ip.core.customdev.util.SoapHeader> getSoapHeaders()
    public void setSoapHeaders(java.util.List<com.sap.gateway.ip.core.customdev.util.SoapHeader> soapHeaders) 
       public void clearSoapHeaders()
 */
import com.sap.gateway.ip.core.customdev.util.Message;
import java.util.HashMap;

import java.util.Base64; 
import org.json.JSONObject; 
import org.json.JSONArray;
import org.json.JSONException;
import javax.ws.rs.core.MediaType;
 
import org.apache.camel.*;


import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream; 
import java.net.HttpURLConnection;
import java.net.URL;
 

def Message processExtFctMetadata(Message message) {
    
    String finalXml = "<ExtractForecastMetadata>";
    def body=message.getBody(); 
    String algorithmName = "";
    String historicalPeriods = "";
    String forecastPeriods   = "";
   
    byte[] responseBody = body.getBytes();;
    try {
		JSONObject extractFctJSON =new JSONObject(new String(responseBody));

		JSONArray valueJSONArray = extractFctJSON.getJSONArray("value");

		if(valueJSONArray.length() > 0){
			JSONObject valueJSONObject =  valueJSONArray.getJSONObject(0);
			algorithmName = (String)valueJSONObject.get("AlgorithmName");
			historicalPeriods = (Integer)valueJSONObject.get("HistoricalPeriods");
			forecastPeriods = (Integer)valueJSONObject.get("ForecastPeriods");
			
			finalXml = finalXml + "<parameters historicalPeriods=" + "\"" + historicalPeriods  + "\" forecastPeriods=\"" + forecastPeriods +  "\" algorithmName=\"" + algorithmName + "\"></parameters>";
		    
			
			message.setProperty("historicalPeriods", historicalPeriods);
			message.setProperty("forecastPeriods", forecastPeriods); 
			message.setProperty("algorithmName", algorithmName); 
		} 

	    finalXml = finalXml+  "</ExtractForecastMetadata>";
       
	    // CLEAR HTTP HEaders
	  
	    message.setHeader("CamelHttpQuery", "");
	    message.setHeader("x-csrf-token", "");
	    
		message.setBody(finalXml);
	} catch (JSONException e) { 
		message.setBody(e);
	}
    return message;
}



def Message processExtFctAlgorithimInput(Message message) {
     
    def body=message.getBody(); 
    String algorithmName = "";
    String historicalPeriods = "";
    String forecastPeriods   = "";
   
    byte[] responseBody = body.getBytes();;
    try {
        //def map = message.getHeaders();
	    
        //def csrfToken = map.get("x-csrf-token");
        
        //message.setProperty("IBPCSRFToken", csrfToken);
        
        JSONObject metadataJSONObject = new JSONObject();
        
        metadataJSONObject.put("RequestID",          message.getProperty("RequestID"));
        metadataJSONObject.put("HistoricalPeriods",  message.getProperty("historicalPeriods"));
        metadataJSONObject.put("ForecastPeriods",    message.getProperty("forecastPeriods"));
        metadataJSONObject.put("AlgorithmName",      message.getProperty("algorithmName"));
        metadataJSONObject.put("AlgorithmParameter", ",");
        metadataJSONObject.put("Periodicity",         "");
        
        JSONArray metadataJSONArray = new JSONArray();   
        metadataJSONArray.put(metadataJSONObject);
        
		JSONObject extractFctJSON = new JSONObject(new String(responseBody));
		
		String eTag    = (String)extractFctJSON.get("@odata.metadataEtag");
		String context = (String)extractFctJSON.get("@odata.context"); 

		JSONArray valueJSONArray = extractFctJSON.getJSONArray("value");
		
		JSONObject azureMLJSONObject = new JSONObject();
		azureMLJSONObject.put("@odata.metadataEtag", eTag);
		azureMLJSONObject.put("@odata.context",      context);
		azureMLJSONObject.put("Metadata",            metadataJSONArray);
		azureMLJSONObject.put("value",               valueJSONArray);
		
		message.setProperty("eTag", eTag);
		message.setProperty("context", context);  
	    
	    def newBody = azureMLJSONObject.toString() as String;
    	long len = newBody.getBytes().length;
    	String payloadSize = len.toString(); 
    	
    	// CLEAR and SET HTTP HEaders
	    message.setHeader("CamelHttpQuery", "");
	    message.setHeader("x-csrf-token", "");
    	message.setHeader("Content-Length", payloadSize);
    	message.setHeader("Content-Type", "application/json");
    	message.setHeader("Authorization",  message.getProperty("AzureMLToken"));
	   //  message.setHeader("Authorization",);
	    
    	message.setBody(newBody);
	 
		
	} catch (JSONException e) { 
		message.setBody(e);
	}
    return message;
}

def String fetchToken(Message message) {
    
    def body = message.getBody(java.lang.String) as String;
    message.setProperty("tempBody", body);
    
    
    def getRequest = new URL(message.getProperty("IBPUrl") + "/Input").openConnection() as HttpURLConnection; 
	getRequest.setRequestMethod("GET");
	getRequest.setRequestProperty("User-Agent", "SAP CPI");
	getRequest.setRequestProperty("x-csrf-token", "fetch");
	getRequest.setRequestProperty('Authorization','Basic ' + message.getProperty("IBPUser").bytes.encodeBase64().toString());
	getRequest.connect(); 
	
    def status = getRequest.getResponseCode(); 
    String token = "init";
    def cookies = getRequest.getHeaderFields().get("set-cookie") as List<String>;
    
	if (status == HttpURLConnection.HTTP_OK) {
        token = getRequest.getHeaderField("x-csrf-token");
    }
    
    message.setProperty("IBPToken", token);
    
    message.setProperty("IBPCookie", cookies);
    
    return token;
		 
}


def Message prepareResults(Message message) {
        
    fetchToken(message);
    
    
    // def body = message.getBody(java.lang.String) as String;
    def body = message.getProperty("tempBody") as String;
	long len = body.getBytes().length;
	String payloadSize = len.toString(); 
	
    // message.setHeader("x-csrf-token",  message.getProperty("IBPCSRFToken")); 
	message.setHeader("Content-Length", payloadSize);
	message.setHeader("Content-Type", "application/json");
	message.setBody(body);  
	 
    def messageLog = messageLogFactory.getMessageLog(message);

    // Request
    def postRequest = new URL(message.getProperty("IBPUrl") + "/Result").openConnection() as HttpURLConnection;

    postRequest.setRequestMethod('POST'); 
    postRequest.setRequestProperty("Accept", 'application/json');
    postRequest.setRequestProperty("Content-Type", 'application/json');
	postRequest.setRequestProperty("User-Agent", "SAP CPI");
    postRequest.setRequestProperty("Content-Length", payloadSize);
    postRequest.setRequestProperty("x-csrf-token", message.getProperty("IBPToken"));
    
    def cookies = message.getProperty("IBPCookie");
    
    for (String cookie : cookies) {
        postRequest.addRequestProperty("Cookie", cookie.split(";", 2)[0]);
    }
    
    postRequest.setRequestProperty('Authorization','Basic ' + message.getProperty("IBPUser").bytes.encodeBase64().toString());
    
    String msg;
    postRequest.setDoOutput(true);
	OutputStream os = postRequest.getOutputStream();
	os.write(body.getBytes());
	os.flush();
	os.close();
	int responseCode = postRequest.getResponseCode();
	def inputStr;
	try{
	    inputStr = postRequest.getInputStream() as InputStream;
        // String encoding = postRequest.getContentEncoding() == null ? "UTF-8" : postRequest.getContentEncoding();
    
        // String inputLine = new String(inputStr.readAllBytes(), encoding); 
        String inputLine = read(inputStr);
        
    	if (responseCode == 200) {  
    	    msg = "POST request WORKED - " + responseCode + " \n " + inputLine; 
    	} else {
    	    msg = "POST request did not work - " + responseCode + " \n " + inputLine; 
    	} 
	    
	} catch (Exception e) {
	    msg = msg + e.toString();
	}  
     
    message.setBody(msg); 
    return message;
}


def String read(InputStream inputStream) throws IOException {
    def result = new StringBuilder() as StringBuilder;
    
    while (inputStream.available() > 0) {
        result.append(inputStream.read() as char);
    } 
    return result.toString();
}
