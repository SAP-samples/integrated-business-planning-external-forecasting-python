<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="3.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:uuid="java:java.util.UUID" xmlns:cpi="http://sap.com/it/" exclude-result-prefixes="cpi uuid">
	<xsl:output method="xml" encoding="utf-8"/>
	<xsl:param name="SourceReqParam"/> 
	<xsl:param name="CurrentStep"/>
	<xsl:variable name="eqCharacter" select="'='"/> 
				
<xsl:template match="/*">
		<xsl:choose>
			<xsl:when test="$CurrentStep = 'GetMetadata'">
				<request>
					<xsl:attribute name="id"><xsl:value-of select="substring-after($SourceReqParam, $eqCharacter)"></xsl:value-of></xsl:attribute>
					<payloadID>1234</payloadID>
				</request>
			</xsl:when>
			<xsl:otherwise>
				<request>
					<xsl:attribute name="id">10</xsl:attribute>
				</request>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>
</xsl:stylesheet>
