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
# StormForce XR (XMLRPC) Server                   #
###################################################
# Version:     v0.5.0                             #
###################################################

from twisted.web import xmlrpc


###########
# Classes #
###########
class Database():
	def __init__(self, server, database, username, password, debug_mode):
		from danlog import DanLog
		from datetime import datetime
		
		import psycopg2
		
		
		self.datetime = datetime
		self.log = DanLog("Database")
		self.psycopg2 = psycopg2
		
		
		self.DEBUG_MODE = debug_mode
		
		self.POSTGRESQL_DATABASE = database
		self.POSTGRESQL_PASSWORD = password
		self.POSTGRESQL_SERVER = server
		self.POSTGRESQL_USERNAME = username
	
	def addColumnSQLString(self, table, column_name, column_type):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		return """
DO $$
	BEGIN
		BEGIN
			ALTER TABLE %s ADD COLUMN %s %s;
			
		EXCEPTION WHEN duplicate_column THEN
			-- Nothing
		END;
	END
$$
""" % (table, column_name, column_type)
	
	def createTableSQLString(self, table):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		return """
DO $$
	BEGIN
		BEGIN
			CREATE TABLE %s(ID bigserial PRIMARY KEY);
			
		EXCEPTION WHEN duplicate_table THEN
			-- Nothing
		END;
	END
$$
""" % table
	
	def createIndexSQLString(self, name, table, columns, conn = []):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		return """
DO $$
	BEGIN
		IF NOT EXISTS (
				SELECT c.relname
				FROM pg_class c
				INNER JOIN pg_namespace n ON n.oid = c.relnamespace
				WHERE c.relname = lower('%s') AND n.nspname = 'public' AND c.relkind = 'i'
			) THEN
			
			CREATE INDEX %s ON %s (%s);
		END IF;
	END
$$
""" % (name, name, table, columns)
	
	def connectToDatabase(self, conn = []):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		newconn = self.psycopg2.connect(database = self.POSTGRESQL_DATABASE, host = self.POSTGRESQL_SERVER, user = self.POSTGRESQL_USERNAME, password = self.POSTGRESQL_PASSWORD)
		newconn.autocommit = True
		newconn.set_isolation_level(self.psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
		
		if len(conn) > 0:
			for item in conn:
				item = None
			
			del conn
		
		conn.append(newconn)
	
	def danLookup(self, strfield, strtable, strwhere, parameters = (), conn = []):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		if len(conn) >= 1:
			strsql = ""
			
			if strwhere == "":
				strsql = "SELECT %s FROM %s LIMIT 1" % (strfield, strtable)
				
			else:
				strsql = "SELECT %s FROM %s WHERE %s LIMIT 1" % (strfield, strtable, strwhere)
			
			strsql = strsql.replace("?", """%s""") # "?" doesn't seem to work, work around it
			
			
			try:
				cur = conn[0].cursor()
				cur.execute(strsql, parameters)
				
				row = cur.fetchone()
				
				if row is not None:
					row = row[0]
					
				else:
					row = None
				
				cur.close()
				
				return row
				
			except Exception, ex:
				if self.DEBUG_MODE:
					self.log.error(str(ex))
				
				return None
			
		else:
			if self.DEBUG_MODE:
				self.log.warn("Connection has not been passed.")
			
			return None
	
	def disconnectFromDatabase(self, conn = []):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		if len(conn) == 1:
			conn[0].close()
			conn[0] = None
	
	def executeSQLCommand(self, strsql, parameters = (), conn = []):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		if len(conn) >= 1:
			try:
				strsql = strsql.replace("?", """%s""") # "?" doesn't seem to work, work around it
				
				
				cur = conn[0].cursor()
				cur.execute(strsql, parameters)
				cur.close()
				
				return True
				
			except Exception, ex:
				if self.DEBUG_MODE:
					self.log.error(str(ex))
					self.log.error(str(strsql))
				
				return False
			
		else:
			if self.DEBUG_MODE:
				self.log.warn("Connection has not been passed.")
			
			return None
	
	def executeSQLQuery(self, strsql, parameters = (), conn = []):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		if len(conn) >= 1:
			try:
				strsql = strsql.replace("?", """%s""") # "?" doesn't seem to work, work around it
				
				
				cur = conn[0].cursor()
				cur.execute(strsql, parameters)
				
				rows = cur.fetchall()
				
				cur.close()
				
				return rows
				
			except Exception, ex:
				if self.DEBUG_MODE:
					self.log.error(str(ex))
				
				return None
			
		else:
			if self.DEBUG_MODE:
				self.log.warn("Connection has not been passed.")
			
			return None
	
	def sqlDateTime(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		t = self.datetime.now()
		
		return str(t.strftime("%Y/%m/%d %H:%M:%S"))

class EFM100():
	def __init__(self, port, speed, bits, parity, stopbits, trigger_sub = None, debug_mode = False):
		from danlog import DanLog
		
		import threading
		import time
		
		
		self.log = DanLog("EFM100")
		self.serial = None
		self.thread = None
		self.thread_alive = False
		self.threading = threading
		self.time = time
		self.trigger = trigger_sub
		
		self.DEBUG_MODE = debug_mode
		self.EFM_NEGATIVE = "$-"
		self.EFM_POSITIVE = "$+"
		self.SENTENCE_END = "\n"
		self.SENTENCE_START = "$"
		
		
		# Setup everything we need
		self.log.info("Initialising EFM-100...")
		
		self.setupUnit(port, speed, bits, parity, stopbits)
		self.start()
	
	def dispose(self):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		self.thread_alive = False
		
		if self.serial is not None:
			self.serial.close()
			self.serial = None
	
	def rxThread(self):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		buffer = bytearray()
		
		while self.thread_alive:
			extracted = None
			
			
			bytes = self.serial.inWaiting()
			
			if bytes > 0:
				if self.DEBUG_MODE:
					self.log.info("%d bytes are waiting in the serial buffer." % bytes)
				
				
				# Ensure we're thread-safe
				lock = self.threading.Lock()
				
				with lock:
					try:
						buffer.extend(self.serial.read(bytes))
						
					except Exception, ex:
						if self.DEBUG_MODE:
							self.log.error(str(ex))
			
			x = buffer.find(self.SENTENCE_START)
			
			if x <> -1:
				y = buffer.find(self.SENTENCE_END, x)
				
				if y <> -1:
					if self.DEBUG_MODE:
						self.log.info("A sentence has been found in the buffer.")
					
					
					y += len(self.SENTENCE_END)
					
					# There appears to be complete sentence in there, extract it
					extracted = str(buffer[x:y])
			
			
			if extracted is not None:
				# Remove it from the buffer first
				newbuf = str(buffer).replace(extracted, "", 1)
				
				buffer = bytearray()
				buffer.extend(newbuf)
				
				
				# Now trigger any events
				if self.trigger is not None:
					if self.DEBUG_MODE:
						self.log.info("Triggering sentence subroutine...")
					
					
					self.trigger(extracted)
					
				else:
					self.log.warn("Trigger subroutine not defined, cannot raise sentence event.")
			
			self.time.sleep(0.01)
	
	def setupUnit(self, port, speed, bits, parity, stopbits):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		import serial
		
		
		self.serial = serial.Serial()
		self.serial.baudrate = speed
		self.serial.bytesize = bits
		self.serial.parity = parity
		self.serial.port = port
		self.serial.stopbits = stopbits
		self.serial.timeout = 10.
		self.serial.writeTimeout = None
		self.serial.xonxoff = False
		
		self.serial.open()
		
		self.serial.flushInput()
		self.serial.flushOutput()
	
	def start(self):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		self.thread_alive = True
		
		self.thread = self.threading.Thread(target = self.rxThread)
		self.thread.setDaemon(1)
		self.thread.start()

class LD250(EFM100):
	#
	# LD sentence key:
	#
	# <bbb.b> = bearing to strike 0-359.9 degrees
	# <ccc>   = close strike rate 0-999 strikes/minute
	# <ca>    = close alarm status (0 = inactive, 1 = active)
	# <cs>    = checksum
	# <ddd>   = corrected strike distance (0-300 miles)
	# <hhh.h> = current heading from GPS/compass
	# <sa>    = severe alarm status (0 = inactive, 1 = active)
	# <sss>   = total strike rate 0-999 strikes/minute
	# <uuu>   = uncorrected strike distance (0-300 miles)
	def __init__(self, port, speed, bits, parity, stopbits, squelch = 0, trigger_sub = None, debug_mode = False):
		from danlog import DanLog
		
		import threading
		import time
		
		
		self.log = DanLog("LD250")
		self.serial = None
		self.squelch = int(squelch)
		self.thread = None
		self.thread_alive = False
		self.threading = threading
		self.time = time
		self.trigger = trigger_sub
		
		self.DEBUG_MODE = debug_mode
		self.LD_NOISE  = "$WIMLN" # $WIMLN*<cs>
		self.LD_STATUS = "$WIMST" # $WIMST,<ccc>,<sss>,<ca>,<sa>,<hhh.h>*<cs>
		self.LD_STRIKE = "$WIMLI" # $WIMLI,<ddd>,<uuu>,<bbb.b>*<cs>
		self.SENTENCE_END = "\n"
		self.SENTENCE_START = "$"
		
		
		# Setup everything we need
		self.log.info("Initialising LD-250...")
		
		self.setupUnit(port, speed, bits, parity, stopbits)
		self.start()
	
	def setupUnit(self, port, speed, bits, parity, stopbits):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		import serial
		
		
		self.serial = serial.Serial()
		self.serial.baudrate = speed
		self.serial.bytesize = bits
		self.serial.parity = parity
		self.serial.port = port
		self.serial.stopbits = stopbits
		self.serial.timeout = 10.
		self.serial.writeTimeout = None
		self.serial.xonxoff = None
		
		self.serial.open()
		
		self.serial.flushInput()
		self.serial.flushOutput()
		
		
		# Attempt to set the squelch
		self.log.info("Setting squelch...")
		
		
		ok = False
		
		for x in xrange(0, 3):
			self.serial.write("SQ%d\r" % self.squelch)
			self.serial.flush()
			
			o = self.serial.readline().replace("\r", "").replace("\n", "")
			
			if o.startswith(":SQUELCH %d (0-15)" % self.squelch):
				ok = True
				break
		
		if not ok:
			if self.DEBUG_MODE:
				self.log.warn("The squelch doesn't appear to have been set.")

class LD350(EFM100):
	#
	# LD sentence key:
	#
	# <bbb.b> = bearing to strike 0-359.9 degrees
	# <ccc>   = close strike rate 0-999 strikes/minute
	# <ca>    = close alarm status (0 = inactive, 1 = active)
	# <cs>    = checksum
	# <ddd>   = corrected strike distance (0-300 miles)
	# <hhh.h> = current heading from GPS/compass
	# <sa>    = severe alarm status (0 = inactive, 1 = active)
	# <ldns1> = lightning network 1 connection state
	# <ldns2> = lightning network 2 connection state
	# <sss>   = total strike rate 0-999 strikes/minute
	# <uuu>   = uncorrected strike distance (0-300 miles)
	def __init__(self, port, speed, bits, parity, stopbits, squelch = 0, trigger_sub = None, debug_mode = False):
		from danlog import DanLog
		
		import threading
		import time
		
		
		self.log = DanLog("LD350")
		self.serial = None
		self.squelch = int(squelch)
		self.thread = None
		self.thread_alive = False
		self.threading = threading
		self.time = time
		self.trigger = trigger_sub
		
		self.DEBUG_MODE = debug_mode
		self.LD_NOISE  = "$WIMLN" # $WIMLN*<cs>
		self.LD_STATUS = "$WIMSU" # $WIMSU,<ccc>,<sss>,<ca>,<sa>,<ldns1>,<ldns2>,<hhh.h>*<cs>
		self.LD_STRIKE = "$WIMLI" # $WIMLI,<ddd>,<uuu>,<bbb.b>*<cs>
		self.SENTENCE_END = "\n"
		self.SENTENCE_START = "$"
		
		
		# Setup everything we need
		self.log.info("Initialising LD-350...")
		
		self.setupUnit(port, speed, bits, parity, stopbits)
		self.start()
	
	def setupUnit(self, port, speed, bits, parity, stopbits):
		if self.DEBUG_MODE:
			self.log.info("Running...")
		
		
		import serial
		
		
		self.serial = serial.Serial()
		self.serial.baudrate = speed
		self.serial.bytesize = bits
		self.serial.parity = parity
		self.serial.port = port
		self.serial.stopbits = stopbits
		self.serial.timeout = 10.
		self.serial.writeTimeout = None
		self.serial.xonxoff = None
		
		self.serial.open()
		
		self.serial.flushInput()
		self.serial.flushOutput()
		
		
		# Attempt to set the squelch
		self.log.info("Setting squelch...")
		
		
		ok = False
		
		for x in xrange(0, 3):
			self.serial.write("SQ%d\r" % self.squelch)
			self.serial.flush()
			
			o = self.serial.readline().replace("\r", "").replace("\n", "")
			
			if o.startswith(":SQUELCH %d (0-100)" % self.squelch):
				ok = True
				break
		
		if not ok:
			if self.DEBUG_MODE:
				self.log.warn("The squelch doesn't appear to have been set.")

class SXRServer():
	def __init__(self):
		from danlog import DanLog
		from datetime import datetime
		from twisted.internet import defer, reactor
		from twisted.web import resource, server
		from xml.dom import minidom
		
		import math
		import os
		import sys
		import threading
		import time
		
		
		self.db = None # Initialised in main()
		self.cron_alive = False
		self.cron_thread = None
		self.datetime = datetime
		self.efmunit = None
		self.ldunit = None
		self.log = DanLog("SXR")
		self.math = math
		self.minidom = minidom
		self.os = os
		self.sys = sys
		self.threading = threading
		self.time = time
		self.twisted_internet_defer = defer
		self.twisted_internet_reactor = reactor
		self.twisted_web_resource = resource
		self.twisted_web_server = server
		
		
		self.CLOSE_DISTANCE = 15
		
		self.DB_VERSION = 1008
		self.DEBUG_MODE = False
		
		self.EFM100_BITS = 8
		self.EFM100_NAME = "Boltek EFM-100"
		self.EFM100_PARITY = "N"
		self.EFM100_PORT = ""
		self.EFM100_SPEED = 9600
		self.EFM100_STOPBITS = 1
		
		self.LD250_BITS = 8
		self.LD250_NAME = "Boltek LD-250"
		self.LD250_PARITY = "N"
		self.LD250_PORT = "/dev/ttyu0"
		self.LD250_SQUELCH = 0
		self.LD250_SPEED = 9600
		self.LD250_STOPBITS = 1
		self.LD250_USE_UNCORRECTED_STRIKES = False
		
		self.MAP_MATRIX_CENTRE = (300, 300)
		self.MAP_MATRIX_SIZE = (600, 600)
		
		self.POSTGRESQL_DATABASE = "stormforce_xr"
		self.POSTGRESQL_PASSWORD = ""
		self.POSTGRESQL_SERVER = "localhost"
		self.POSTGRESQL_USERNAME = "stormforce"
		
		self.SERVER_COPYRIGHT = "(c)2008-2012, 2014 - Daniel Knaggs"
		self.SERVER_NAME = "StormForce XR"
		self.SERVER_PORT = 7397
		self.SERVER_VERSION = "0.5.0"
		self.STRIKE_COPYRIGHT = "Lightning Data (c) %d - Daniel Knaggs" % self.datetime.now().year
		
		self.TRAC_DETECTION_METHOD = 0
		self.TRAC_SENSITIVITY = 10
		self.TRAC_STORM_WIDTH = 30 # miles
		self.TRAC_UPDATE_TIME = 2 # minutes
		self.TRAC_VERSION = "0.4.0"
		
		self.XML_SETTINGS_FILE = "sxrserver-settings.xml"
	
	def cBool(self, value):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		if str(value).lower() == "false" or str(value) == "0":
			return False
			
		elif str(value).lower() == "true" or str(value) == "1":
			return True
			
		else:
			return False
	
	def cron(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		while self.cron_alive:
			t = self.datetime.now()
			
			if t.second == 0:
				myconn = []
				self.db.connectToDatabase(myconn)
				
				if (t.hour == 0 and t.minute == 0):
					# New day, reset grand counters
					if self.DEBUG_MODE:
						self.log.info("New day has started, resetting grand counters...")
					
					
					if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET CloseTotal = %(N)s, NoiseTotal = %(N)s, StrikesTotal = %(N)s, StrikesOutOfRange = %(N)s", {"N": 0}, myconn):
						if self.DEBUG_MODE:
							self.log.warn("Unable to write the zero noise total into the database.")
				
				# Reset the per minute counters
				if self.DEBUG_MODE:
					self.log.info("New minute has started, resetting minute counters...")
				
				if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET CloseMinute = %(N)s, NoiseMinute = %(N)s, StrikesMinute = %(N)s", {"N": 0}, myconn):
					if self.DEBUG_MODE:
						self.log.warn("Unable to write the zero noise minute into the database.")
				
				
				# Reset counters if excessive
				if self.DEBUG_MODE:
					self.log.info("New minute has started, resetting counters if excessive...")
				
				
				if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET StrikesMinute = %(StrikesMinute)s WHERE StrikesMinute > %(MaxStrikes)s", {"StrikesMinute": 0, "MaxStrikes": 999}, myconn):
					if self.DEBUG_MODE:
						self.log.warn("Unable to write the zero excessive strike minute into the database.")
				
				if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET NoiseMinute = %(NoiseMinute)s WHERE NoiseMinute > %(MaxNoise)s", {"NoiseMinute": 0, "MaxNoise": 999}, myconn):
					if self.DEBUG_MODE:
						self.log.warn("Unable to write the zero excessive noise minute into the database.")
				
				if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET StrikesOutOfRange = %(StrikesOutOfRange)s WHERE StrikesOutOfRange > %(MaxOOR)s", {"StrikesOutOfRange": 0, "MaxOOR": 999}, myconn):
					if self.DEBUG_MODE:
						self.log.warn("Unable to write the zero excessive strike out of range into the database.")
				
				
				if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET CloseTotal = %(CloseTotal)s WHERE CloseTotal > %(MaxClose)s", {"CloseTotal": 0, "MaxClose": 999999}, myconn):
					if self.DEBUG_MODE:
						self.log.warn("Unable to write the zero excessive close total into the database.")
				
				if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET NoiseTotal = %(NoiseTotal)s WHERE NoiseTotal > %(MaxNoise)s", {"NoiseTotal": 0, "MaxNoise": 999999}, myconn):
					if self.DEBUG_MODE:
						self.log.warn("Unable to write the zero excessive noise total into the database.")
				
				if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET StrikesTotal = %(StrikesTotal)s WHERE StrikesTotal > %(MaxStrikes)s", {"StrikesTotal": 0, "MaxStrikes": 999999}, myconn):
					if self.DEBUG_MODE:
						self.log.warn("Unable to write the zero excessive strike total into the database.")
				
				
				self.db.disconnectFromDatabase(myconn)
				
				
				if t.minute % self.TRAC_UPDATE_TIME == 0:
					# See if TRAC finds any thunderstorms
					r = self.threading.Thread(target = self.trac)
					r.setDaemon(1)
					r.start()
			
			
			self.time.sleep(1.)
	
	def exitProgram(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		# Cron
		self.cron_alive = False
		
		
		# EFM-100
		if self.efmunit is not None:
			self.efmunit.dispose()
			self.efmunit = None
		
		# LD-250
		if self.ldunit is not None:
			self.ldunit.dispose()
			self.ldunit = None
		
		
		self.sys.exit(0)
	
	def ifNoneReturnZero(self, strinput):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		if strinput is None:
			return 0
		
		else:
			return strinput
	
	def iif(self, testval, trueval, falseval):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		if testval:
			return trueval
		
		else:
			return falseval
	
	def main(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
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
		self.log.info("")
		self.log.info("StormForce XR - Server")
		self.log.info("======================")
		self.log.info("Checking settings...")
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			self.log.warn("The XML settings file doesn't exist, create one...")
			
			self.xmlXRSettingsWrite()
			
			
			self.log.info("The XML settings file has been created using the default settings.  Please edit it and restart the SXR server once you're happy with the settings.")
			
			exitProgram()
			
		else:
			self.log.info("Reading XML settings...")
			
			self.xmlXRSettingsRead()
			
			# This will ensure it will have any new settings in
			if self.os.path.exists(self.XML_SETTINGS_FILE + ".bak"):
				self.os.unlink(self.XML_SETTINGS_FILE + ".bak")
				
			self.os.rename(self.XML_SETTINGS_FILE, self.XML_SETTINGS_FILE + ".bak")
			self.xmlXRSettingsWrite()
		
		
		self.log.info("Setting up database...")
		self.db = Database(self.POSTGRESQL_SERVER, self.POSTGRESQL_DATABASE, self.POSTGRESQL_USERNAME, self.POSTGRESQL_PASSWORD, self.DEBUG_MODE)
		
		self.updateDatabase()
		
		
		self.log.info("Connecting to LD-250...")
		
		self.ldunit = LD250(self.LD250_PORT, self.LD250_SPEED, self.LD250_BITS, self.LD250_PARITY, self.LD250_STOPBITS, self.LD250_SQUELCH, self.sentenceRX, self.DEBUG_MODE)
		
		
		if self.EFM100_PORT <> "":
			self.log.info("Connecting to EFM-100...")
			
			self.efmunit = EFM100(self.EFM100_PORT, self.EFM100_SPEED, self.EFM100_BITS, self.EFM100_PARITY, self.EFM100_STOPBITS, self.sentenceRX, self.DEBUG_MODE)
		
		
		self.log.info("Starting cron...")
		self.cron_alive = True
		
		cron_thread = self.threading.Thread(target = self.cron)
		cron_thread.setDaemon(1)
		cron_thread.start()
		
		
		self.log.info("Configuring server...")
		
		f = XRXMLRPCFunctions(self.POSTGRESQL_SERVER, self.POSTGRESQL_DATABASE, self.POSTGRESQL_USERNAME, self.POSTGRESQL_PASSWORD, self.DEBUG_MODE)
		xmlrpc.addIntrospection(f)
		
		s = self.twisted_web_resource.Resource()
		s.putChild("xmlrpc", f)
		
		
		self.log.info("Starting server...")
		
		try:
			self.twisted_internet_reactor.listenTCP(self.SERVER_PORT, self.twisted_web_server.Site(s))
			self.twisted_internet_reactor.run()
			
		except KeyboardInterrupt:
			pass
			
		except Exception, ex:
			self.log.error(str(ex))
		
		
		
		self.log.info("Exiting...")
		self.exitProgram()
	
	def sentenceRX(self, sentence):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		myconn = []
		self.db.connectToDatabase(myconn)
		
		sentence = sentence.replace("\r", "").replace("\n", "")
		star_split = sentence.split("*")
		
		
		if sentence.startswith(self.ldunit.LD_NOISE):
			# Noise
			if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET NoiseMinute = NoiseMinute + %(N)s, NoiseTotal = NoiseTotal + %(N)s", {"N": 1}, myconn):
				if self.DEBUG_MODE:
					self.log.warn("Unable to write the noise minute into the database.")
			
		elif sentence.startswith(self.ldunit.LD_STATUS):
			# Status update
			if len(star_split) == 2:
				data_split = star_split[0].split(",")
				
				if len(data_split) == 6:
					close_strikes = int(data_split[1])
					total_strikes = int(data_split[2])
					close_alarm = self.cBool(data_split[3])
					severe_alarm = self.cBool(data_split[4])
					gps_heading = float(data_split[5])
					
					
					# Update the alarm status
					if not self.db.executeSQLCommand("UPDATE tblUnitStatus SET CloseAlarm = %(CloseAlarm)s, SevereAlarm = %(SevereAlarm)s, ReceiverLastDetected = LOCALTIMESTAMP WHERE Hardware = %(Hardware)s", {"CloseAlarm": close_alarm, "SevereAlarm": severe_alarm, "Hardware": self.LD250_NAME}, myconn):
						if self.DEBUG_MODE:
							self.log.warn("Unable to update the database with the unit status.")
			
		elif sentence.startswith(self.ldunit.LD_STRIKE):
			# Strike
			if len(star_split) == 2:
				data_split = star_split[0].split(",")
				
				if len(data_split) == 4:
					strike_distance_corrected = int(data_split[1])
					strike_distance = int(data_split[2])
					strike_angle = float(data_split[3])
					strike_type = "CG"
					strike_polarity = ""
					
					# Use a bit of trignonmetry to get the X,Y co-ords
					#
					#        ^
					#       /|
					#      / |
					#  H  /  | O
					#    /   |
					#   /    |
					#  / )X  |
					# /-------
					#     A
					new_distance = 0.
					
					if self.LD250_USE_UNCORRECTED_STRIKES:
						new_distance = strike_distance
						
					else:
						new_distance = strike_distance_corrected
					
					o = self.math.sin(self.math.radians(strike_angle)) * float(new_distance)
					a = self.math.cos(self.math.radians(strike_angle)) * float(new_distance)
					
					
					if not self.db.executeSQLCommand("INSERT INTO tblStrikes(X, Y, DateTimeOfStrike, CorrectedStrikeDistance, UncorrectedStrikeDistance, StrikeAngle, StrikeType, StrikePolarity) VALUES(%(X)s, %(Y)s, LOCALTIMESTAMP, %(CorrectedStrikeDistance)s, %(UncorrectedStrikeDistance)s, %(StrikeAngle)s, %(StrikeType)s, %(StrikePolarity)s)", {"X": int(self.MAP_MATRIX_CENTRE[0] + o), "Y": int(self.MAP_MATRIX_CENTRE[1] + -a), "CorrectedStrikeDistance": strike_distance_corrected, "UncorrectedStrikeDistance": strike_distance, "StrikeAngle": strike_angle, "StrikeType": "CG", "StrikePolarity": ""}, myconn):
						if self.DEBUG_MODE:
							self.log.warn("Unable to write the strike into the database.")
					
					
					if new_distance <= 300.:
						if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET StrikesMinute = StrikesMinute + %(N)s, StrikesTotal = StrikesTotal + %(N)s", {"N": 1}, myconn):
							if self.DEBUG_MODE:
								self.log.warn("Unable to write the strike into the database.")
						
						
						if new_distance <= self.CLOSE_DISTANCE:
							if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET CloseMinute = CloseMinute + %(N)s, CloseTotal = CloseTotal + %(N)s", {"N": 1}, myconn):
								if self.DEBUG_MODE:
									self.log.warn("Unable to write the close strike into the database.")
						
					else:
						if not self.db.executeSQLCommand("UPDATE tblStrikeCounter SET StrikesOutOfRange = StrikesOutOfRange + %(N)s", {"N": 1}, myconn):
							if self.DEBUG_MODE:
								self.log.warn("Unable to write the out of range strike into the database.")
			
		else:
			if self.efmunit is not None:
				if sentence.startswith(self.efmunit.EFM_POSITIVE) or sentence.startswith(self.efmunit.EFM_NEGATIVE):
					data_split = star_split[0].split(",")
					
					if len(data_split) == 2:
						electric_field_level = data_split[0]
						fault_present = self.cBool(data_split[1])
						
						
						efl = float(electric_field_level.replace("$", ""))
						
						if not self.db.executeSQLCommand("INSERT INTO tblElectricFieldStrength(DateTimeOfMeasurement, kVm) VALUES(LOCALTIMESTAMP, %(kVm)s)", {"kVm": efl}, myconn):
							if self.DEBUG_MODE:
								self.log.warn("Failed to write out the field strength to the database.")
						
						if not self.db.executeSQLCommand("UPDATE tblUnitStatus SET SevereAlarm = %(SevereAlarm)s, ReceiverLastDetected = LOCALTIMESTAMP WHERE Hardware = %(Hardware)s", {"SevereAlarm": fault_present, "Hardware": self.EFM100_NAME}, myconn):
							if self.DEBUG_MODE:
								self.log.warn("Unable to update the database with the unit status.")
		
		self.db.disconnectFromDatabase(myconn)
	
	def trac(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		# Moved to new class
		try:
			t = TRAC(self.POSTGRESQL_SERVER, self.POSTGRESQL_DATABASE, self.POSTGRESQL_USERNAME, self.POSTGRESQL_PASSWORD, self.TRAC_DETECTION_METHOD, self.DEBUG_MODE)
			t.run()
			t = None
			
		except Exception, ex:
			self.log.error("An error occurred while running TRAC.")
			self.log.error(ex)
			
		finally:
			if self.DEBUG_MODE:
				self.log.info("Completed.")
	
	def updateDatabase(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		myconn = []
		self.db.connectToDatabase(myconn)
		
		
		##########
		# Tables #
		##########
		if self.DEBUG_MODE:
			self.log.info("Creating tables...")
		
		
		# tblElectricFieldStrength
		self.log.info("TABLE: tblElectricFieldStrength")
		self.db.executeSQLCommand(self.db.createTableSQLString("tblElectricFieldStrength"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblElectricFieldStrength", "DateTimeOfMeasurement", "timestamp"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblElectricFieldStrength", "kVm", "decimal(4,2)"), conn = myconn)
		
		
		# tblServerDetails
		self.log.info("TABLE: tblServerDetails")
		self.db.executeSQLCommand("DROP TABLE IF EXISTS tblServerDetails CASCADE", conn = myconn)
		self.db.executeSQLCommand("CREATE TABLE tblServerDetails(ID bigserial PRIMARY KEY)", conn = myconn) # MEMORY
		self.db.executeSQLCommand("ALTER TABLE tblServerDetails ADD COLUMN ServerStarted timestamp", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblServerDetails ADD COLUMN ServerApplication varchar(20)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblServerDetails ADD COLUMN ServerCopyright varchar(100)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblServerDetails ADD COLUMN ServerVersion varchar(8)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblServerDetails ADD COLUMN StrikeCopyright varchar(100)", conn = myconn)
		
		self.db.executeSQLCommand("INSERT INTO tblServerDetails(ServerStarted, ServerApplication, ServerCopyright, ServerVersion, StrikeCopyright) VALUES(LOCALTIMESTAMP, %(ServerApplication)s, %(ServerCopyright)s, %(ServerVersion)s, %(StrikeCopyright)s)", {"ServerApplication": self.SERVER_NAME, "ServerCopyright": self.SERVER_COPYRIGHT, "ServerVersion": self.SERVER_VERSION, "StrikeCopyright": self.STRIKE_COPYRIGHT}, myconn)
		
		
		# tblStrikeCounter
		self.log.info("TABLE: tblStrikeCounter")
		self.db.executeSQLCommand("DROP TABLE IF EXISTS tblStrikeCounter CASCADE", conn = myconn)
		self.db.executeSQLCommand("CREATE TABLE tblStrikeCounter(ID bigserial PRIMARY KEY)", conn = myconn) # MEMORY
		self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN CloseMinute int", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN CloseTotal int", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN NoiseMinute int", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN NoiseTotal int", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN StrikesMinute int", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN StrikesTotal int", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblStrikeCounter ADD COLUMN StrikesOutOfRange int", conn = myconn)
		
		self.db.executeSQLCommand("INSERT INTO tblStrikeCounter(CloseMinute, CloseTotal, NoiseMinute, NoiseTotal, StrikesMinute, StrikesTotal, StrikesOutOfRange) VALUES(%(N)s, %(N)s, %(N)s, %(N)s, %(N)s, %(N)s, %(N)s)", {"N": 0}, myconn)
		
		
		# tblStrikes
		self.log.info("TABLE: tblStrikes")
		self.db.executeSQLCommand(self.db.createTableSQLString("tblStrikes"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblStrikes", "X", "smallint"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblStrikes", "Y", "smallint"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblStrikes", "DateTimeOfStrike", "timestamp"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblStrikes", "CorrectedStrikeDistance", "decimal(6,3)"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblStrikes", "UncorrectedStrikeDistance", "decimal(6,3)"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblStrikes", "StrikeType", "varchar(2)"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblStrikes", "StrikePolarity", "varchar(1)"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblStrikes", "StrikeAngle", "decimal(4,1)"), conn = myconn)
		
		
		# tblSystem
		self.log.info("TABLE: tblSystem")
		self.db.executeSQLCommand(self.db.createTableSQLString("tblSystem"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblSystem", "DatabaseVersion", "int"), conn = myconn)
		
		rowcount = int(self.ifNoneReturnZero(self.db.danLookup("COUNT(ID)", "tblSystem", "", conn = myconn)))
		
		if rowcount == 0:
			self.db.executeSQLCommand("INSERT INTO tblSystem(DatabaseVersion) VALUES(%(DatabaseVersion)s)", {"DatabaseVersion": 0}, myconn)
		
		
		# tblTRACDetails
		self.log.info("TABLE: tblTRACDetails")
		self.db.executeSQLCommand(self.db.createTableSQLString("tblTRACDetails"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACDetails", "HeaderID", "bigint"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACDetails", "DateTimeOfReading", "timestamp"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACDetails", "DateTimeOfLastStrike", "timestamp"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACDetails", "CurrentStrikeRate", "int"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACDetails", "TotalStrikes", "int"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACDetails", "Intensity", "varchar(12)"), conn = myconn)
		
		
		# tblTRACGrid
		self.log.info("TABLE: tblTRACGrid")
		self.db.executeSQLCommand(self.db.createTableSQLString("tblTRACGrid"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACGrid", "X", "smallint"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACGrid", "Y", "smallint"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACGrid", "Counter", "int"), conn = myconn)
		
		rowcount = int(self.ifNoneReturnZero(self.db.danLookup("COUNT(ID)", "tblTRACGrid", "", conn = myconn)))
		
		if rowcount < 360000:
			self.log.warn("The TRAC grid hasn't been populated (or is invalid), this may take a while to build (%d)..." % rowcount)
			
			
			self.db.executeSQLCommand("""
DO $$
	BEGIN
		DELETE FROM tblTRACGrid;
		
		FOR y IN 0..%d LOOP
			FOR x IN 0..%d LOOP
				INSERT INTO tblTRACGrid(X, Y, Counter) VALUES(x, y, 0);
			END LOOP;
		END LOOP;
	END
$$
""" % (self.MAP_MATRIX_SIZE[1] - 1, self.MAP_MATRIX_SIZE[0] - 1), conn = myconn)
			
		else:
			self.db.executeSQLCommand("UPDATE tblTRACGrid SET Counter = 0 WHERE Counter <> 0", conn = myconn)
		
		
		# tblTRACHeader
		self.log.info("TABLE: tblTRACHeader")
		self.db.executeSQLCommand(self.db.createTableSQLString("tblTRACHeader"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACHeader", "GID", "varchar(40)"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACHeader", "CRC32", "varchar(8)"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACHeader", "DateTimeOfDiscovery", "timestamp"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACHeader", "Bearing", "decimal(10,5)"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACHeader", "Distance", "decimal(10,5)"), conn = myconn)
		self.db.executeSQLCommand(self.db.addColumnSQLString("tblTRACHeader", "DetectionMethod", "smallint"), conn = myconn)
		
		
		# tblTRACStatus
		self.log.info("TABLE: tblTRACStatus")
		self.db.executeSQLCommand("DROP TABLE IF EXISTS tblTRACStatus", conn = myconn)
		self.db.executeSQLCommand("CREATE TABLE tblTRACStatus(ID bigserial PRIMARY KEY)", conn = myconn) # MEMORY
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN Version varchar(6)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN DetectionMethod smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN Active boolean", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN NoOfStorms smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN MostActive varchar(14)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN MostActiveDistance decimal(10,5)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN Closest varchar(14)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN ClosestDistance decimal(10,5)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStatus ADD COLUMN Width smallint", conn = myconn)
		
		self.db.executeSQLCommand("INSERT INTO tblTRACStatus(Version, DetectionMethod, Active, NoOfStorms, MostActive, MostActiveDistance, Closest, ClosestDistance, Width) VALUES(%(Version)s, %(DetectionMethod)s, %(Active)s, %(NoOfStorms)s, %(MostActive)s, %(MostActiveDistance)s, %(Closest)s, %(ClosestDistance)s, %(Width)s)", {"Version": self.TRAC_VERSION, "DetectionMethod": self.TRAC_DETECTION_METHOD, "Active": False, "NoOfStorms": 0, "MostActive": "", "MostActiveDistance": 0, "Closest": "", "ClosestDistance": 0, "Width": self.TRAC_STORM_WIDTH}, myconn)
		
		
		# tblTRACStorms
		self.log.info("TABLE: tblTRACStorms")
		self.db.executeSQLCommand("DROP TABLE IF EXISTS tblTRACStorms CASCADE", conn = myconn)
		self.db.executeSQLCommand("CREATE TABLE tblTRACStorms(ID bigserial PRIMARY KEY)", conn = myconn) # MEMORY
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN X smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN Y smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN XOffset smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN YOffset smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN Name varchar(14)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN Intensity smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblTRACStorms ADD COLUMN Distance decimal(10,5)", conn = myconn)
		
		
		# tblUnitStatus
		self.log.info("TABLE: tblUnitStatus")
		self.db.executeSQLCommand("DROP TABLE IF EXISTS tblUnitStatus CASCADE", conn = myconn)
		self.db.executeSQLCommand("CREATE TABLE tblUnitStatus(ID bigserial PRIMARY KEY)", conn = myconn) # MEMORY
		self.db.executeSQLCommand("ALTER TABLE tblUnitStatus ADD COLUMN Hardware varchar(20)", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblUnitStatus ADD COLUMN SquelchLevel smallint", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblUnitStatus ADD COLUMN UseUncorrectedStrikes boolean", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblUnitStatus ADD COLUMN CloseAlarm boolean", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblUnitStatus ADD COLUMN SevereAlarm boolean", conn = myconn)
		self.db.executeSQLCommand("ALTER TABLE tblUnitStatus ADD COLUMN ReceiverLastDetected timestamp", conn = myconn)
		
		self.db.executeSQLCommand("INSERT INTO tblUnitStatus(Hardware, SquelchLevel, UseUncorrectedStrikes, CloseAlarm, SevereAlarm, ReceiverLastDetected) VALUES(%(Hardware)s, %(SquelchLevel)s, %(UseUncorrectedStrikes)s, %(CloseAlarm)s, %(SevereAlarm)s, NULL)", {"Hardware": self.LD250_NAME, "SquelchLevel": self.LD250_SQUELCH, "UseUncorrectedStrikes": self.LD250_USE_UNCORRECTED_STRIKES, "CloseAlarm": False, "SevereAlarm": False}, myconn)
		
		if self.EFM100_PORT <> "":
			self.db.executeSQLCommand("INSERT INTO tblUnitStatus(Hardware, SquelchLevel, UseUncorrectedStrikes, CloseAlarm, SevereAlarm, ReceiverLastDetected) VALUES(%(Hardware)s, %(SquelchLevel)s, %(UseUncorrectedStrikes)s, %(CloseAlarm)s, %(SevereAlarm)s, NULL)", {"Hardware": self.EFM100_NAME, "SquelchLevel": 0, "UseUncorrectedStrikes": False, "CloseAlarm": False, "SevereAlarm": False}, myconn)
		
		
		
		#########
		# Views #
		#########
		if self.DEBUG_MODE:
			self.log.info("Creating views...")
		
		
		self.db.executeSQLCommand("DROP VIEW IF EXISTS vwStrikesPersistence CASCADE", conn = myconn)
		self.db.executeSQLCommand("DROP VIEW IF EXISTS vwStrikesSummaryByMinute CASCADE", conn = myconn)
		self.db.executeSQLCommand("DROP VIEW IF EXISTS vwTRACPersistence CASCADE", conn = myconn)
		self.db.executeSQLCommand("DROP VIEW IF EXISTS vwTRACStrikesPeak CASCADE", conn = myconn)
		self.db.executeSQLCommand("DROP VIEW IF EXISTS vwUnitStatus CASCADE", conn = myconn)
		
		self.log.info("VIEW: vwStrikesPersistence")
		self.db.executeSQLCommand("""CREATE VIEW vwStrikesPersistence AS
SELECT ID, X, Y, DateTimeOfStrike, CAST(EXTRACT(epoch from (LOCALTIMESTAMP - DateTimeOfStrike)) AS smallint) AS StrikeAge
FROM tblStrikes
WHERE DateTimeOfStrike >= LOCALTIMESTAMP - INTERVAL '1 HOUR' AND DateTimeOfStrike >= (SELECT ServerStarted FROM tblServerDetails LIMIT 1)""", conn = myconn)
		
		self.log.info("VIEW: vwStrikesSummaryByMinute")
		self.db.executeSQLCommand("""CREATE VIEW vwStrikesSummaryByMinute AS
SELECT CAST(to_char(DateTimeOfStrike, 'YYYY/MM/DD HH24:MI:00') AS timestamp) AS Minute, ((CAST(EXTRACT(epoch from (CAST(to_char(LOCALTIMESTAMP, 'YYYY/MM/DD HH24:MI:00') AS timestamp) - CAST(to_char(DateTimeOfStrike, 'YYYY/MM/DD HH24:MI:00') AS timestamp))) AS smallint)) / 60) AS StrikeAge, COUNT(ID) AS NumberOfStrikes
FROM vwStrikesPersistence
GROUP BY CAST(to_char(DateTimeOfStrike, 'YYYY/MM/DD HH24:MI:00') AS timestamp), ((CAST(EXTRACT(epoch from (CAST(to_char(CAST(to_char(LOCALTIMESTAMP, 'YYYY/MM/DD HH24:MI:00') AS timestamp), 'YYYY/MM/DD HH24:MI:00') AS timestamp) - CAST(to_char(DateTimeOfStrike, 'YYYY/MM/DD HH24:MI:00') AS timestamp))) AS smallint)) / 60)""", conn = myconn)
		
		self.log.info("VIEW: vwTRACPersistence")
		self.db.executeSQLCommand("""CREATE VIEW vwTRACPersistence AS
SELECT ID, X, Y, DateTimeOfStrike, EXTRACT(epoch from (LOCALTIMESTAMP - DateTimeOfStrike)) AS StrikeAge
FROM tblStrikes
WHERE DateTimeOfStrike >= LOCALTIMESTAMP - INTERVAL '30 MINUTES' AND DateTimeOfStrike >= (SELECT ServerStarted FROM tblServerDetails LIMIT 1)""", conn = myconn)
		
		self.log.info("VIEW: vwTRACStrikesPeak")
		self.db.executeSQLCommand("""CREATE VIEW vwTRACStrikesPeak AS
SELECT COUNT(ID) AS StrikeCount, CAST(to_char(DateTimeOfStrike, 'YYYY/MM/DD HH24:MI:00') AS timestamp) AS PeakTime, MIN(X) AS MinX, MIN(Y) AS MinY
FROM vwTRACPersistence
GROUP BY CAST(to_char(DateTimeOfStrike, 'YYYY/MM/DD HH24:MI:00') AS timestamp)""", conn = myconn)
		
		self.log.info("VIEW: vwUnitStatus")
		self.db.executeSQLCommand("""CREATE VIEW vwUnitStatus AS
SELECT ID, Hardware, SquelchLevel, UseUncorrectedStrikes, CloseAlarm, SevereAlarm, ReceiverLastDetected, (CASE WHEN ReceiverLastDetected IS NULL THEN TRUE ELSE (CASE WHEN EXTRACT(epoch from (LOCALTIMESTAMP - ReceiverLastDetected)) >= 5 THEN TRUE ELSE FALSE END) END) AS ReceiverLost
FROM tblUnitStatus""", conn = myconn)
		
		
		
		###########
		# Indices #
		###########
		if self.DEBUG_MODE:
			self.log.info("Indices...")
		
		self.log.info("INDEX: tblElectricFieldStrength_DateTimeOfMeasurement")
		self.db.executeSQLCommand(self.db.createIndexSQLString("tblElectricFieldStrength_DateTimeOfMeasurement", "tblElectricFieldStrength", "DateTimeOfMeasurement"), conn = myconn)
		
		
		self.log.info("INDEX: tblStrikes_X_Y")
		self.db.executeSQLCommand(self.db.createIndexSQLString("tblStrikes_X_Y", "tblStrikes", "X, Y"), conn = myconn)
		
		self.log.info("INDEX: tblStrikes_DateTimeOfStrike")
		self.db.executeSQLCommand(self.db.createIndexSQLString("tblStrikes_DateTimeOfStrike", "tblStrikes", "DateTimeOfStrike"), conn = myconn)
		
		
		self.log.info("INDEX: tblTRACDetails_HeaderID")
		self.db.executeSQLCommand(self.db.createIndexSQLString("tblTRACDetails_HeaderID", "tblTRACDetails", "HeaderID"), conn = myconn)
		
		
		self.log.info("INDEX: tblTRACGrid_X_Y")
		self.db.executeSQLCommand(self.db.createIndexSQLString("tblTRACGrid_X_Y", "tblTRACGrid", "X, Y"), conn = myconn)
		
		
		
		#############
		# Functions #
		#############
		if self.DEBUG_MODE:
			self.log.info("Functions...")
		
		self.log.info("FUNCTION: fnTRAC")
		s = """
CREATE OR REPLACE FUNCTION fnTRAC(detectionmethod INT) RETURNS INT AS $$
DECLARE
	strikes_header RECORD;
	strikes_details RECORD;
	trend RECORD;
	
	TRAC_FULL SMALLINT;
	TRAC_HALF SMALLINT;
	TRAC_QUARTER SMALLINT;
	TRAC_SENSITIVITY SMALLINT;
	TRAC_UPDATE_TIME SMALLINT;
	
	x_offset INT;
	y_offset INT;
	offset_x INT;
	offset_y INT;
	
	top_left BIGINT;
	top_right BIGINT;
	bottom_left BIGINT;
	bottom_right BIGINT;
	
	tl INT;
	tr INT;
	bl INT;
	br INT;
	
	new_x INT;
	new_y INT;
	
	o INT;
	a INT;
	
	deg_offset DECIMAL(10,5);
	degx DECIMAL(10,5);
	deg DECIMAL(10,5);
	distance DECIMAL(10,5);
	abs_distance DECIMAL(10,5);
	
	total_count BIGINT;
	
	first_recorded_activity TIMESTAMP;
	last_recorded_activity TIMESTAMP;
	
	current_strike_rate BIGINT;
	peak_strike_rate BIGINT;
	
	guid VARCHAR;
	guid_ss INT;
	crc32 VARCHAR;
	
	intensity_class VARCHAR;
	intensity_trend VARCHAR;
	intensity_trend_symbol VARCHAR;
	
	rises INT;
	falls INT;
	
	average_strike_count DECIMAL(10,5);
	
	diff DECIMAL(10,5);
	
	amount DECIMAL(10,5);
	
	current_name VARCHAR;
	
	tracid BIGINT;
	
	trac_most_active VARCHAR;
	trac_most_active_distance DECIMAL(10,5);
	
	trac_closest VARCHAR;
	trac_closest_distance DECIMAL(10,5);

	corrected_strikes_in_sector BIGINT;
	strikes_in_sector BIGINT;
	storms_found INT;
BEGIN
	-- Populate the variables
	x_offset := 0;
	y_offset := 0;
	storms_found := 0;
	trac_closest_distance := 300.;
	trac_most_active_distance := 0.;
	
	
	-- Populate the "constants"
	TRAC_FULL := (SELECT Width FROM tblTRACStatus LIMIT 1);
	
	IF TRAC_FULL %% 2 > 0 THEN
		TRAC_FULL := TRAC_FULL - 1;
	END IF;
	
	TRAC_HALF := TRAC_FULL / 2;
	TRAC_QUARTER := TRAC_HALF / 2;
	TRAC_SENSITIVITY := 5;
	TRAC_UPDATE_TIME := 1;
	
	RAISE NOTICE 'TRAC detection method is %%', detectionmethod;
	RAISE NOTICE 'TRAC_FULL is %%', TRAC_FULL;
	RAISE NOTICE 'TRAC_HALF is %%', TRAC_HALF;
	RAISE NOTICE 'TRAC_QUARTER is %%', TRAC_QUARTER;
	RAISE NOTICE 'TRAC_SENSITIVITY is %%', TRAC_SENSITIVITY;
	
	
	-- Reset any tables
	UPDATE tblTRACGrid SET Counter = 0 WHERE Counter <> 0;
	UPDATE tblTRACStatus SET Active = FALSE, NoOfStorms = 0, MostActive = '', MostActiveDistance = 0, Closest = '', ClosestDistance = 0;
	
	DELETE FROM tblTRACStorms;
	
	
	-- Get the unique areas where the strikes are
	DROP TABLE IF EXISTS tmpStrikesHeader;
	
	IF detectionmethod = 0 THEN
		-- Fixed-grid
		CREATE TEMPORARY TABLE tmpStrikesHeader AS
			SELECT div(X, TRAC_FULL) * TRAC_FULL AS X, div(Y, TRAC_FULL) * TRAC_FULL AS Y
			FROM vwTRACPersistence
			GROUP BY div(X, TRAC_FULL) * TRAC_FULL, div(Y, TRAC_FULL) * TRAC_FULL
			HAVING COUNT(ID) >= TRAC_SENSITIVITY
		;
		
	ELSIF detectionmethod = 1 THEN
		-- Freestyle-grid
		CREATE TEMPORARY TABLE tmpStrikesHeader AS
			SELECT DISTINCT X, Y
			FROM vwTRACPersistence
			GROUP BY X, Y
		;
		
	ELSE
		RAISE EXCEPTION 'Unknown TRAC detection method %%.', detectionmethod;
	END IF;
	
	
	FOR strikes_header	IN	SELECT X, Y
							FROM tmpStrikesHeader
							ORDER BY X, Y
						LOOP
		
		IF detectionmethod = 0 THEN
			strikes_in_sector = COALESCE((	SELECT COUNT(ID) - (SELECT SUM(Counter) FROM tblTRACGrid WHERE (X >= strikes_header.X AND X < strikes_header.X + TRAC_FULL) AND (Y >= strikes_header.Y AND Y < strikes_header.Y + TRAC_FULL)) AS NoOfStrikes
											FROM vwTRACPersistence
											WHERE (X >= strikes_header.X AND X < strikes_header.X + TRAC_FULL) AND (Y >= strikes_header.Y AND Y < strikes_header.Y + TRAC_FULL)
								), 0);
			
		ELSIF detectionmethod = 1 THEN
			strikes_in_sector = COALESCE((	SELECT COUNT(ID) - (SELECT SUM(Counter) FROM tblTRACGrid WHERE (X >= strikes_header.X - TRAC_HALF AND X < strikes_header.X + TRAC_HALF) AND (Y >= strikes_header.Y - TRAC_HALF AND Y < strikes_header.Y + TRAC_HALF)) AS NoOfStrikes
											FROM vwTRACPersistence
											WHERE (X >= strikes_header.X - TRAC_HALF AND X < strikes_header.X + TRAC_HALF) AND (Y >= strikes_header.Y - TRAC_HALF AND Y < strikes_header.Y + TRAC_HALF)
								), 0);
		END IF;
		
		IF strikes_in_sector = 0 THEN
			RAISE NOTICE 'WARN: Zero strikes where found in the sector.';
		END IF;
		
		corrected_strikes_in_sector := strikes_in_sector;
		
		RAISE NOTICE 'INFO: %% strikes were found within the vicinity of (%%, %%).', strikes_in_sector, strikes_header.X, strikes_header.Y;
		
		
		IF strikes_in_sector >= TRAC_SENSITIVITY THEN
			-- This "sector" may have a storm in it, dig deeper...
			DROP TABLE IF EXISTS tmpStrikesDetails;
			
			IF detectionmethod = 0 THEN
				CREATE TEMPORARY TABLE tmpStrikesDetails AS
					SELECT COUNT(ID) AS NoOfStrikes, (SELECT Counter FROM tblTRACGrid WHERE X = vwTRACPersistence.X AND Y = vwTRACPersistence.Y) AS TrackedStrikes, X, Y
					FROM vwTRACPersistence
					WHERE (X >= strikes_header.X AND X < strikes_header.X + TRAC_FULL) AND (Y >= strikes_header.Y AND Y < strikes_header.Y)
					GROUP BY X, Y
				;
				
			ELSIF detectionmethod = 1 THEN
				CREATE TEMPORARY TABLE tmpStrikesDetails AS
					SELECT COUNT(ID) AS NoOfStrikes, (SELECT Counter FROM tblTRACGrid WHERE X = vwTRACPersistence.X AND Y = vwTRACPersistence.Y) AS TrackedStrikes, X, Y
					FROM vwTRACPersistence
					WHERE (X >= strikes_header.X - TRAC_HALF AND X < strikes_header.X + TRAC_HALF) AND (Y >= strikes_header.Y - TRAC_HALF AND Y < strikes_header.Y + TRAC_HALF)
					GROUP BY X, Y
				;
			END IF;
			
			
			FOR strikes_details	IN	SELECT NoOfStrikes, TrackedStrikes, X, Y
									FROM tmpStrikesDetails
									ORDER BY X, Y
								LOOP
				
				corrected_strikes_in_sector := corrected_strikes_in_sector - strikes_details.TrackedStrikes;
				
				IF corrected_strikes_in_sector >= TRAC_SENSITIVITY THEN
					UPDATE tblTRACGrid SET Counter = Counter + (strikes_details.NoOfStrikes - strikes_details.TrackedStrikes) WHERE X = strikes_details.X AND Y = strikes_details.Y;
				END IF;
			END LOOP;
			
			DROP TABLE IF EXISTS tmpStrikesDetails;
			
			
			IF corrected_strikes_in_sector >= TRAC_SENSITIVITY THEN
				RAISE NOTICE 'INFO: Deep scan found a storm in (%%, %%).', strikes_header.X, strikes_header.Y;
				
				
				x_offset := 0;
				y_offset := 0;
				storms_found := storms_found + 1;
				
				
				-- Prepare to register the storm
				IF detectionmethod = 0 THEN
					-- No offset required
					offset_x := strikes_header.X;
					offset_y := strikes_header.Y;
					
				ELSIF detectionmethod = 1 THEN
					-- Apply the offset since we search *around* the strike
					offset_x := strikes_header.X - TRAC_HALF;
					offset_y := strikes_header.Y - TRAC_HALF;
				END IF;
				
				top_left := 	(	SELECT COUNT(ID) AS OffsetCount
								FROM vwTRACPersistence
								WHERE (X >= offset_x AND X < offset_x + TRAC_HALF) AND (Y >= offset_y AND Y < offset_y + TRAC_HALF)
							);
				top_right := (	SELECT COUNT(ID) AS OffsetCount
								FROM vwTRACPersistence
								WHERE (X >= offset_x + TRAC_HALF AND X < offset_x + TRAC_FULL) AND (Y >= offset_y AND Y < offset_y + TRAC_HALF)
							);
				bottom_left := (	SELECT COUNT(ID) AS OffsetCount
									FROM vwTRACPersistence
									WHERE (X >= offset_x AND X < offset_x + TRAC_HALF) AND (Y >= offset_y + TRAC_HALF AND Y < offset_y + TRAC_FULL)
								);
				bottom_right :=	(	SELECT COUNT(ID) AS OffsetCount
									FROM vwTRACPersistence
									WHERE (X >= offset_x + TRAC_HALF AND X < offset_x + TRAC_FULL) AND (Y >= offset_y + TRAC_HALF AND Y < offset_y + TRAC_FULL)
								);
				
				total_count := top_left + top_right + bottom_left + bottom_right;
				
				IF total_count <> strikes_in_sector THEN
					RAISE NOTICE 'WARN: The total strike count doesn''t appear match the count in the sector (%%, %%)', total_count, strikes_in_sector;
				END IF;
				
				RAISE NOTICE 'DEBUG: Offset 1 - %% %% %% %%', top_left, top_right, bottom_left, bottom_right;
				
				
				tl := CAST((top_left / total_count) * CAST(TRAC_QUARTER AS DECIMAL) AS INT);
				tr := CAST((top_right / total_count) * CAST(TRAC_QUARTER AS DECIMAL) AS INT);
				bl := CAST((bottom_left / total_count) * CAST(TRAC_QUARTER AS DECIMAL) AS INT);
				br := CAST((bottom_right / total_count) * CAST(TRAC_QUARTER AS DECIMAL) AS INT);
				
				RAISE NOTICE 'DEBUG: Offset 2 - %% %% %% %%', tl, tr, bl, br;
				
				
				-- The greater percentage will make the centre offset to the corner
				x_offset := x_offset + -tl;
				y_offset := y_offset + -tl;
				
				x_offset := x_offset + tr;
				y_offset := y_offset + -tr;
				
				x_offset := x_offset + -bl;
				y_offset := y_offset + bl;
				
				x_offset := x_offset + br;
				y_offset := y_offset + br;
				
				
				-- Apply the offset since we search *around* the strike
				IF detectionmethod = 1 THEN
					x_offset := x_offset + -TRAC_HALF;
					y_offset := y_offset + -TRAC_HALF;
				END IF;
				
				RAISE NOTICE 'DEBUG: Offset 3 - %% %%', x_offset, y_offset;
				
				
				
				------------------------
				-- Register the storm --
				------------------------
				UPDATE tblTRACStatus SET Active = TRUE, NoOfStorms = NoOfStorms + 1;
				
				
				-- Calculate the degrees and miles from the X and Y points
				new_x := strikes_header.X + x_offset;
				new_y := strikes_header.Y + y_offset;
				
				o := 0;
				a := 0;
				deg_offset := 0;
				
				IF (new_x >= 0 and new_x < 300) and (new_y >= 0 and new_y < 300) THEN
					-- Top left
					o := 300 - new_x;
					a := 300 - new_y;
					
					deg_offset := 270;
					
				ELSIF (new_x >= 300 and new_x < 600) and (new_y >= 0 and new_y < 300) THEN
					-- Top right
					o := new_x - 300;
					a := 300 - new_y;
					
					deg_offset := 0;
					
				ELSIF (new_x >= 0 and new_x < 300) and (new_y >= 300 and new_y < 600) THEN
					-- Bottom left
					o := 300 - new_x;
					a := new_y - 300;
					
					deg_offset := 180;
					
				ELSE
					-- Bottom right
					o := new_x - 300;
					a := new_y - 300;
					
					deg_offset := 90;
				END IF;
				
				
				-- Numbers will be zero based, so add one
				o := o + 1;
				a := a + 1;
				
				RAISE NOTICE 'DEBUG: O = %%, A = %%', o, a;
				
				
				-- Time for a bit of trigonometry
				degx := degrees(atan(o / a));
				deg := degx + deg_offset;
				distance := sqrt(power(o, 2) + power(a, 2));
				abs_distance := abs(distance);
				
				RAISE NOTICE 'DEBUG: Degrees = %%, X = %%, H = %%', deg, degx, distance;
				
				
				-- Gather some stats
				IF detectionmethod = 0 THEN
					first_recorded_activity := (SELECT MIN(DateTimeOfStrike) AS FirstRecordedActivity FROM vwTRACPersistence WHERE (X >= strikes_header.X AND X < strikes_header.X + TRAC_FULL) AND (Y >= strikes_header.Y AND Y < strikes_header.Y + TRAC_FULL));
					last_recorded_activity := (SELECT MAX(DateTimeOfStrike) AS LastRecordedActivity FROM vwTRACPersistence WHERE (X >= strikes_header.X AND X < strikes_header.X + TRAC_FULL) AND (Y >= strikes_header.Y AND Y < strikes_header.Y + TRAC_FULL));
					
					current_strike_rate := (SELECT COUNT(ID) FROM vwTRACPersistence WHERE DateTimeOfStrike >= LOCALTIMESTAMP - (TRAC_UPDATE_TIME || ' MINUTES')::INTERVAL AND (X >= strikes_header.X AND X < strikes_header.X + TRAC_FULL) AND (Y >= strikes_header.Y AND Y < strikes_header.Y + TRAC_FULL));
					peak_strike_rate := (SELECT MAX(StrikeCount) FROM vwTRACStrikesPeak WHERE (MinX >= strikes_header.X AND MinX < strikes_header.X + TRAC_FULL) AND (MinY >= strikes_header.Y AND MinY < strikes_header.Y + TRAC_FULL));
					
				ELSIF detectionmethod = 1 THEN
					first_recorded_activity := (SELECT MIN(DateTimeOfStrike) AS FirstRecordedActivity FROM vwTRACPersistence WHERE (X >= strikes_header.X - TRAC_HALF AND X < strikes_header.X + TRAC_HALF) AND (Y >= strikes_header.Y - TRAC_HALF AND Y < strikes_header.Y + TRAC_HALF));
					last_recorded_activity := (SELECT MAX(DateTimeOfStrike) AS LastRecordedActivity FROM vwTRACPersistence WHERE (X >= strikes_header.X - TRAC_HALF AND X < strikes_header.X + TRAC_HALF) AND (Y >= strikes_header.Y - TRAC_HALF AND Y < strikes_header.Y + TRAC_HALF));
					
					current_strike_rate := (SELECT COUNT(ID) FROM vwTRACPersistence WHERE DateTimeOfStrike >= LOCALTIMESTAMP - (TRAC_UPDATE_TIME || ' MINUTES')::INTERVAL AND (X >= strikes_header.X - TRAC_HALF AND X < strikes_header.X + TRAC_HALF) AND (Y >= strikes_header.Y - TRAC_HALF AND Y < strikes_header.Y + TRAC_HALF));
					peak_strike_rate := (SELECT MAX(StrikeCount) FROM vwTRACStrikesPeak WHERE (MinX >= strikes_header.X - TRAC_HALF AND MinX < strikes_header.X + TRAC_HALF) AND (MinY >= strikes_header.Y - TRAC_HALF AND MinY < strikes_header.Y + TRAC_HALF));
				END IF;
				
				IF peak_strike_rate = 0 THEN
					peak_strike_rate := current_strike_rate;
				END IF;
				
				guid := encode(digest(concat(strikes_header.X, strikes_header.X + TRAC_FULL, strikes_header.Y, strikes_header.Y + TRAC_FULL, first_recorded_activity), 'sha1'), 'hex');
				
				-- Pick the middle eight characters since we don't have CRC32, we just need it unique for the session
				guid_ss := (length(guid) / 2) - 4;
				crc32 := substring(guid from guid_ss for 8);
				
				RAISE NOTICE 'DEBUG: guid = %%, guid_ss = %%, crc32 = %%', guid, guid_ss, crc32;
				
				
				-- Since we have the strike rate we can determine the classification of the storm
				intensity_class := 'N/A';
				intensity_trend := 'N/A';
				intensity_trend_symbol := '';
				
				If current_strike_rate < 10 THEN
					intensity_class := 'Very Weak';
					
				ELSIF current_strike_rate < 20 THEN
					intensity_class := 'Weak';
					
				ELSIF current_strike_rate < 40 THEN
					intensity_class := 'Moderate';
					
				ELSIF current_strike_rate < 50 THEN
					intensity_class := 'Strong';
					
				ELSIF current_strike_rate < 60 THEN
					intensity_class := 'Very Strong';
					
				ELSE
					intensity_class := 'Severe';
				END IF;
				
				
				-- Calculate the trend by counting the rises and the falls based on the average strike rate, not the best way but can be improved later
				rises := 0;
				falls := 0;
				
				IF detectionmethod = 0 THEN
					average_strike_count := (SELECT SUM(StrikeCount) / COUNT(*) FROM vwTRACStrikesPeak WHERE (MinX >= strikes_header.X AND MinX < strikes_header.X + TRAC_FULL) AND (MinY >= strikes_header.Y AND MinY < strikes_header.Y + TRAC_FULL));
					
				ELSIF detectionmethod = 1 THEN
					average_strike_count := (SELECT SUM(StrikeCount) / COUNT(*) FROM vwTRACStrikesPeak WHERE (MinX >= strikes_header.X - TRAC_HALF AND MinX < strikes_header.X + TRAC_HALF) AND (MinY >= strikes_header.Y - TRAC_HALF AND MinY < strikes_header.Y + TRAC_HALF));
				END IF;
				
				
				DROP TABLE IF EXISTS tmpStrikesTrend;
				
				IF detectionmethod = 0 THEN
					CREATE TEMPORARY TABLE tmpStrikesTrend AS
						SELECT StrikeCount, PeakTime
						FROM vwTRACStrikesPeak
						WHERE (MinX >= strikes_header.X AND MinX < strikes_header.X + TRAC_FULL) AND (MinY >= strikes_header.Y AND MinY < strikes_header.Y + TRAC_FULL)
					;
					
				ELSIF detectionmethod = 1 THEN
					CREATE TEMPORARY TABLE tmpStrikesTrend AS
						SELECT StrikeCount, PeakTime
						FROM vwTRACStrikesPeak
						WHERE (MinX >= strikes_header.X - TRAC_HALF AND MinX < strikes_header.X + TRAC_HALF) AND (MinY >= strikes_header.Y - TRAC_HALF AND MinY < strikes_header.Y + TRAC_HALF)
					;
				END IF;
				
				
				FOR trend	IN	SELECT StrikeCount
								FROM tmpStrikesTrend
								ORDER BY PeakTime
							LOOP
					
					diff := trend.StrikeCount - average_strike_count;
					
					IF diff > 0 THEN
						rises := rises + 1;
						
					ELSIF diff < 0 THEN
						falls := falls + 1;
					END IF;
				END LOOP;
				
				DROP TABLE IF EXISTS tmpStrikesTrend;
				
				
				RAISE NOTICE 'DEBUG: Rises = %%, falls = %%', rises, falls;
				
				
				IF rises > falls THEN
					intensity_trend := 'Intensifying';
					intensity_trend_symbol := '^';
					
				ELSIF falls > rises THEN
					intensity_trend := 'Weakening';
					intensity_trend_symbol := '.';
					
				ELSE
					intensity_trend := 'No Change';
					intensity_trend_symbol := '-';
				END IF;
				
				
				-- Strike rate amount (mainly for the progress bar)
				amount := 0.;
				
				IF current_strike_rate > 50 THEN
					amount := 1.;
					
				ELSE
					amount := current_strike_rate / 50.;
				END IF;
				
				current_name := crc32 || intensity_trend_symbol || current_strike_rate;
				
				RAISE NOTICE 'INFO: Storm name is %%', current_name;
				
				
				-- Make log of the storm in the database
				tracid := COALESCE((SELECT ID FROM tblTRACHeader WHERE GID = guid LIMIT 1), 0);
				
				IF tracid = 0 THEN
					-- Storm not found in database, add new entry
					RAISE NOTICE 'INFO: Storm GUID %% not found in header, creating entry...', guid;
					
					
					INSERT INTO tblTRACHeader(GID, CRC32, DateTimeOfDiscovery, Bearing, Distance, DetectionMethod)
					VALUES(guid, crc32, first_recorded_activity, deg, abs_distance, 1);
					
					
					tracid := COALESCE((SELECT ID FROM tblTRACHeader WHERE GID = guid LIMIT 1));
					
					IF tracid = 0 THEN
						RAISE NOTICE 'WARN: Failed to locate the newly created record for storm ID %%', guid;
					END IF;
				END IF;
				
				-- Double-check
				IF tracid > 0 THEN
					INSERT INTO tblTRACDetails(HeaderID, DateTimeOfReading, DateTimeOfLastStrike, CurrentStrikeRate, TotalStrikes, Intensity)
					VALUES(tracid, LOCALTIMESTAMP, last_recorded_activity, current_strike_rate, total_count, intensity_trend);
				END IF;
				
				
				RAISE NOTICE 'DEBUG: total_count = %%, trac_most_active_distance = %%', total_count, trac_most_active_distance;
				
				IF total_count > trac_most_active_distance THEN
					trac_most_active := current_name;
					trac_most_active_distance := abs_distance;
					
					UPDATE tblTRACStatus SET MostActive = trac_most_active, MostActiveDistance = trac_most_active_distance;
				END IF;
				
				
				RAISE NOTICE 'DEBUG: abs_distance = %%, trac_closest_distance = %%', abs_distance, trac_closest_distance;
				
				IF abs_distance < trac_closest_distance THEN
					trac_closest := current_name;
					trac_closest_distance := abs_distance;
					
					UPDATE tblTRACStatus SET Closest = trac_closest, ClosestDistance = trac_closest_distance;
				END IF;
				
				
				-- Now for client purposes
				INSERT INTO tblTRACStorms(X, Y, XOffset, YOffset, Name, Intensity, Distance)
				VALUES(strikes_header.X, strikes_header.Y, x_offset, y_offset, current_name, amount, abs_distance);
			END IF;
		END IF;
	END LOOP;
	
	
	-- Clean up
	DROP TABLE IF EXISTS tmpStrikesHeader;
	DROP TABLE IF EXISTS tmpStrikesDetails;
	DROP TABLE IF EXISTS tmpStrikesTrend;
	
	
	
	-- Return
	RAISE NOTICE 'TRAC has found %% storms.', storms_found;
	
	RETURN storms_found;
END
$$ LANGUAGE plpgsql;
"""
		self.db.executeSQLCommand(s, conn = myconn)
		
		
		
		###########
		# Updates #
		###########
		if self.DEBUG_MODE:
			self.log.info("Updating data...")
		
		
		curr_db_version = int(self.ifNoneReturnZero(self.db.danLookup("DatabaseVersion", "tblSystem", "", conn = myconn)))
		
		if curr_db_version < self.DB_VERSION:
			# Update needed
			self.db.executeSQLCommand("ALTER TABLE tblElectricFieldStrength ALTER COLUMN kVm TYPE decimal(4,2)", conn = myconn)
			
			
			self.db.executeSQLCommand("DROP INDEX IF EXISTS StrikeGridRef", conn = myconn)
			
			self.db.executeSQLCommand("DROP INDEX IF EXISTS GridRef0", conn = myconn)
			self.db.executeSQLCommand("DROP INDEX IF EXISTS GridRef1", conn = myconn)
			self.db.executeSQLCommand("DROP INDEX IF EXISTS GridRef2", conn = myconn)
			self.db.executeSQLCommand("DROP INDEX IF EXISTS GridRef3", conn = myconn)
			self.db.executeSQLCommand("DROP INDEX IF EXISTS GridRef4", conn = myconn)
			self.db.executeSQLCommand("DROP INDEX IF EXISTS GridRef5", conn = myconn)
			
			self.db.executeSQLCommand("DROP TABLE IF EXISTS tblStrikesPersistence0 CASCADE", conn = myconn)
			self.db.executeSQLCommand("DROP TABLE IF EXISTS tblStrikesPersistence1 CASCADE", conn = myconn)
			self.db.executeSQLCommand("DROP TABLE IF EXISTS tblStrikesPersistence2 CASCADE", conn = myconn)
			self.db.executeSQLCommand("DROP TABLE IF EXISTS tblStrikesPersistence3 CASCADE", conn = myconn)
			self.db.executeSQLCommand("DROP TABLE IF EXISTS tblStrikesPersistence4 CASCADE", conn = myconn)
			self.db.executeSQLCommand("DROP TABLE IF EXISTS tblStrikesPersistence5 CASCADE", conn = myconn)
			
			self.db.executeSQLCommand("DROP VIEW IF EXISTS vwStrikesPeak CASCADE", conn = myconn)
			
			
			# Finally, update the db version
			self.db.executeSQLCommand("UPDATE tblSystem SET DatabaseVersion = %(DatabaseVersion)s", {"DatabaseVersion": self.DB_VERSION}, myconn)
		
		self.db.disconnectFromDatabase(myconn)
	
	def xmlXRSettingsRead(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		if self.os.path.exists(self.XML_SETTINGS_FILE):
			xmldoc = self.minidom.parse(self.XML_SETTINGS_FILE)
			
			myvars = xmldoc.getElementsByTagName("Setting")
			
			for var in myvars:
				for key in var.attributes.keys():
					val = str(var.attributes[key].value)
					
					# Now put the correct values to correct key
					if key == "ServerPort":
						self.SERVER_PORT = int(val)
						
					elif key == "LD250Bits":
						self.LD250_BITS = int(val)
						
					elif key == "LD250Parity":
						self.LD250_PARITY = val
						
					elif key == "LD250Port":
						self.LD250_PORT = val
						
					elif key == "LD250Squelch":
						self.LD250_SQUELCH = int(val)
						
					elif key == "LD250Speed":
						self.LD250_SPEED = int(val)
						
					elif key == "LD250StopBits":
						self.LD250_STOPBITS = int(val)
						
					elif key == "LD250UseUncorrectedStrikes":
						self.LD250_USE_UNCORRECTED_STRIKES = self.cBool(val)
						
					elif key == "EFM100Bits":
						self.EFM100_BITS = int(val)
						
					elif key == "EFM100Parity":
						self.EFM100_PARITY = val
						
					elif key == "EFM100Port":
						self.EFM100_PORT = val
						
					elif key == "EFM100Speed":
						self.EFM100_SPEED = int(val)
						
					elif key == "EFM100StopBits":
						self.EFM100_STOPBITS = int(val)
						
					elif key == "PostgreSQLDatabase":
						self.POSTGRESQL_DATABASE = val
						
					elif key == "PostgreSQLPassword":
						self.POSTGRESQL_PASSWORD = val
						
					elif key == "PostgreSQLServer":
						self.POSTGRESQL_SERVER = val
						
					elif key == "PostgreSQLUsername":
						self.POSTGRESQL_USERNAME = val
						
					elif key == "CloseDistance":
						self.CLOSE_DISTANCE = int(val)
						
					elif key == "TRACDetectionMethod":
						self.TRAC_DETECTION_METHOD = int(val)
						
					elif key == "TRACSensitivity":
						self.TRAC_SENSITIVITY = int(val)
						
					elif key == "TRACStormWidth":
						self.TRAC_STORM_WIDTH = int(val)
						
					elif key == "TRACUpdateTime":
						self.TRAC_UPDATE_TIME = int(val)
						
					elif key == "StrikeCopyright":
						self.STRIKE_COPYRIGHT = val
						
					elif key == "DebugMode":
						self.DEBUG_MODE = self.cBool(val)
						
					else:
						self.log.warn("XML setting attribute \"%s\" isn't known.  Ignoring..." % key)
	
	def xmlXRSettingsWrite(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			xmloutput = file(self.XML_SETTINGS_FILE, "w")
			
			
			xmldoc = self.minidom.Document()
			
			# Create header
			settings = xmldoc.createElement("SXRServer")
			xmldoc.appendChild(settings)
			
			# Write each of the details one at a time, makes it easier for someone to alter the file using a text editor
			var = xmldoc.createElement("Setting")
			var.setAttribute("ServerPort", str(self.SERVER_PORT))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD250Port", str(self.LD250_PORT))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD250Speed", str(self.LD250_SPEED))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD250Bits", str(self.LD250_BITS))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD250Parity", str(self.LD250_PARITY))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD250StopBits", str(self.LD250_STOPBITS))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD250Squelch", str(self.LD250_SQUELCH))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("LD250UseUncorrectedStrikes", str(self.LD250_USE_UNCORRECTED_STRIKES))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("EFM100Port", str(self.EFM100_PORT))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("EFM100Speed", str(self.EFM100_SPEED))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("EFM100Bits", str(self.EFM100_BITS))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("EFM100Parity", str(self.EFM100_PARITY))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("EFM100StopBits", str(self.EFM100_STOPBITS))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("PostgreSQLServer", str(self.POSTGRESQL_SERVER))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("PostgreSQLDatabase", str(self.POSTGRESQL_DATABASE))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("PostgreSQLUsername", str(self.POSTGRESQL_USERNAME))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("PostgreSQLPassword", str(self.POSTGRESQL_PASSWORD))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("CloseDistance", str(self.CLOSE_DISTANCE))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("TRACDetectionMethod", str(self.TRAC_DETECTION_METHOD))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("TRACSensitivity", str(self.TRAC_SENSITIVITY))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("TRACStormWidth", str(self.TRAC_STORM_WIDTH))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("TRACUpdateTime", str(self.TRAC_UPDATE_TIME))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("StrikeCopyright", str(self.STRIKE_COPYRIGHT))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("DebugMode", str(self.DEBUG_MODE))
			settings.appendChild(var)
			
			
			# Finally, save to the file
			xmloutput.write(xmldoc.toprettyxml())
			xmloutput.close()

class TRAC():
	def __init__(self, database_server, database_database, database_username, database_password, trac_detection_method, debug_mode):
		self.db = Database(database_server, database_database, database_username, database_password, debug_mode)
		self.log = DanLog("TRAC")
		
		self.DEBUG_MODE = debug_mode
		self.TRAC_DETECTION_METHOD = trac_detection_method
	
	def run(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		myconn = []
		self.db.connectToDatabase(myconn)
		
		
		trac_result = self.db.executeSQLQuery("SELECT fnTRAC(%(A)s)", {"A": self.TRAC_DETECTION_METHOD}, myconn)
		
		if trac_result is not None:
			for t in trac_result:
				self.log.info("TRAC has detected %d storms." % int(t[0]))
				break
			
		else:
			if self.DEBUG_MODE:
				self.log.warn("TRAC failed to run, review any SQL errors.")
		
		
		self.db.disconnectFromDatabase(myconn)

class XRXMLRPCFunctions(xmlrpc.XMLRPC):
	def __init__(self, database_server, database_database, database_username, database_password, debug_mode):
		xmlrpc.XMLRPC.__init__(self)
		
		
		from danlog import DanLog
		from twisted.internet import threads
		from xml.dom import minidom
		from StringIO import StringIO
		
		import gzip
		import xmlrpclib
		
		
		self.DEBUG_MODE = debug_mode
		
		self.db = Database(database_server, database_database, database_username, database_password, debug_mode)
		self.gzip = gzip
		self.log = DanLog("XRXMLRPCFunctions")
		self.minidom = minidom
		self.stringio = StringIO
		self.twisted_internet_threads = threads
		self.xmlrpclib = xmlrpclib
	
	def compressData(self, data):
		dio = self.stringio()
		
		com = self.gzip.GzipFile(fileobj = dio, mode = "wb", compresslevel = 9)
		com.write(data)
		com.close()
		
		return self.xmlrpclib.Binary(dio.getvalue())
	
	
	def xmlrpc_fieldCounter(self):
		self.log.info("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT kVm FROM tblElectricFieldStrength ORDER BY ID DESC LIMIT 1", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("kVm", str(row[0]))
				sxrdataset.appendChild(var)
				break
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_fieldCounter.help = "Returns the electric field strength from the Boltek EFM-100."
	xmlrpc_fieldCounter.signature = [["SXRDataSet[kVm]", "none"]]
	
	
	def xmlrpc_lastHourOfStrikesByMinute(self):
		self.log.info("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT Minute, StrikeAge, NumberOfStrikes FROM vwStrikesSummaryByMinute ORDER BY Minute", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("Minute", str(row[0]))
				var.setAttribute("StrikeAge", str(row[1]))
				var.setAttribute("NumberOfStrikes", str(row[2]))
				sxrdataset.appendChild(var)
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_lastHourOfStrikesByMinute.help = "Returns the number of strikes in the last hour grouped per minute, the strike age is represented in minutes."
	xmlrpc_lastHourOfStrikesByMinute.signature = [["SXRDataSet[Minute, StrikeAge, NumberOfStrikes]", "none"]]
	
	
	def xmlrpc_serverDetails(self):
		self.log.info("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT ServerStarted, ServerApplication, ServerCopyright, ServerVersion, StrikeCopyright FROM tblServerDetails LIMIT 1", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				self.log.info("Row...")
				var = xmldoc.createElement("Row")
				var.setAttribute("ServerStarted", str(row[0]))
				var.setAttribute("ServerApplication", str(row[1]))
				var.setAttribute("ServerCopyright", str(row[2]))
				var.setAttribute("ServerVersion", str(row[3]))
				var.setAttribute("StrikeCopyright", str(row[4]))
				sxrdataset.appendChild(var)
				break
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_serverDetails.help = "Returns specific details about the server StormForce XR is running on."
	xmlrpc_serverDetails.signature = [["SXRDataSet[ServerStarted, ServerApplication, ServerCopyright, ServerVersion, StrikeCopyright]", "none"]]
	
	
	def xmlrpc_serverUptime(self):
		self.log.info("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT DATE_PART('epoch', ServerStarted) AS ServerStartedUT FROM tblServerDetails LIMIT 1", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("ServerStartedUT", str(row[0]))
				sxrdataset.appendChild(var)
				break
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_serverUptime.help = "Returns the server started date in UNIX timestamp format."
	xmlrpc_serverUptime.signature = [["SXRDataSet[ServerStartedUT]", "none"]]
	
	
	def xmlrpc_strikeCounter(self):
		self.log.info("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT CloseMinute, CloseTotal, NoiseMinute, NoiseTotal, StrikesMinute, StrikesTotal, StrikesOutOfRange FROM tblStrikeCounter LIMIT 1", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("CloseMinute", str(row[0]))
				var.setAttribute("CloseTotal", str(row[1]))
				var.setAttribute("NoiseMinute", str(row[2]))
				var.setAttribute("NoiseTotal", str(row[3]))
				var.setAttribute("StrikesMinute", str(row[4]))
				var.setAttribute("StrikesTotal", str(row[5]))
				var.setAttribute("StrikesOutOfRange", str(row[6]))
				sxrdataset.appendChild(var)
				break
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_strikeCounter.help = "Returns the strike counters."
	xmlrpc_strikeCounter.signature = [["SXRDataSet[CloseMinute, CloseTotal, NoiseMinute, NoiseTotal, StrikesMinute, StrikesTotal, StrikesOutOfRange]", "none"]]
	
	
	def xmlrpc_strikePersistence(self):
		self.log.info("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT DISTINCT StrikeAge, X, Y, X - 300 AS RelativeX, Y - 300 AS RelativeY, DateTimeOfStrike FROM vwStrikesPersistence ORDER BY DateTimeOfStrike ASC", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("StrikeAge", str(row[0]))
				var.setAttribute("X", str(row[1]))
				var.setAttribute("Y", str(row[2]))
				var.setAttribute("RelativeX", str(row[3]))
				var.setAttribute("RelativeY", str(row[4]))
				var.setAttribute("DateTimeOfStrike", str(row[5]))
				sxrdataset.appendChild(var)
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_strikePersistence.help = "Returns the persistence data based on the current time minus one hour, remember that depending on the server settings the X,Y co-ords maybe using uncorrected strike factors (default is to use corrected strike factors).  The relative values are based on the centre of the map and the strike age is represented in seconds."
	xmlrpc_strikePersistence.signature = [["SXRDataSet[StrikeAge, X, Y, RelativeX, RelativeY, DateTimeOfStrike]", "none"]]
	
	
	def xmlrpc_tracStatus(self):
		self.log.info("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT Version, Active, NoOfStorms, MostActive, MostActiveDistance, Closest, ClosestDistance, Width FROM tblTRACStatus LIMIT 1", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("Version", str(row[0]))
				var.setAttribute("Active", str(row[1]))
				var.setAttribute("NoOfStorms", str(row[2]))
				var.setAttribute("MostActive", str(row[3]))
				var.setAttribute("MostActiveDistance", str(row[4]))
				var.setAttribute("Closest", str(row[5]))
				var.setAttribute("ClosestDistance", str(row[6]))
				var.setAttribute("Width", str(row[7]))
				sxrdataset.appendChild(var)
				break
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_tracStatus.help = "Returns the status of the TRAC engine."
	xmlrpc_tracStatus.signature = [["SXRDataSet[Version, Active, NoOfStorms, MostActive, MostActiveDistance, Closest, ClosestDistance, Width]", "none"]]
	
	
	def xmlrpc_tracStorms(self):
		self.log.info("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT X, Y, XOffset, YOffset, Name, Intensity, Distance FROM tblTRACStorms ORDER BY ID", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("X", str(row[0]))
				var.setAttribute("Y", str(row[1]))
				var.setAttribute("XOffset", str(row[2]))
				var.setAttribute("YOffset", str(row[3]))
				var.setAttribute("Name", str(row[4]))
				var.setAttribute("Intensity", str(row[5]))
				var.setAttribute("Distance", str(row[6]))
				sxrdataset.appendChild(var)
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_tracStorms.help = "Returns the storms TRAC is monitoring for drawing on-screen."
	xmlrpc_tracStorms.signature = [["SXRDataSet[X, Y, XOffset, YOffset, Name, Intensity, Distance]", "none"]]
	
	
	def xmlrpc_unitStatus(self):
		self.log.info("Starting...")
		
		
		def cb():
			myconn = []
			self.db.connectToDatabase(myconn)
			
			rows = self.db.executeSQLQuery("SELECT Hardware, SquelchLevel, UseUncorrectedStrikes, CloseAlarm, SevereAlarm, ReceiverLastDetected, ReceiverLost FROM vwUnitStatus ORDER BY Hardware", conn = myconn)
			
			self.db.disconnectFromDatabase(myconn)
			
			
			xmldoc = self.minidom.Document()
			
			sxrdataset = xmldoc.createElement("SXRDataSet")
			xmldoc.appendChild(sxrdataset)
			
			for row in rows:
				var = xmldoc.createElement("Row")
				var.setAttribute("Hardware", str(row[0]))
				var.setAttribute("SquelchLevel", str(row[1]))
				var.setAttribute("UseUncorrectedStrikes", str(row[2]))
				var.setAttribute("CloseAlarm", str(row[3]))
				var.setAttribute("SevereAlarm", str(row[4]))
				var.setAttribute("ReceiverLastDetected", str(row[5]))
				var.setAttribute("ReceiverLost", str(row[6]))
				sxrdataset.appendChild(var)
			
			return self.compressData(xmldoc.toprettyxml())
		
		return self.twisted_internet_threads.deferToThread(cb)
	
	xmlrpc_unitStatus.help = "Returns information about the Boltek LD-250 and Boltek EFM-100."
	xmlrpc_unitStatus.signature = [["SXRDataSet[Hardware, SquelchLevel, UseUncorrectedStrikes, CloseAlarm, SevereAlarm, ReceiverLastDetected, ReceiverLost]", "none"]]


########
# Main #
########
if __name__ == "__main__":
	l = None
	
	try:
		from danlog import DanLog
		
		
		l = DanLog("Main")
		l.info("Preparing...")
		
		sxr = SXRServer()
		sxr.main()
		sxr = None
		
	except Exception, ex:
		if l is not None:
			l.fatal(str(ex))
			
		else:
			print "Exception: %s" % str(ex)
