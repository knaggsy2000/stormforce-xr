#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################
# Copyright/License Notice (Modified BSD License)                       #
#########################################################################
#########################################################################
# Copyright (c) 2008-2012, 2014, Daniel Knaggs - 2E0DPK/M6DPK           #
# All rights reserved.                                                  #
#                                                                       #
# Redistribution and use in source and binary forms, with or without    #
# modification, are permitted provided that the following conditions    #
# are met: -                                                            #
#                                                                       #
#   * Redistributions of source code must retain the above copyright    #
#     notice, this list of conditions and the following disclaimer.     #
#                                                                       #
#   * Redistributions in binary form must reproduce the above copyright #
#     notice, this list of conditions and the following disclaimer in   #
#     the documentation and/or other materials provided with the        #
#     distribution.                                                     #
#                                                                       #
#   * Neither the name of the author nor the names of its contributors  #
#     may be used to endorse or promote products derived from this      #
#     software without specific prior written permission.               #
#                                                                       #
#   * This Software is not to be used for safety purposes.              #
#                                                                       #
#   * You agree and abide the Disclaimer for your Boltek products.      #
#                                                                       #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS   #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT     #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR #
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT  #
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT      #
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY #
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT   #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  #
#########################################################################


###################################################
# StormForce XR (XMLRPC) Mini Client              #
###################################################
# Version:     v0.5.0                             #
###################################################


from StringIO import StringIO

from datetime import *
import gzip
import math
import os
import sys
import time
import xmlrpclib
from xml.dom import minidom


#############
# Constants #
#############
CLIENT_VERSION = "0.5.0"

DEBUG_MODE = False
DEMO_MODE = False

LDUNIT_SQUELCH = 0

SSBT_ENABLED = False
STORMFORCEXR_SERVER = "http://127.0.0.1:7397/xmlrpc/"

TRAC_STORM_WIDTH = 0
TRAC_VERSION = "0.0.0"

ZOOM_DISTANCE = 300

XML_SETTINGS_FILE = "sxrminiclient-settings.xml"


###############
# Subroutines #
###############
def cBool(value):
	if DEBUG_MODE:
		log("cBool", "Information", "Starting...")
	
	
	if str(value).lower() == "false" or str(value) == "0":
		return False
		
	elif str(value).lower() == "true" or str(value) == "1":
		return True
		
	else:
		return False

def decompress(data):
	dio = StringIO(data)
	com = gzip.GzipFile(fileobj = dio, mode = "rb")
	
	return com.read()

def exitProgram():
	if DEBUG_MODE:
		log("exitProgram", "Information", "Starting...")
	
	
	global cron_alive
	
	cron_alive = False
	
	sys.exit(0)

def extractDataset(data):
	xmldata = StringIO(decompress(data))
	xmldoc = minidom.parse(xmldata)
	
	myvars = xmldoc.getElementsByTagName("Row")
	
	
	ret = []
	
	for var in myvars:
		row = {}
		
		for key in var.attributes.keys():
			val = str(var.attributes[key].value)
			
			row[str(key)] = val
		
		ret.append(row)
	
	return ret

def getch():
	plat = sys.platform.lower()
	
	if plat == "win32":
		import msvcrt
		
		
		return msvcrt.getch()
		
	else:
		import termios
		
		
		fd = sys.stdin.fileno()
		old = termios.tcgetattr(fd)
		new = termios.tcgetattr(fd)
		new[3] = new[3] & ~termios.ICANON & ~termios.ECHO
		new[6][termios.VMIN] = 1
		new[6][termios.VTIME] = 0
		termios.tcsetattr(fd, termios.TCSANOW, new)
		
		c = None
		
		try:
			c = os.read(fd, 1)
		
		finally:
			termios.tcsetattr(fd, termios.TCSAFLUSH, old)
		
		return c

def ifNoneReturnZero(strinput):
	if DEBUG_MODE:
		log("ifNoneReturnZero", "Information", "Starting...")
	
	
	if strinput is None:
		return 0
	
	else:
		return strinput

def iif(testval, trueval, falseval):
	if DEBUG_MODE:
		log("iif", "Information", "Starting...")
	
	
	if testval:
		return trueval
	
	else:
		return falseval

def log(module, level, message):
	t = datetime.now()
	
	print "%s | SXR/%s()/%s - %s" % (str(t.strftime("%d/%m/%Y %H:%M:%S")), module, level, message)

def main():
	if DEBUG_MODE:
		log("main", "Information", "Starting...")
	
	
	print """
#########################################################################
# Copyright/License Notice (Modified BSD License)                       #
#########################################################################
#########################################################################
# Copyright (c) 2008-2012, 2014, Daniel Knaggs - 2E0DPK/M6DPK           #
# All rights reserved.                                                  #
#                                                                       #
# Redistribution and use in source and binary forms, with or without    #
# modification, are permitted provided that the following conditions    #
# are met: -                                                            #
#                                                                       #
#   * Redistributions of source code must retain the above copyright    #
#     notice, this list of conditions and the following disclaimer.     #
#                                                                       #
#   * Redistributions in binary form must reproduce the above copyright #
#     notice, this list of conditions and the following disclaimer in   #
#     the documentation and/or other materials provided with the        #
#     distribution.                                                     #
#                                                                       #
#   * Neither the name of the author nor the names of its contributors  #
#     may be used to endorse or promote products derived from this      #
#     software without specific prior written permission.               #
#                                                                       #
#   * This Software is not to be used for safety purposes.              #
#                                                                       #
#   * You agree and abide the Disclaimer for your Boltek products.      #
#                                                                       #
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS   #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT     #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR #
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT  #
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, #
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT      #
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, #
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY #
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT   #
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE #
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.  #
#########################################################################
"""
	log("main", "Information", "")
	log("main", "Information", "StormForce XR - Mini Client")
	log("main", "Information", "===========================")
	log("main", "Information", "Checking settings...")
	
	
	if not os.path.exists(XML_SETTINGS_FILE):
		log("main", "Warning", "The XML settings file doesn't exist, create one...")
		
		xmlXRSettingsWrite()
		
		
		log("main", "Information", "The XML settings file has been created using the default settings.  Please edit it and restart the SXR mini client once you're happy with the settings.")
		
		exitProgram()
		
	else:
		log("main", "Information", "Reading XML settings...")
		
		xmlXRSettingsRead()
		
		# This will ensure it will have any new settings in
		if os.path.exists(XML_SETTINGS_FILE + ".bak"):
			os.unlink(XML_SETTINGS_FILE + ".bak")
			
		os.rename(XML_SETTINGS_FILE, XML_SETTINGS_FILE + ".bak")
		xmlXRSettingsWrite()
	
	
	log("main", "Information", "Starting...")
	
	while True:
		try:
			print """
Help
====
r - Receiver status
s - Strike statistics
f - Electric field strength
t - TRAC status
y - TRAC storms
d - Server details
p - Strike persistence
l - Last hour of strikes per minute
q - Quit

Choice:""",
			
			i = getch()
			
			if len(i) == 1:
				print i
				print "\n"
				
				if i == "r":
					# Receiver status
					s = xmlrpclib.ServerProxy(STORMFORCEXR_SERVER)
					data = extractDataset(s.unitStatus().data)
					s = None
					
					
					txt = "Hardware\n=======\n"
					
					for row in data:
						txt += "Hardware:     %s\n" % str(row["Hardware"])
						txt += "Lost:         %s\n" % iif(cBool(row["ReceiverLost"]), "Yes", "No")
						txt += "Close Alarm:  %s\n" % iif(cBool(row["CloseAlarm"]), "Active", "Inactive")
						txt += "Severe Alarm: %s\n" % iif(cBool(row["SevereAlarm"]), "Active", "Inactive")
						txt += "Squelch:      %d\n" % int(row["SquelchLevel"])
						txt += "\n"
					
					print txt
					
				elif i == "s":
					# Strike statistics
					s = xmlrpclib.ServerProxy(STORMFORCEXR_SERVER)
					data = extractDataset(s.strikeCounter().data)
					s = None
					
					
					txt = "Strike Statistics\n=================\n"
					
					for row in data:
						txt += "Strikes: %03d %06d %03d\n" % (int(row["StrikesMinute"]), int(row["StrikesTotal"]), int(row["StrikesOutOfRange"]))
						txt += "Close:   %03d %06d\n" % (int(row["CloseMinute"]), int(row["CloseTotal"]))
						txt += "Noise:   %03d %06d\n" % (int(row["NoiseMinute"]), int(row["NoiseTotal"]))
						txt += "\n"
						break
					
					print txt
					
				elif i == "f":
					# Electric field strength
					s = xmlrpclib.ServerProxy(STORMFORCEXR_SERVER)
					data = extractDataset(s.fieldCounter().data)
					s = None
					
					
					txt = "Electic Field Strength\n======================\n"
					
					for row in data:
						txt += "Strength: %2.2f\n" % float(row["kVm"])
						txt += "\n"
						break
					
					print txt
				
				elif i == "t":
					# TRAC status
					s = xmlrpclib.ServerProxy(STORMFORCEXR_SERVER)
					data = extractDataset(s.tracStatus().data)
					s = None
					
					
					txt = "TRAC\n====\n"
					
					for row in data:
						txt += "TRAC Version:         %s\n" % str(row["Version"])
						txt += "TRAC Active:          %s\n" % iif(cBool(row["Active"]), "Yes", "No")
						txt += "No of Storms:         %d\n" % int(row["NoOfStorms"])
						txt += "Most Active:          %s\n" % str(row["MostActive"])
						txt += "Most Active Distance: %2.2f\n" % float(row["MostActiveDistance"])
						txt += "Closest:              %s\n" % str(row["Closest"])
						txt += "Closest Distance:     %2.2f\n" % float(row["ClosestDistance"])
						txt += "Storm Width:          %d\n" % int(row["Width"])
						txt += "\n"
						break
					
					print txt
					
				elif i == "y":
					# TRAC storms
					s = xmlrpclib.ServerProxy(STORMFORCEXR_SERVER)
					data = extractDataset(s.tracStorms().data)
					s = None
					
					
					txt = "TRAC Storms\n===========\n"
					txt += "X\tY\tXOffset\tYOffset\tName\t\tIntensity\tDistance\n"
					txt += "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
					
					for row in data:
						txt += "%d\t%d\t%d\t%d\t%s\t%d\t\t%2.2f\n" % (int(row["X"]), int(row["Y"]), int(row["XOffset"]), int(row["YOffset"]), str(row["Name"]), int(row["Intensity"]), float(row["Distance"]))
					
					print txt
					
				elif i == "d":
					# Server details
					s = xmlrpclib.ServerProxy(STORMFORCEXR_SERVER)
					data = extractDataset(s.serverDetails().data)
					s = None
					
					
					txt = "Server Details\n==============\n"
					
					for row in data:
						txt += "Server Started:     %s\n" % str(row["ServerStarted"])
						txt += "Server Application: %s\n" % str(row["ServerApplication"])
						txt += "Server Version:     %s\n" % str(row["ServerVersion"])
						txt += "Server Copyright:   %s\n" % str(row["ServerCopyright"])
						txt += "Strike Copyright:   %s\n" % str(row["StrikeCopyright"])
						txt += "\n"
						break
					
					print txt
					
				elif i == "p":
					# Strike persistence
					s = xmlrpclib.ServerProxy(STORMFORCEXR_SERVER)
					data = extractDataset(s.strikePersistence().data)
					s = None
					
					
					txt = "Strike Persistence\n==================\n"
					txt += "Age\tX\tY\tRX\tRY\tDateTime Of Strike\n"
					txt += "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
					
					for row in data:
						txt += "%d\t%d\t%d\t%d\t%d\t%s\n" % (int(row["StrikeAge"]), int(row["X"]), int(row["Y"]), int(row["RelativeX"]), int(row["RelativeY"]), str(row["DateTimeOfStrike"]))
					
					print txt
					
				elif i == "l":
					# Last hour of strikes per minute
					s = xmlrpclib.ServerProxy(STORMFORCEXR_SERVER)
					data = extractDataset(s.lastHourOfStrikesByMinute().data)
					s = None
					
					
					txt = "Last Hour Of Strikes By Minute\n==============================\n"
					txt +="Minute\t\t\tAge\tStrikes\n"
					txt += "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
					
					for row in data:
						txt += "%s\t%d\t%d\n" % (str(row["Minute"]), int(row["StrikeAge"]), int(row["NumberOfStrikes"]))
					
					print txt
					
				elif i == "q":
					break
				
		except KeyboardInterrupt:
			break
			
		except Exception, ex:
			log("main", "Exception", str(ex))
	
	
	log("main", "Information", "Exiting...")
	exitProgram()

def xmlXRSettingsRead():
	if DEBUG_MODE:
		log("xmlXRSettingsRead", "Information", "Starting...")
	
	
	global DEBUG_MODE, STORMFORCEXR_SERVER
	
	
	if os.path.exists(XML_SETTINGS_FILE):
		xmldoc = minidom.parse(XML_SETTINGS_FILE)
		
		myvars = xmldoc.getElementsByTagName("Setting")
		
		for var in myvars:
			for key in var.attributes.keys():
				val = str(var.attributes[key].value)
				
				# Now put the correct values to correct key
				if key == "StormForceXRServer":
					STORMFORCEXR_SERVER = val
					
				elif key == "DebugMode":
					DEBUG_MODE = cBool(val)
					
				else:
					log("xmlXRSettingsRead", "Warning", "XML setting attribute \"%s\" isn't known.  Ignoring..." % key)

def xmlXRSettingsWrite():
	if DEBUG_MODE:
		log("xmlXRSettingsWrite", "Information", "Starting...")
	
	
	if not os.path.exists(XML_SETTINGS_FILE):
		xmloutput = file(XML_SETTINGS_FILE, "w")
		
		
		xmldoc = minidom.Document()
		
		# Create header
		settings = xmldoc.createElement("SXRMiniClient")
		xmldoc.appendChild(settings)
		
		# Write each of the details one at a time, makes it easier for someone to alter the file using a text editor
		var = xmldoc.createElement("Setting")
		var.setAttribute("StormForceXRServer", str(STORMFORCEXR_SERVER))
		settings.appendChild(var)
		
		
		var = xmldoc.createElement("Setting")
		var.setAttribute("DebugMode", str(DEBUG_MODE))
		settings.appendChild(var)
		
		
		# Finally, save to the file
		xmloutput.write(xmldoc.toprettyxml())
		xmloutput.close()


########
# Main #
########
if __name__ == "__main__":
	main()
