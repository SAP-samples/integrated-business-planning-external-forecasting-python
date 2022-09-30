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
import com.sap.it.api.msglog.*;
import java.util.HashMap;
import java.util.UUID; 
import java.util.Iterator; 
import java.util.List; 
import java.lang.Thread;
import java.lang.String;
import java.lang.Integer;
import com.sap.it.api.mapping.*;
import groovy.xml.XmlUtil;

def Message processData(Message message) {
       //Body 
       def body = message.getBody();
       message.setBody(body + "Body is modified");
       //Headers 
       def map = message.getHeaders();
       def value = map.get("oldHeader");
       message.setHeader("oldHeader", value + "modified");
       message.setHeader("newHeader", "newHeader");
       //Properties 
       map = message.getProperties();
       value = map.get("oldProperty");
       message.setProperty("oldProperty", value + "modified");
       message.setProperty("newProperty", "newProperty");
       return message;
}

def String getContextProperty(String propName, MappingContext context){
    String propValue = context.getProperty(propName);
	return propValue; 
}


def String getCounter(String counterName,Message message) {
    Integer counterValue = message.getProperty(counterName) as Integer ?:0;
    counterValue = counterValue + 1;
    message.setProperty(counterName,counterValue);
    return counterValue;
}

def String addGetCounter(String counterName,Message message) {
    Integer counterValue = message.getProperty(counterName) as Integer ?:0;
    message.setProperty(counterName,++counterValue);
    return counterValue;
}

def Message logMessage(java.lang.String fileName, Message message) {
	def body = message.getBody(java.lang.String);
	def messageLog = messageLogFactory.getMessageLog(message);
	def counter = getCounter(fileName + 'Counter',message).padLeft(3,' ');
	def logCounter = getCounter('OverallLogCounter',message).padLeft(4,' ');
	if(messageLog != null){
		messageLog.addAttachmentAsString(logCounter + " " + fileName + counter, body, "text/plain");
	};
	
	return message;
}

def Message logTime(java.lang.String fileName, Message message) {
	def messageLog = messageLogFactory.getMessageLog(message);
	def counter = getCounter(fileName + 'CounterTime',message).padLeft(3,' ');
	def logCounter = getCounter('OverallLogCounter',message).padLeft(4,' ');
	Date date = new Date(); 
	if(messageLog != null){
		messageLog.addAttachmentAsString(logCounter + " " +fileName + counter, date.format("YYYY-MM-dd HH:mm:ss.Ms"), "text/plain");
	};
	
	return message;
}

def Message logErrors(Message message) {
    message = logMessage("IBP Commit Errors", message);
	return message;
}

def Message logS4Output(Message message) {
    message = logMessage("S/4 Output", message);
	return message;
}

def Message logS4Input(Message message) {
    message = logMessage("S/4 Input", message);
	return message;
}

def Message logIBPInput(Message message) {
    message = logMessage("IBP Input", message);
	return message;
}

def Message logIBPOutput(Message message) {
    message = logMessage("IBP Output", message);
	return message;
}

def Message logS4OutputTime(Message message) {
    message = logTime("S/4 Output Time", message);
	return message;
}

def Message logS4InputTime(Message message) {
    message = logTime("S/4 Input Time", message);
	return message;
}

def Message logIBPInputTime(Message message) {
    message = logTime("IBP Input Time", message);
	return message;
}

def Message logIBPInputTimeMD(Message message) {
    def masterDataType = message.getHeader("IBPMasterDataType",String);
    message = logTime("IBP Input Time ${masterDataType}", message);
	return message;
}

def Message logIBPOutputTime(Message message) {
    message = logTime("IBP Output Time", message);
	return message;
}

def Message logIBPOutputTimeMD(Message message) {
    def masterDataType = message.getHeader("IBPMasterDataType",String);
    message = logTime("IBP Output Time ${masterDataType}", message);
	return message;
}

def Message logInMappingTime(Message message) {
    message = logTime("In Mapping Time", message);
	return message;
}

def Message logMapStepATime(Message message) {
    message = logTime("Map Step A Time", message);
	return message;
}

def Message logMapStepATimeMD(Message message) {
    def masterDataType = message.getHeader("IBPMasterDataType",String);
    message = logTime("Map Step A Time ${masterDataType}", message);
	return message;
}

def Message logMapStepBTime(Message message) {
    message = logTime("Map Step B Time", message);
	return message;
}

def Message logMapStepBTimeMD(Message message) {
    def masterDataType = message.getHeader("IBPMasterDataType",String);
    message = logTime("Map Step B Time ${masterDataType}", message);
	return message;
}

def Message logMapStepCTime(Message message) {
    message = logTime("Map Step C Time", message);
	return message;
}

def Message logMapStepA(Message message) {
    message = logMessage("Map Step A", message);
	return message;
}

def Message logMapStepB(Message message) {
    message = logMessage("Map Step B", message);
	return message;
}

def Message logMapStepC(Message message) {
    message = logMessage("Map Step C", message);
	return message;
}

def Message logBranchStepA(Message message) {
    message = logMessage("Branch Step A", message);
	return message;
}

def Message logIBPGet(Message message) {
    message = logMessage("IBP Get Interface", message);
	return message;
}

def Message logIBPResult(Message message) {
    message = logMessage("IBP Results", message);
	return message;
}

def Message logLastResponse(Message message) {
    message = logMessage("Last Response", message);
	return message;
}

def Message logErrorResponse(Message message) {
    message = logMessage("Error Response", message);
	return message;
}

def Message createGuid(Message message) {
    String guid = java.util.UUID.randomUUID(); 
    guid = guid.replace("-","").toLowerCase();
    message.setProperty("guid", guid);
    return message;
}

def Message wait(Message message) {
    Thread.sleep(5000);
    return message;
}

def Message setIBPWriteStep(Message message) {
    def step = message.getProperty("IBPStep");
    if(step == null)
      step = 'Handshake'
    else if(step == 'Handshake')
      step = 'WriteData'
    else if(step == 'WriteData') {
      def writeRunning = message.getHeader("writeRunning",String);
      if (writeRunning == 'false')
        step = 'ScheduleProcess';
    }
    else if(step == 'ScheduleProcess')
      step = 'GetProcessStatus';
    else if(step == 'GetProcessStatus') {
      def inProcess = message.getProperty("postProcessInProgress");
      if (inProcess == false)
        step = 'GetResult';
    };
    message.setProperty("IBPStep",step);
    return message;
}

def Message removeHeaderQuotes( Message message) {
	def body = message.getBody(java.lang.String);
	body = body.replaceAll("\"LOCID\",\"PRDID\",\"PERIODID4\",\"TSTFR\",\"ACTUALSQTY\"","LOCID,PRDID,PERIODID4,TSTFR,ACTUALSQTY");
    message.setBody(body);
    return message;	return message;
}

def Message addPackageSizeToOffset(Message message) {
    message.setProperty("IBPOffset", 3000); 
    return message;
}

def Message storeAddressesAndHeaders(Message message) {
    def nodeListCallsWithHeaders = message.getProperty('nodeListCallsWithHeaders');
    def listDirectProcessAddresses = [];
    def mapAddressesWithHeaders = [:];
    def numberAddresses = nodeListCallsWithHeaders.length;
    for (int i = 0; i < numberAddresses; i++) {
        def addressWithHeaders = nodeListCallsWithHeaders.item(i);
        listDirectProcessAddresses.add(addressWithHeaders.nodeName);
        def attrMap = addressWithHeaders.attributes
        def numberHeaders = attrMap.length;
        def headers = [:];
        for (int j = 0; j < numberHeaders; j++) {
            headers[attrMap.item(j).nodeName] = attrMap.item(j).nodeValue;
        }
        mapAddressesWithHeaders[addressWithHeaders.nodeName] = headers;
    }
    message.setProperty('listDirectProcessAddresses',listDirectProcessAddresses);
    message.setProperty('mapAddressesWithHeaders',mapAddressesWithHeaders);
    message.setProperty('numberDirectProcessCalls',numberAddresses);
    return message;
}

def Message setAddressAndHeaders(Message message) {
    def headers = message.getHeaders();
    def callCounter = message.getProperty('callCounter');
    def listDirectProcessAddresses = message.getProperty('listDirectProcessAddresses')
    def directProcessAddress = listDirectProcessAddresses.getAt(callCounter);
    def allDivertingHeaders = message.getProperty('mapAddressesWithHeaders');
    def divertingHeaders = allDivertingHeaders.get(directProcessAddress);
    def overwrittenHeaders = [:];
    def length =  divertingHeaders.size();
    divertingHeaders.each{ 
        def oldEntryValue = headers.get(it.key);
        overwrittenHeaders[it.key] = headers.get(it.key);
        message.setHeader(it.key,it.value);   
    }
    message.setProperty('overwrittenHeaders',overwrittenHeaders);
    message.setHeader('ProcessDirectAddress',directProcessAddress);
    
    return message;
}

def Message restoreDefaultHeaders(Message message) {
    def headers = message.getHeaders();
    def overwrittenHeaders = message.getProperty('overwrittenHeaders');
    overwrittenHeaders.each{ 
        message.setHeader(it.key,it.value);   
    }    
    return message;
}



def Message rememberHeaders(Message message) {
    def headers = message.getHeaders();
    message.setProperty("InputHeaders", headers);
    return message;
}

def Message restoreHeaders(Message message) {
    def headers = message.getHeaders();
    def allowedHeaders = headers.get('AllowedHeaders');
    def inputHeaders = message.getProperty('InputHeaders');
    if (inputHeaders != null) {
        inputHeaders.findAll{it.key ==~ /(?i)($allowedHeaders)/}.each() {  /* case insensitive pattern search */
           message.setHeader(it.key,it.value);
        }
        /* reread, as some headers might be overwritten */
        headers = message.getHeaders();
        message.setProperty('InputHeaders',null);
    }
    
    /* start of creating calculated data */
    String guid = headers.get("IBPTransactionGuid")?:java.util.UUID.randomUUID().toString().replace("-","").toUpperCase();
    message.setHeader("IBPTransactionGuid", guid);
    def plants = (headers.get("Plants")?:'').tokenize(',');
    def plantFilterField = headers.get("PlantFilterField");
    String eqString = '';
    String betweenString = '';
    String plantFilter = '';
    def severalSingletons = false;
    def severalIntervals = false;
    for (plant in plants) {
        def singlePlants = plant.tokenize('-');
        if (singlePlants.size == 1) {
            if (eqString != '') {
                eqString += ' or ';
                severalSingletons = true;
            }
            eqString += "plantFieldName eq '" + singlePlants[0] + "'";
        } 
        else {
            if (betweenString != '') {
                betweenString += ' or ';
                severalIntervals = true;
            }
            betweenString += "plantFieldName ge '" + singlePlants[0] + "' and plantFieldName le '" + singlePlants[1] + "'";
        }
    }
    if (betweenString != '' && eqString != '') {
        plantFilter = '(' + eqString + ' or ' + betweenString + ')';
    } 
    else if (eqString != '') {
        if (severalSingletons == true) 
            plantFilter = "($eqString)";
        else 
            plantFilter = eqString;
    }
    else if (severalIntervals == true) {
        plantFilter = "(" + betweenString + ")";
    }
    else plantFilter = betweenString;
    def plantFilterWithNode = '_ProductPlant/any(p:' + plantFilter.replaceAll("plantFieldName","p/$plantFilterField") + ')';
    plantFilter = plantFilter.replaceAll("plantFieldName",plantFilterField);
    message.setHeader("PlantFilter", plantFilter); 
    message.setProperty("ProductPlantFilterWithNode", plantFilterWithNode);
    message.setProperty("ProductPlantFilter", plantFilter);
    String FieldsPerMDType = '<Fields>';
    String FileNamesPerMDType = '<FileNames>';
    String StagingTablesPerMDType = '<StagingTables>';
    String ColumnList = '<IT_COLUMN_LIST>';
    String iFlowStartTimestamp = headers.get("IFlowStartTimestamp");
    String iFlowStartTimestampDecimalsOnly = iFlowStartTimestamp.replaceAll("[^0-9]","").substring(0,14);
    def SAP_RunId = message.getProperty('SAP_RunId');
    def IBPMasterDataPrefix = headers.get('IBPMasterDataPrefix');
    headers.findAll{ it.key ==~ /IBPFields[A-Z0-9_]+/ }.each { key , value ->
        def MDType = key.substring(9);
        FieldsPerMDType += "<${MDType}>${value}</${MDType}>";
        def FileName = "Prefix_${IBPMasterDataPrefix}_MasterData_${MDType}_CI-RunId_${SAP_RunId}";
        def StagingTable = "SOPMD_STAG_${IBPMasterDataPrefix}${MDType}";
        FileNamesPerMDType += "<${MDType}>${FileName}</${MDType}>";
        StagingTablesPerMDType += "<${MDType}>${StagingTable}</${MDType}>";
        value.tokenize(',').each { fieldName ->
            ColumnList += "<item><FILE_NAME>${FileName}</FILE_NAME><TABLE_NAME>${StagingTable}</TABLE_NAME><COLUMN_NAME>${fieldName}</COLUMN_NAME></item>";
        }
    }
    message.setProperty("IBPFieldsPerMDType", FieldsPerMDType << '</Fields>');
    message.setProperty("IBPFileNamesPerMDType", FileNamesPerMDType << '</FileNames>');
    message.setProperty("IBPStagingTablesPerMDType", StagingTablesPerMDType << '</StagingTables>');
    message.setHeader("IFlowStartTimestampDecimalsOnly",iFlowStartTimestampDecimalsOnly);
    message.setHeader("IBPColumnList", ColumnList << '</IT_COLUMN_LIST>');
    return message;
}

def Message setLogCustomHeaders(Message message) {
	def messageLog = messageLogFactory.getMessageLog(message);
	def headers = message.getHeaders();
	def logCustomHeaders = headers.get("LogCustomHeaders");
	def logCustomProperties = headers.get("LogCustomProperties");
	def logAttachmentHeaders = headers.get("LogAttachmentHeaders");
	if(messageLog != null){
	    if(logCustomHeaders!=null) {
    	    logCustomHeaders.tokenize(',').each() {
    	        setLogCustomHeader(headers, messageLog, it);		
    	    }
	    }
	    if(logCustomProperties!=null) {
    	    logCustomProperties.tokenize(',').each() {
    	        setLogCustomProperty(message, messageLog, it);		
    	    }
	    }
	    if(logAttachmentHeaders!=null) {
    	    logAttachmentHeaders.tokenize(',').each() {
    	        setLogAttachmentHeader(headers, messageLog, it);		
    	    }
	    }
	    
	}
	return message;
}

def void setLogCustomHeader(Map<String,Object> headers, MessageLog messageLog, String headerName) {
    
	def header = headers.get(headerName);		
	if(header!=null){
		messageLog.addCustomHeaderProperty(headerName, header);		
    }
}

def void setLogCustomProperty(Message message, MessageLog messageLog, String propertyName) {
    
	def property = message.getProperty(propertyName);		
	if(property!=null){
		messageLog.addCustomHeaderProperty(propertyName, property);		
    }
}

def void setLogAttachmentHeader(Map<String,Object> headers, MessageLog messageLog, String headerName) {
    
	def header = headers.get(headerName);		
	if(header!=null){
		messageLog.addAttachmentAsString(headerName, header, 'text/plain')	
    }
}

def String subStringRobust(String sourceString, String beginIndex, String endIndex, MappingContext context) {
    String stringNotNull = "";
    if(sourceString != null){
        stringNotNull = sourceString;
    };
    Integer beginInt = beginIndex.toInteger();
    Integer endInt = endIndex.toInteger();
    String stringResult;
    if(stringNotNull.length( ) <= beginIndex) {
      stringResult = '';
    } 
    else {
        if(stringNotNull.length( ) <= endIndex) {
            stringResult = stringNotNull.substring(beginInt);
        } 
        else{
            stringResult = stringNotNull.substring(beginInt,endInt);
        }
    }
    return stringResult;
}

def String subString0to5(String sourceString, MappingContext context) {
    String stringNotNull = "";
    if(sourceString != null){
        stringNotNull = sourceString;
    }
    String stringResult;
    if(stringNotNull.length( ) <= 5) {
      stringResult = stringNotNull;
    } else{
        stringResult = stringNotNull.substring(0,5);
    }
    return stringResult;
}

def String subString5to10(String sourceString, MappingContext context) {
    String stringNotNull = "";
    if(sourceString != null){
        stringNotNull = sourceString;
    }
    String stringResult;
    if(stringNotNull.length( ) <= 5) {
      stringResult = '';
    } else{
        if(stringNotNull.length( ) <= 10) {
            stringResult = stringNotNull.substring(5);
        } else{
            stringResult = stringNotNull.substring(5,10);
        }
    }
    return stringResult;
}

def String subString10to20(String sourceString, MappingContext context) {
    String stringNotNull = "";
    if(sourceString != null){
        stringNotNull = sourceString;
    }
    String stringResult;
    if(stringNotNull.length( ) <= 10) {
      stringResult = '';
    } 
    else{
        if(stringNotNull.length( ) <= 20) {
            stringResult = stringNotNull.substring(10);
        } 
        else{
            stringResult = stringNotNull.substring(10,20);
        }
    }
    return stringResult;
}
