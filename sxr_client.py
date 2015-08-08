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
# StormForce XR (XMLRPC) Client                   #
###################################################
# Version:     v0.5.0                             #
###################################################


###########
# Classes #
###########
class SXRClient():
	def __init__(self):
		from danlog import DanLog
		from xml.dom import minidom
		from StringIO import StringIO
		
		import gzip
		import os
		import sys
		import threading
		import time
		import xmlrpclib
		
		
		self.cron_alive = False
		self.cron_thread = None
		self.gzip = gzip
		self.log = DanLog("SXRClient")
		self.minidom = minidom
		self.os = os
		self.stringio = StringIO
		self.sys = sys
		self.threading = threading
		self.time = time
		self.ui = None
		self.xmlrpclib = xmlrpclib
		
		self.CAPTURE_DIRECTORY = "capture"
		self.CAPTURE_FILENAME = "stormforce-xr.png"
		self.CAPTURE_FULL_PATH =  self.os.path.join(self.CAPTURE_DIRECTORY, self.CAPTURE_FILENAME)
		self.CLIENT_VERSION = "0.5.0"
		
		self.DEBUG_MODE = False
		self.DEMO_MODE = False
		
		self.GRAPH_DIRECTORY = "graphs"
		self.GRAPH_MBM_FILENAME = "mbm.png"
		self.GRAPH_MBM_FULL_PATH = self.os.path.join(self.GRAPH_DIRECTORY, self.GRAPH_MBM_FILENAME)
		
		self.MAP_MATRIX_CENTRE = (300, 300)
		self.MAP_MATRIX_SIZE = (600, 600)
		
		self.SHOW_CROSSHAIR = True
		self.SHOW_RANGE_CIRCLES = False
		self.STORMFORCEXR_SERVER = "http://127.0.0.1:7397/xmlrpc/"
		self.STRIKE_SHAPE = 1
		
		self.TRAC_STORM_WIDTH = 0
		self.TRAC_VERSION = "0.0.0"
		
		self.UPDATE_PERIOD_CAPTURE = 15.
		self.UPDATE_PERIOD_CURRENT_TIME = 1.
		self.UPDATE_PERIOD_EFM100 = 5.
		self.UPDATE_PERIOD_GRAPHS = 60.
		self.UPDATE_PERIOD_LD250 = 2.
		self.UPDATE_PERIOD_STRIKES = 15.
		
		self.ZOOM_DISTANCE = 300
		
		self.XML_SETTINGS_FILE = "sxrclient-settings.xml"
	
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
		
		
		# Get the server uptime, only need to get it once
		last_uptime = 0.
		
		try:
			s = self.xmlrpclib.ServerProxy(self.STORMFORCEXR_SERVER)
			data = self.extractDataset(s.serverUptime().data)
			s = None
			
			for row in data:
				last_uptime = float(row["ServerStartedUT"])
				break
			
		except Exception, ex:
			self.log.error(str(ex))
			
			last_uptime = self.time.time()
		
		
		# Run "cron"
		last = self.time.time() - 3600. # Minus one hour to force a update immediately
		last_capture = last
		last_efm100 = last
		last_graphs = last
		last_ld250 = last
		last_strike = last
		last_time = last
		
		while self.cron_alive:
			now = self.time.time()
			
			
			# What do we need to do?
			last_capture_diff = (now - last_capture)
			last_efm100_diff = (now - last_efm100)
			last_graphs_diff = (now - last_graphs)
			last_ld250_diff = (now - last_ld250)
			last_strike_diff = (now - last_strike)
			last_time_diff = (now - last_time)
			
			
			# Update the LD-250
			if last_ld250_diff >= self.UPDATE_PERIOD_LD250:
				try:
					# Strike counter
					s = self.xmlrpclib.ServerProxy(self.STORMFORCEXR_SERVER)
					data = self.extractDataset(s.strikeCounter().data)
					s = None
					
					for row in data:
						self.ui.updateLD250CloseArea(int(row["CloseMinute"]), int(row["CloseTotal"]))
						self.ui.updateLD250NoiseArea(int(row["NoiseMinute"]), int(row["NoiseTotal"]))
						self.ui.updateLD250StrikeArea(int(row["StrikesMinute"]), int(row["StrikesTotal"]), int(row["StrikesOutOfRange"]))
						break
					
					
					# Receiver status and alarms
					s = self.xmlrpclib.ServerProxy(self.STORMFORCEXR_SERVER)
					data = self.extractDataset(s.unitStatus().data)
					s = None
					
					for row in data:
						if str(row["Hardware"]) == "Boltek LD-250":
							if not self.cBool(row["ReceiverLost"]):
								self.ui.updateLD250ReceiverArea("Active")
								
							else:
								self.ui.updateLD250ReceiverArea("Inactive")
							
							
							self.ui.updateLD250CloseAlarmArea(self.cBool(row["CloseAlarm"]))
							self.ui.updateLD250SevereAlarmArea(self.cBool(row["SevereAlarm"]))
							self.ui.updateLD250SquelchArea(int(row["SquelchLevel"]))
							
							break
					
				except Exception, ex:
					self.log.error(str(ex))
					
				finally:
					last_ld250 = self.time.time()
			
			
			# Update the EFM-100
			if last_efm100_diff >= self.UPDATE_PERIOD_EFM100:
				try:
					# Field strength
					s = self.xmlrpclib.ServerProxy(self.STORMFORCEXR_SERVER)
					data = self.extractDataset(s.fieldCounter().data)
					s = None
					
					for row in data:
						self.ui.updateEFM100FieldArea(float(row["kVm"]))
						break
					
					
					# Receiver status and alarms
					s = self.xmlrpclib.ServerProxy(self.STORMFORCEXR_SERVER)
					data = self.extractDataset(s.unitStatus().data)
					s = None
					
					for row in data:
						if str(row["Hardware"]) == "Boltek EFM-100":
							if not self.cBool(row["ReceiverLost"]):
								self.ui.updateEFM100ReceiverArea("Active")
								
							else:
								self.ui.updateEFM100ReceiverArea("Inactive")
							
							break
					
				except Exception, ex:
					self.log.error(str(ex))
					
				finally:
					last_efm100 = self.time.time()
			
			
			# Update strikes (persistence)
			if last_strike_diff >= self.UPDATE_PERIOD_STRIKES:
				try:
					# Re-draw the base screen and plot "old" strikes
					s = self.xmlrpclib.ServerProxy(self.STORMFORCEXR_SERVER)
					data = self.extractDataset(s.strikePersistence().data)
					s = None
					
					
					# "Clear" the strike area
					self.ui.renderScreen()
					
					
					# Old strikes
					strike_colour = None
					
					x = 0
					y = 0
					
					for row in data:
						if int(row["StrikeAge"]) >= 0 and int(row["StrikeAge"]) < 300:
							strike_colour = self.ui.COLOUR_OLD_STRIKE_0
							
						elif int(row["StrikeAge"]) >= 300 and int(row["StrikeAge"]) < 600:
							strike_colour = self.ui.COLOUR_OLD_STRIKE_1
							
						elif int(row["StrikeAge"]) >= 600 and int(row["StrikeAge"]) < 900:
							strike_colour = self.ui.COLOUR_OLD_STRIKE_2
							
						elif int(row["StrikeAge"]) >= 900 and int(row["StrikeAge"]) < 1200:
							strike_colour = self.ui.COLOUR_OLD_STRIKE_3
							
						elif int(row["StrikeAge"]) >= 1200 and int(row["StrikeAge"]) < 1500:
							strike_colour = self.ui.COLOUR_OLD_STRIKE_4
							
						elif int(row["StrikeAge"]) >= 1500 and int(row["StrikeAge"]) < 1800:
							strike_colour = self.ui.COLOUR_OLD_STRIKE_5
							
						elif int(row["StrikeAge"]) >= 1800 and int(row["StrikeAge"]) < 2100:
							strike_colour = self.ui.COLOUR_OLD_STRIKE_6
							
						elif int(row["StrikeAge"]) >= 2100 and int(row["StrikeAge"]) < 2400:
							strike_colour = self.ui.COLOUR_OLD_STRIKE_7
							
						elif int(row["StrikeAge"]) >= 2400 and int(row["StrikeAge"]) < 2700:
							strike_colour = self.ui.COLOUR_OLD_STRIKE_8
							
						elif int(row["StrikeAge"]) >= 2700 and int(row["StrikeAge"]) < 3000:
							strike_colour = self.ui.COLOUR_OLD_STRIKE_9
							
						elif int(row["StrikeAge"]) >= 3000 and int(row["StrikeAge"]) < 3300:
							strike_colour = self.ui.COLOUR_OLD_STRIKE_10
							
						else:
							strike_colour = self.ui.COLOUR_OLD_STRIKE_11
						
						
						# Draw the strike with it's colour
						x = int(row["X"])
						y = int(row["Y"])
						
						
						self.ui.plotStrikeXY(x + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2), y + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2), strike_colour)
					
					
					# Update TRAC while we're at it
					s = self.xmlrpclib.ServerProxy(self.STORMFORCEXR_SERVER)
					data = self.extractDataset(s.tracStatus().data)
					s = None
					
					
					TRAC_STORM_WIDTH = 0
					
					for row in data:
						self.ui.updateTRACVersionArea(str(row["Version"]))
						self.ui.updateTRACStatus(self.cBool(row["Active"]))
						self.ui.updateTRACStormsArea(int(row["NoOfStorms"]))
						self.ui.updateTRACClosestArea("%s" % str(row["Closest"]))
						self.ui.updateTRACMostActiveArea("%s" % str(row["MostActive"]))
						self.ui.updateTRACStormWidthArea(int(row["Width"]))
						
						TRAC_STORM_WIDTH = int(row["Width"])
						break
					
					
					TRAC_FULL = 0
					
					if TRAC_STORM_WIDTH % 2 == 0:
						TRAC_FULL = int(TRAC_STORM_WIDTH)
						
					else:
						TRAC_FULL = int(TRAC_STORM_WIDTH - 1)
					
					TRAC_HALF = TRAC_FULL / 2
					TRAC_THIRD = TRAC_FULL / 3
					TRAC_QUARTER = TRAC_HALF / 2
					
					
					# Draw the storms TRAC is monitoring
					s = self.xmlrpclib.ServerProxy(self.STORMFORCEXR_SERVER)
					data = self.extractDataset(s.tracStorms().data)
					s = None
					
					if self.DEBUG_MODE:
						# Draw the TRAC grid to help debug it
						for y in range(0, self.MAP_MATRIX_SIZE[1], TRAC_FULL):
							for x in range(0, self.MAP_MATRIX_SIZE[0], TRAC_FULL):
								rect = self.ui.pygame.draw.line(self.ui.screen, self.ui.COLOUR_SIDELINE, [x, y], [x, y], 1)
								self.ui.pygame.display.update(rect)
					
					for row in data:
						x = int(row["X"])
						y = int(row["Y"])
						x_offset = int(row["XOffset"])
						y_offset = int(row["YOffset"])
						name = str(row["Name"])
						intensity = int(row["Intensity"])
						
						
						points = []
						
						if self.STRIKE_SHAPE == self.ui.SHAPE_SQUARE:
							points.append([x + x_offset + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2), y + y_offset + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2)])
							points.append([x + TRAC_FULL + x_offset + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2), y + y_offset + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2)])
							points.append([x + TRAC_FULL + x_offset + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2), y + TRAC_FULL + y_offset + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2)])
							points.append([x + x_offset + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2), y + TRAC_FULL + y_offset + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2)])
							
						elif self.STRIKE_SHAPE == self.ui.SHAPE_TRIANGLE or self.STRIKE_SHAPE == self.ui.SHAPE_PLUS_1 or self.STRIKE_SHAPE == self.ui.SHAPE_PLUS_2:
							points.append([x + TRAC_HALF + x_offset + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2), y + y_offset + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2)])
							points.append([x + TRAC_FULL + x_offset + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2), y + TRAC_HALF + y_offset + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2)])
							points.append([x + TRAC_HALF + x_offset + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2), y + TRAC_FULL + y_offset + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2)])
							points.append([x + x_offset + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2), y + TRAC_HALF + y_offset + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2)])
							
						elif self.STRIKE_SHAPE == self.ui.SHAPE_CIRCLE:
							rect = self.ui.pygame.draw.circle(self.ui.screen, self.ui.TRAC_COLOUR, [int(x + TRAC_HALF + x_offset + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2)), int(y + TRAC_HALF + y_offset + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2))], TRAC_HALF, 1)
						
						
						if (self.STRIKE_SHAPE <> self.ui.SHAPE_CIRCLE):
							rect = self.ui.pygame.draw.polygon(self.ui.screen, self.ui.progressBarColour(self.ui.TRAC_GRADIENT_MIN, self.ui.TRAC_GRADIENT_MAX, int(TRAC_FULL * intensity), TRAC_FULL), points, 1)
						
						self.ui.pygame.display.update(rect)
						
						
						# Draw the intensity as a "progress bar" with the storm ID as well - the CRC32 length will be 40 pixels
						rect = self.ui.pygame.Rect(((x + x_offset + TRAC_HALF + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2)) - 30, y + y_offset + TRAC_FULL + 3 + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2)), (70, 8))
						
						id_surface = self.ui.square_font.render(name, True, self.ui.COLOUR_BLACK)
						self.ui.screen.blit(id_surface, [(x + x_offset + TRAC_HALF + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2)) - 29, y + y_offset + TRAC_FULL + 3 + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2)])
						
						id_surface = self.ui.square_font.render(name, True, self.ui.COLOUR_WHITE)
						self.ui.screen.blit(id_surface, [(x + x_offset + TRAC_HALF + self.ui.CENTRE_X - (self.ui.MAP_SIZE[0] / 2)) - 30, y + y_offset + TRAC_FULL + 2 + self.ui.CENTRE_Y - (self.ui.MAP_SIZE[1] / 2)])
						
						self.ui.pygame.display.update(rect)
					
				except Exception, ex:
					self.log.error(str(ex))
					
				finally:
					last_strike = self.time.time()
			
			
			# Update the graphs
			if last_graphs_diff >= self.UPDATE_PERIOD_GRAPHS:
				try:
					g = XRGraphs()
					
					if g.available():
						# Minute-by-minute
						s = self.xmlrpclib.ServerProxy(self.STORMFORCEXR_SERVER)
						data = self.extractDataset(s.lastHourOfStrikesByMinute().data)
						s = None
						
						g.lastHourOfStrikesByMinute(data, self.GRAPH_MBM_FULL_PATH)
						
					else:
						if self.os.path.exists(self.GRAPH_MBM_FULL_PATH):
							self.os.unlink(self.GRAPH_MBM_FULL_PATH)
					
					g.dispose()
					g = None
					
					
					self.ui.updateStrikeHistoryArea()
					
				except Exception, ex:
					self.log.error(str(ex))
					
				finally:
					last_graphs = self.time.time()
			
			
			# Update current time/date and uptime
			if last_time_diff >= self.UPDATE_PERIOD_CURRENT_TIME:
				try:
					self.ui.updateTime()
					self.ui.updateUptime(now - last_uptime)
					
				except Exception, ex:
					self.log.error(str(ex))
					
				finally:
					last_time = self.time.time()
			
			
			# Capture
			if last_capture_diff >= self.UPDATE_PERIOD_CAPTURE:
				try:
					self.ui.captureScreen(self.CAPTURE_FULL_PATH)
					
				except Exception, ex:
					self.log.error(str(ex))
					
				finally:
					last_capture = self.time.time()
			
			
			self.time.sleep(0.1)
	
	def decompress(self, data):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		dio = self.stringio(data)
		com = self.gzip.GzipFile(fileobj = dio, mode = "rb")
		
		return com.read()
	
	def exitProgram(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		global cron_alive
		
		cron_alive = False
		
		self.sys.exit(0)
	
	def extractDataset(self, data):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		xmldata = self.stringio(self.decompress(data))
		xmldoc = self.minidom.parse(xmldata)
		
		myvars = xmldoc.getElementsByTagName("Row")
		
		
		ret = []
		
		for var in myvars:
			row = {}
			
			for key in var.attributes.keys():
				val = str(var.attributes[key].value)
				
				row[str(key)] = val
			
			ret.append(row)
		
		return ret
	
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
		self.log.info("StormForce XR - Client")
		self.log.info("======================")
		self.log.info("Checking settings...")
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			self.log.warn("The XML settings file doesn't exist, create one...")
			
			self.xmlXRSettingsWrite()
			
			
			self.log.info("The XML settings file has been created using the default settings.  Please edit it and restart the SXR client once you're happy with the settings.")
			
			self.exitProgram()
			
		else:
			self.log.info("Reading XML settings...")
			
			self.xmlXRSettingsRead()
			
			# This will ensure it will have any new settings in
			if self.os.path.exists(self.XML_SETTINGS_FILE + ".bak"):
				self.os.unlink(self.XML_SETTINGS_FILE + ".bak")
				
			self.os.rename(self.XML_SETTINGS_FILE, self.XML_SETTINGS_FILE + ".bak")
			self.xmlXRSettingsWrite()
		
		
		self.log.info("Creating directories...")
		
		if not self.os.path.exists(self.CAPTURE_DIRECTORY):
			self.os.mkdir(self.CAPTURE_DIRECTORY)
		
		if not self.os.path.exists(self.GRAPH_DIRECTORY):
			self.os.mkdir(self.GRAPH_DIRECTORY)
		
		
		self.log.info("Removing old captures...")
		
		for root, dirs, files in self.os.walk(self.CAPTURE_DIRECTORY, topdown = False):
			for f in files:
				self.os.unlink(self.os.path.join(root, f))
		
		
		self.log.info("Removing old graphs...")
		
		for root, dirs, files in self.os.walk(self.GRAPH_DIRECTORY, topdown = False):
			for f in files:
				self.os.unlink(self.os.path.join(root, f))
		
		
		self.log.info("Creating UI...")
		self.ui = UI(self, self.DEBUG_MODE)
		
		
		self.log.info("Starting cron...")
		self.cron_alive = True
		
		self.cron_thread = self.threading.Thread(target = self.cron)
		self.cron_thread.setDaemon(1)
		self.cron_thread.start()
		
		
		self.log.info("Starting UI...")
		
		try:
			self.ui.start()
			
		except KeyboardInterrupt:
			pass
			
		except Exception, ex:
			self.log.error(str(ex))
		
		
		self.log.info("Exiting...")
		self.exitProgram()
	
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
					if key == "StormForceXRServer":
						self.STORMFORCEXR_SERVER = val
						
					elif key == "DebugMode":
						self.DEBUG_MODE = self.cBool(val)
						
					elif key == "DemoMode":
						self.DEMO_MODE = self.cBool(val)
						
					elif key == "StrikeShape":
						self.STRIKE_SHAPE = int(val)
						
					elif key == "ShowCrosshair":
						self.SHOW_CROSSHAIR = self.cBool(val)
						
					elif key == "ShowRangeCircles":
						self.SHOW_RANGE_CIRCLES = self.cBool(val)
						
					elif key == "UpdatePeriodCapture":
						self.UPDATE_PERIOD_CAPTURE = float(val)
						
					elif key == "UpdatePeriodCurrentTime":
						self.UPDATE_PERIOD_CURRENT_TIME = float(val)
						
					elif key == "UpdatePeriodEFM100":
						self.UPDATE_PERIOD_EFM100 = float(val)
						
					elif key == "UpdatePeriodGraphs":
						self.UPDATE_PERIOD_GRAPHS = float(val)
						
					elif key == "UpdatePeriodLD250":
						self.UPDATE_PERIOD_LD250 = float(val)
						
					elif key == "UpdatePeriodStrikes":
						self.UPDATE_PERIOD_STRIKES = float(val)
						
					else:
						self.log.warn("XML setting attribute \"%s\" isn't known.  Ignoring..." % key)
	
	def xmlXRSettingsWrite(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		if not self.os.path.exists(self.XML_SETTINGS_FILE):
			xmloutput = file(self.XML_SETTINGS_FILE, "w")
			
			
			xmldoc = self.minidom.Document()
			
			# Create header
			settings = xmldoc.createElement("SXRClient")
			xmldoc.appendChild(settings)
			
			# Write each of the details one at a time, makes it easier for someone to alter the file using a text editor
			var = xmldoc.createElement("Setting")
			var.setAttribute("StormForceXRServer", str(self.STORMFORCEXR_SERVER))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("DemoMode", str(self.DEMO_MODE))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("StrikeShape", str(self.STRIKE_SHAPE))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("ShowCrosshair", str(self.SHOW_CROSSHAIR))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("ShowRangeCircles", str(self.SHOW_RANGE_CIRCLES))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodCapture", str(self.UPDATE_PERIOD_CAPTURE))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodCurrentTime", str(self.UPDATE_PERIOD_CURRENT_TIME))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodEFM100", str(self.UPDATE_PERIOD_EFM100))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodGraphs", str(self.UPDATE_PERIOD_GRAPHS))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodLD250", str(self.UPDATE_PERIOD_LD250))
			settings.appendChild(var)
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("UpdatePeriodStrikes", str(self.UPDATE_PERIOD_STRIKES))
			settings.appendChild(var)
			
			
			var = xmldoc.createElement("Setting")
			var.setAttribute("DebugMode", str(self.DEBUG_MODE))
			settings.appendChild(var)
			
			
			# Finally, save to the file
			xmloutput.write(xmldoc.toprettyxml())
			xmloutput.close()

class UI():
	def __init__(self, client, debug_mode = False):
		from danlog import DanLog
		from datetime import datetime
		
		import math
		import os
		import xmlrpclib
		
		
		self.client = client
		self.datetime = datetime
		self.log = DanLog("UI")
		self.math = math
		self.os = os
		self.xmlrpclib = xmlrpclib
		
		
		self.BACKGROUND = None
		self.CENTRE_X = 300
		self.CENTRE_Y = 300
		self.CLOSE_TEXT_COLOUR = [255, 0, 0]
		self.COLOUR_ALARM_ACTIVE = [255, 0, 0]
		self.COLOUR_ALARM_INACTIVE = [0, 255, 0]
		self.COLOUR_BLACK = [0, 0, 0]
		self.COLOUR_CROSSHAIR = [245, 245, 90]
		self.COLOUR_NEW_STRIKE = [252, 252, 252]
		self.COLOUR_OLD_STRIKE_0 = [255, 100, 0]
		self.COLOUR_OLD_STRIKE_1 = [255, 200, 0]
		self.COLOUR_OLD_STRIKE_2 = [200, 255, 0]
		self.COLOUR_OLD_STRIKE_3 = [150, 255, 0]
		self.COLOUR_OLD_STRIKE_4 = [0, 255, 50]
		self.COLOUR_OLD_STRIKE_5 = [0, 255, 150]
		self.COLOUR_OLD_STRIKE_6 = [0, 200, 200]
		self.COLOUR_OLD_STRIKE_7 = [0, 150, 255]
		self.COLOUR_OLD_STRIKE_8 = [0, 50, 255]
		self.COLOUR_OLD_STRIKE_9 = [50, 50, 255]
		self.COLOUR_OLD_STRIKE_10 = [100, 0, 255]
		self.COLOUR_OLD_STRIKE_11 = [150, 0, 200]
		self.COLOUR_RANGE_25 = [146, 146, 146]
		self.COLOUR_RANGE_50 = [146, 146, 146]
		self.COLOUR_RANGE_100 = [146, 146, 146]
		self.COLOUR_RANGE_150 = [146, 146, 146]
		self.COLOUR_RANGE_200 = [146, 146, 146]
		self.COLOUR_RANGE_250 = [146, 146, 146]
		self.COLOUR_RANGE_300 = [146, 146, 146]
		self.COLOUR_SIDELINE = [255, 255, 255]
		self.COLOUR_WHITE = [255, 255, 255]
		self.COLOUR_YELLOW = [255, 255, 0]
		self.COPYRIGHT_MESSAGE_1 = "StormForce XR - Client v" + self.client.CLIENT_VERSION
		self.COPYRIGHT_MESSAGE_2 = "(c) 2008-2012, 2014 - Daniel Knaggs"
		self.DEBUG_MODE = debug_mode
		self.EFM100_FIELD = (605, 116)
		self.EFM100_FIELD_VALUE = (682, 116)
		self.EFM100_HEADER = (605, 96)
		self.EFM100_RECEIVER = (605, 108)
		self.EFM100_RECEIVER_VALUE = (682, 108)
		self.INFO_SIZE = None
		self.LD250_CLOSE = (764, 20)
		self.LD250_CLOSE_VALUE = (814, 20)
		self.LD250_CLOSE_ALARM = (605, 20)
		self.LD250_CLOSE_ALARM_VALUE = (682, 20)
		self.LD250_HEADER = (605, 0)
		self.LD250_NOISE = (764, 28)
		self.LD250_NOISE_VALUE = (814, 28)
		self.LD250_RECEIVER = (605, 12)
		self.LD250_RECEIVER_VALUE = (682, 12)
		self.LD250_SEVERE_ALARM = (605, 28)
		self.LD250_SEVERE_ALARM_VALUE = (682, 28)
		self.LD250_SQUELCH = (605, 36)
		self.LD250_SQUELCH_VALUE = (682, 36)
		self.LD250_STRIKES = (764, 12)
		self.LD250_STRIKES_VALUE = (814, 12)
		self.LDUNIT_SQUELCH = 0
		self.MANIFESTO_ELECTION = 0
		self.MANIFESTO_PUBLISHED = 1
		self.MANIFESTO_UNPUBLISHED = 2
		self.MAP_MATRIX_CENTRE = (300, 300) # Can be changed if needed
		self.MAP_MATRIX_SIZE = (600, 600) # Ditto
		self.MAP_SIZE = (600, 600) # DO NOT CHANGE!
		self.MAP = self.os.path.join("png", "map-300.png")
		self.NOISE_TEXT_COLOUR = [30, 200, 240]
		self.SCREEN_SIZE = (920, 600)
		self.SHAPE_CIRCLE = 2
		self.SHAPE_PLUS_1 = 3
		self.SHAPE_PLUS_2 = 4
		self.SHAPE_SQUARE = 0
		self.SHAPE_TRIANGLE = 1
		self.SMALL_NUM = 0.000001
		self.SSBT_ENABLED = False
		self.SSBT_HEADER = (605, 240)
		self.SSBT_MANIFESTO = (605, 260)
		self.SSBT_MANIFESTO_VALUE = (682, 260)
		self.SSBT_STATUS = (605, 252)
		self.SSBT_STATUS_VALUE = (682, 252)
		self.STRIKE_GRAPH = (603, 288)
		self.STRIKE_GRAPH_HEADER = (605, 288)
		self.STRIKE_TEXT_COLOUR = [240, 230, 0]
		self.TIME_SIZE = (220, 20)
		self.TIME_TEXT = [668, 572]
		self.TIME_TEXT_COLOUR = [0, 200, 36]
		self.TRAC_CLOSEST = (764, 220)
		self.TRAC_CLOSEST_VALUE = (814, 220)
		self.TRAC_COLOUR = [0, 255, 255]
		self.TRAC_COUNT = (740, 202)
		self.TRAC_GRADIENT_MIN = [0, 255, 0]
		self.TRAC_GRADIENT_MAX = self.TRAC_COLOUR
		self.TRAC_HEADER = (605, 192)
		self.TRAC_MOST_ACTIVE = (605, 220)
		self.TRAC_MOST_ACTIVE_VALUE = (682, 220)
		self.TRAC_STATUS = (605, 204)
		self.TRAC_STATUS_VALUE = (682, 204)
		self.TRAC_STORM_WIDTH_TEXT = (605, 228)
		self.TRAC_STORM_WIDTH_VALUE = (682, 228)
		self.TRAC_STORMS = (605, 212)
		self.TRAC_STORMS_VALUE = (682, 212)
		self.UPTIME_SIZE = (140, 18)
		self.UPTIME_TEXT = [698, 532]
		self.UPTIME_TEXT_COLOUR = [255, 0, 0]
		self.UNIT_SECTION_COLOUR = [255, 200, 0]
		
		
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		self.alarm_font = None
		self.number_font = None
		self.screen = None
		self.square_font = None
		self.small_number_font = None
		self.time_font = None
		self.uptime_font = None
		
		
		# Updated "constants"
		self.INFO_SIZE = (self.SCREEN_SIZE[0] - self.MAP_SIZE[0], self.MAP_SIZE[1])
		
		self.MINUTE = 60
		self.HOUR = self.MINUTE * 60
		self.DAY = self.HOUR * 24
		
		
		
		# Start setting things up
		import pygame
		import pygame.locals
		
		self.pygame = pygame
		self.pygame_locals = pygame.locals
		
		
		self.pygame.init()
		
		self.screen = self.pygame.display.set_mode(self.SCREEN_SIZE, 0, 32)
		self.pygame.display.set_caption("StormForce XR - Client v%s" % self.client.CLIENT_VERSION)
		
		
		# Fonts
		self.alarm_font = self.pygame.font.Font(self.os.path.join("ttf", "aldo.ttf"), 28)
		self.number_font = self.pygame.font.Font(self.os.path.join("ttf", "lcd2.ttf"), 30)
		self.square_font = self.pygame.font.Font(self.os.path.join("ttf", "micron55.ttf"), 8)
		self.small_number_font = self.pygame.font.Font(self.os.path.join("ttf", "7linedigital.ttf"), 8)
		self.time_font = self.pygame.font.Font(self.os.path.join("ttf", "lcd1.ttf"), 18)
		self.uptime_font = self.pygame.font.Font(self.os.path.join("ttf", "lcd1.ttf"), 18)
		
		
		# Map
		if not self.os.path.exists(self.MAP):
			self.MAP = self.os.path.join("png", "blank.png")
		
		self.BACKGROUND = self.pygame.image.load(self.MAP).convert()
	
	def captureScreen(self, filename):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		self.pygame.image.save(self.screen, filename)
	
	def clearEFM100FieldArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.EFM100_FIELD_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearEFM100ReceiverArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.EFM100_RECEIVER_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250CloseAlarmArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_CLOSE_ALARM_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250CloseArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_CLOSE_VALUE, (120, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250NoiseArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_NOISE_VALUE, (120, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250ReceiverArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_RECEIVER_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250SevereAlarmArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_SEVERE_ALARM_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250SquelchArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_SQUELCH_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearLD250StrikeArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.LD250_STRIKES_VALUE, (120, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearSSBTArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.SSBT_STATUS_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearSSBTManifestoArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.SSBT_MANIFESTO_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearStrikeHistoryArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.STRIKE_GRAPH, (316, 232))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTimeArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.TIME_TEXT, self.TIME_SIZE)
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTRACArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.TRAC_STATUS_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTRACClosestArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.TRAC_CLOSEST_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTRACMostActiveArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.TRAC_MOST_ACTIVE_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTRACStormsArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.TRAC_STORMS_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTRACStormWidthArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.TRAC_STORM_WIDTH_VALUE, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearTRACVersionArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.TRAC_HEADER, (80, 8))
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def clearUptimeArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.pygame.Rect(self.UPTIME_TEXT, self.UPTIME_SIZE)
		self.pygame.draw.rect(self.screen, self.COLOUR_BLACK, rect)
		
		return rect
	
	def disableInput(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		self.pygame.event.set_allowed(None)
	
	def enableInput(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		self.pygame.event.set_blocked(None)
		self.pygame.event.set_allowed([KEYDOWN, QUIT, VIDEOEXPOSE])
	
	def handleEvents(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		self.pygame.key.set_repeat(1000, 100)
		
		while True:
			event = self.pygame.event.wait()
			
			if event.type == self.pygame.locals.QUIT:
				self.client.exitProgram()
			
			elif event.type == self.pygame.locals.KEYDOWN:
				if event.mod & self.pygame.locals.KMOD_CTRL:
					pass
			
				elif event.mod & self.pygame.locals.KMOD_ALT:
					pass
			
				elif event.mod & self.pygame.locals.KMOD_SHIFT:
					pass
				
				else:
					if event.key == self.pygame.locals.K_ESCAPE:
						self.client.exitProgram()
						
					elif event.key == self.pygame.locals.K_INSERT:
						self.log.info("Development: To do, zoom in.")
						
					elif event.key == self.pygame.locals.K_DELETE:
						self.log.info("Development: To do, zoom out.")
						
					elif event.key == self.pygame.locals.K_q:
						self.client.exitProgram()
	
	def progressBar(self, position, startcolour, endcolour, value, maxvalue, thickness):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		r_step = 0
		g_step = 0
		b_step = 0
		
		for x in range(0, value):
			if x > maxvalue:
				break
				
			else:
				# Get the next colour
				colour = [min(max(startcolour[0] + r_step, 0), 255), min(max(startcolour[1] + g_step, 0), 255), min(max(startcolour[2] + b_step, 0), 255)]
				
				# Draw the gradient
				rect = self.pygame.Rect([position[0] + x, position[1]], [1, thickness])
				self.pygame.draw.rect(self.screen, colour, rect)
				
				# Increase the colour stepping
				r_step += (endcolour[0] - startcolour[0]) / maxvalue
				g_step += (endcolour[1] - startcolour[1]) / maxvalue
				b_step += (endcolour[2] - startcolour[2]) / maxvalue
	
	def progressBarColour(self, startcolour, endcolour, value, maxvalue):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		r_step = 0
		g_step = 0
		b_step = 0
		colour = self.TRAC_COLOUR
		
		for x in range(0, value):
			if x > maxvalue:
				break
				
			else:
				# Get the next colour
				colour = [min(max(startcolour[0] + r_step, 0), 255), min(max(startcolour[1] + g_step, 0), 255), min(max(startcolour[2] + b_step, 0), 255)]
				
				# Increase the colour stepping
				r_step += (endcolour[0] - startcolour[0]) / maxvalue
				g_step += (endcolour[1] - startcolour[1]) / maxvalue
				b_step += (endcolour[2] - startcolour[2]) / maxvalue
				
		return colour
	
	def plotStrike(self, strikedistance, strikeangle, isold):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		# By using a bit of trignonmetry we can get the missing values
		#
		#       ^
		#      / |
		#  H  /  |
		#    /   | O
		#   /    |
		#  / )X  |
		# /-------
		#     A
		o = self.math.sin(self.math.radians(strikeangle)) * float(strikedistance)
		a = self.math.cos(self.math.radians(strikeangle)) * float(strikedistance)
		
		rect = None
		
		if not isold:
			if self.client.STRIKE_SHAPE == self.SHAPE_SQUARE:
				# We use a 3x3 rectangle to indicate a strike, where (1,1) is the centre (zero-based)
				rect = self.pygame.Rect([(self.CENTRE_X + o) - 1, (self.CENTRE_Y + -a) - 1], [3, 3])
				self.pygame.draw.rect(self.screen, self.COLOUR_NEW_STRIKE, rect)
				
			elif self.client.STRIKE_SHAPE == self.SHAPE_TRIANGLE:
				points = []
				points.append([self.CENTRE_X + o, self.CENTRE_Y + -a])
				points.append([(self.CENTRE_X + o) - 2, (self.CENTRE_Y + -a) - 2])
				points.append([(self.CENTRE_X + o) + 2, (self.CENTRE_Y + -a) - 2])
				
				rect = self.pygame.draw.polygon(self.screen, self.COLOUR_NEW_STRIKE, points)
				
			elif self.client.STRIKE_SHAPE == self.SHAPE_CIRCLE:
				rect = self.pygame.draw.circle(self.screen, self.COLOUR_NEW_STRIKE, [int(self.CENTRE_X + o), int(self.CENTRE_Y + -a)], 2, 0)
			
		else:
			# Draw a 1-pixel blue strike instead
			rect = self.pygame.Rect([(self.CENTRE_X + o) - 1, (self.CENTRE_Y + -a) - 1], [1, 1])
		
		self.pygame.display.update(rect)
	
	def plotStrikeXY(self, x, y, colour):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = None
		
		if self.client.STRIKE_SHAPE == self.SHAPE_SQUARE:
			rect = self.pygame.Rect([x - 1, y - 1], [3, 3])
			self.pygame.draw.rect(self.screen, colour, rect)
			
		elif self.client.STRIKE_SHAPE == self.SHAPE_TRIANGLE:
			points = []
			points.append([x, y])
			points.append([x - 2, y - 2])
			points.append([x + 2, y - 2])
				
			rect = self.pygame.draw.polygon(self.screen, colour, points)
			
		elif self.client.STRIKE_SHAPE == self.SHAPE_CIRCLE:
			rect = self.pygame.draw.circle(self.screen, colour, [int(x), int(y)], 2, 0)
			
		elif self.client.STRIKE_SHAPE == self.SHAPE_PLUS_1 or self.client.STRIKE_SHAPE == self.SHAPE_PLUS_2:
			points = []
			points.append([x - 1, y - 4])
			points.append([x + 1, y - 4])
			points.append([x + 1, y - 1])
			points.append([x + 4, y - 1])
			points.append([x + 4, y + 1])
			points.append([x + 1, y + 1])
			points.append([x + 1, y + 4])
			points.append([x - 1, y + 4])
			points.append([x - 1, y + 1])
			points.append([x - 4, y + 1])
			points.append([x - 4, y - 1])
			points.append([x - 1, y - 1])
			
			if self.client.STRIKE_SHAPE == self.SHAPE_PLUS_1:
				# Have to fill it in like this otherwise it won't draw it correctly
				rect = self.pygame.draw.polygon(self.screen, self.COLOUR_BLACK, points, 1)
				
				self.pygame.draw.line(self.screen, colour, [x, y - 3], [x, y + 3], 1)
				self.pygame.draw.line(self.screen, colour, [x - 3, y], [x + 3, y], 1)
				
			elif self.client.STRIKE_SHAPE == self.SHAPE_PLUS_2:
				rect = self.pygame.draw.polygon(self.screen, colour, points, 1)
		
		self.pygame.display.update(rect)
	
	def renderScreen(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		# Draw the "base" screen
		self.screen.blit(self.BACKGROUND, (0, 0))
		
		# Side section
		COUNTER_SIZE = [self.INFO_SIZE[0] - 10, 52]
		
		# Top lines
		self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, COUNTER_SIZE[1] - 5], [self.SCREEN_SIZE[0], COUNTER_SIZE[1] - 5], 1)
		self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 42], [self.SCREEN_SIZE[0], COUNTER_SIZE[1] + 42], 1)
		self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 90], [self.SCREEN_SIZE[0], COUNTER_SIZE[1] + 90], 1)
		self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 138], [self.SCREEN_SIZE[0], COUNTER_SIZE[1] + 138], 1)
		self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 186], [self.SCREEN_SIZE[0], COUNTER_SIZE[1] + 186], 1)
		self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, COUNTER_SIZE[1] + 234], [self.SCREEN_SIZE[0], COUNTER_SIZE[1] + 234], 1)
		
		
		# Starting point
		self.clearLD250CloseAlarmArea()
		self.clearLD250ReceiverArea()
		self.clearLD250SevereAlarmArea()
		self.clearLD250SquelchArea()
		self.clearLD250CloseArea()
		self.clearLD250NoiseArea()
		self.clearLD250StrikeArea()
		
		self.clearEFM100FieldArea()
		self.clearEFM100ReceiverArea()
		
		self.clearTRACArea()
		self.clearTRACMostActiveArea()
		self.clearTRACStormsArea()
		self.clearTRACStormWidthArea()
		
		self.clearSSBTArea()
		self.clearSSBTManifestoArea()
		
		
		self.updateLD250CloseArea(0, 0)
		self.updateLD250NoiseArea(0, 0)
		self.updateLD250StrikeArea(0, 0, 0)
		
		self.updateTRACClosestArea("")
		self.updateTRACMostActiveArea("")
		self.updateTRACStatus(False)
		self.updateTRACStormsArea(0)
		self.updateTRACStormWidthArea(0)
		
		
		# LD-250
		surface = self.square_font.render("LD-250", False, self.UNIT_SECTION_COLOUR)
		self.screen.blit(surface, self.LD250_HEADER)
		
		surface = self.square_font.render("RECEIVER:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.LD250_RECEIVER)
		
		surface = self.square_font.render("CLOSE ALARM:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.LD250_CLOSE_ALARM)
		
		surface = self.square_font.render("SEVERE ALARM:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.LD250_SEVERE_ALARM)
		
		surface = self.square_font.render("SQUELCH:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.LD250_SQUELCH)
		
		surface = self.square_font.render("STRIKES:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.LD250_STRIKES)
		
		surface = self.square_font.render("CLOSE:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.LD250_CLOSE)
		
		surface = self.square_font.render("NOISE:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.LD250_NOISE)
		
		
		# EFM-100
		surface = self.square_font.render("EFM-100", False, self.UNIT_SECTION_COLOUR)
		self.screen.blit(surface, self.EFM100_HEADER)
		
		surface = self.square_font.render("RECEIVER:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.EFM100_RECEIVER)
		
		surface = self.square_font.render("FIELD LEVEL:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.EFM100_FIELD)
		
		
		# We'll set some of values here
		# LD-250
		surface = self.square_font.render("Inactive", False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(surface, self.LD250_CLOSE_ALARM_VALUE)
		
		surface = self.square_font.render("Inactive", False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(surface, self.LD250_SEVERE_ALARM_VALUE)
		
		surface = self.square_font.render("Inactive", False, self.COLOUR_ALARM_ACTIVE)
		self.screen.blit(surface, self.LD250_RECEIVER_VALUE)
		
		surface = self.square_font.render("%s" % self.LDUNIT_SQUELCH, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(surface, self.LD250_SQUELCH_VALUE)
		
		
		# EFM-100
		surface = self.square_font.render("Inactive", False, self.COLOUR_ALARM_ACTIVE)
		self.screen.blit(surface, self.EFM100_RECEIVER_VALUE)
		
		
		# TRAC
		surface = self.square_font.render("TRAC", False, self.UNIT_SECTION_COLOUR)
		self.screen.blit(surface, self.TRAC_HEADER)
		
		surface = self.square_font.render("STATUS:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.TRAC_STATUS)
		
		surface = self.square_font.render("STORMS:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.TRAC_STORMS)
		
		surface = self.square_font.render("MOST ACTIVE:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.TRAC_MOST_ACTIVE)
		
		surface = self.square_font.render("CLOSEST:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.TRAC_CLOSEST)
		
		surface = self.square_font.render("WIDTH:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.TRAC_STORM_WIDTH_TEXT)
		
		
		# SSBT - StormForce Strike Bi/Triangulation
		surface = self.square_font.render("StormForce Strike Bi/Triangulation (SSBT)", False, self.UNIT_SECTION_COLOUR)
		self.screen.blit(surface, self.SSBT_HEADER)
		
		surface = self.square_font.render("STATUS:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.SSBT_STATUS)
		
		surface = self.square_font.render("MANIFESTO:", False, self.COLOUR_WHITE)
		self.screen.blit(surface, self.SSBT_MANIFESTO)
		
		if self.SSBT_ENABLED:
			surface = self.square_font.render("Active", False, self.COLOUR_ALARM_INACTIVE)
			
		else:
			surface = self.square_font.render("Inactive", False, self.COLOUR_ALARM_ACTIVE)
			
		self.screen.blit(surface, self.SSBT_STATUS_VALUE)
		
		if self.SSBT_ENABLED:
			self.updateSSBTManifesto(self.MANIFESTO_ELECTION)
		
		
		
		# Side line
		self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0], 0], [self.MAP_SIZE[0], self.MAP_SIZE[1] * 2], 1)
		self.pygame.draw.line(self.screen, self.COLOUR_RANGE_300, [self.MAP_SIZE[0] + 1, 0], [self.MAP_SIZE[0] + 1, self.MAP_SIZE[1]], 1)
		
		# Time line
		self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, self.SCREEN_SIZE[1] - 40], [self.SCREEN_SIZE[0], self.SCREEN_SIZE[1] - 40], 1)
		self.pygame.draw.line(self.screen, self.COLOUR_SIDELINE, [self.MAP_SIZE[0] + 2, self.SCREEN_SIZE[1] - 80], [self.SCREEN_SIZE[0], self.SCREEN_SIZE[1] - 80], 1)
		
		surface = self.square_font.render("DATETIME", False, self.UNIT_SECTION_COLOUR)
		self.screen.blit(surface, [self.MAP_SIZE[0] + 5, 561])
		
		surface = self.square_font.render("UPTIME", False, self.UNIT_SECTION_COLOUR)
		self.screen.blit(surface, [self.MAP_SIZE[0] + 5, 521])
		
		# Range circles
		if self.client.SHOW_RANGE_CIRCLES:
			self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_25, [self.CENTRE_X, self.CENTRE_Y], 25, 1)
			self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_50, [self.CENTRE_X, self.CENTRE_Y], 50, 1)
			self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_100, [self.CENTRE_X, self.CENTRE_Y], 100, 1)
			self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_150, [self.CENTRE_X, self.CENTRE_Y], 150, 1)
			self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_200, [self.CENTRE_X, self.CENTRE_Y], 200, 1)
			self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_250, [self.CENTRE_X, self.CENTRE_Y], 250, 1)
			self.pygame.draw.circle(self.screen, self.COLOUR_RANGE_300, [self.CENTRE_X, self.CENTRE_Y], 300, 1)
		
		if self.client.SHOW_CROSSHAIR:
			# Crosshair V
			self.pygame.draw.line(self.screen, self.COLOUR_CROSSHAIR, [self.CENTRE_X, self.CENTRE_Y - 3], [self.CENTRE_X, self.CENTRE_Y + 3], 1)
			
			# Crosshair H
			self.pygame.draw.line(self.screen, self.COLOUR_CROSSHAIR, [self.CENTRE_X - 3, self.CENTRE_Y], [self.CENTRE_X + 3, self.CENTRE_Y], 1)
		
		
		# Copyright text
		uc_split = "Unknown"
		
		try:
			s = self.xmlrpclib.ServerProxy(self.client.STORMFORCEXR_SERVER)
			data = self.client.extractDataset(s.serverDetails().data)
			s = None
			
			for row in data:
				server_details = "%s v%s\n%s\n\n%s" % (str(row["ServerApplication"]), str(row["ServerVersion"]), str(row["ServerCopyright"]), str(row["StrikeCopyright"]))
				uc_split = server_details.split("\n")
				
				break
			
		except Exception, ex:
			self.log.error(str(ex))
		
		
		y_point = 3
		
		for uc_text in uc_split:
			surface = self.square_font.render(uc_text, True, self.COLOUR_BLACK)
			self.screen.blit(surface, [6, y_point])
			
			surface = self.square_font.render(uc_text, True, self.COLOUR_WHITE)
			self.screen.blit(surface, [5, y_point - 1])
			
			y_point += 8
		
		
		surface = self.square_font.render(self.COPYRIGHT_MESSAGE_1, True, self.COLOUR_BLACK)
		self.screen.blit(surface, [6, 580])
		
		surface = self.square_font.render(self.COPYRIGHT_MESSAGE_1, True, self.COLOUR_WHITE)
		self.screen.blit(surface, [5, 579])
		
		
		surface = self.square_font.render(self.COPYRIGHT_MESSAGE_2, True, self.COLOUR_BLACK)
		self.screen.blit(surface, [6, 588])
		
		surface = self.square_font.render(self.COPYRIGHT_MESSAGE_2, True, self.COLOUR_WHITE)
		self.screen.blit(surface, [5, 587])
		
		
		# Range text
		surface = self.square_font.render("Range: %dmiles" % self.client.ZOOM_DISTANCE, True, self.COLOUR_BLACK)
		self.screen.blit(surface, [514, 588])
		
		surface = self.square_font.render("Range: %dmiles" % self.client.ZOOM_DISTANCE, True, self.COLOUR_WHITE)
		self.screen.blit(surface, [513, 587])
		
		
		# Update when done
		self.pygame.display.update()
	
	def start(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		self.renderScreen()
		self.handleEvents()
	
	def updateEFM100FieldArea(self, field):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearEFM100FieldArea()
		
		field_surface = self.square_font.render("%2.2fKV/m" % field, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(field_surface, self.EFM100_FIELD_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateEFM100ReceiverArea(self, status):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearEFM100ReceiverArea()
		
		colour = None
		
		if status == "Active":
			colour = self.COLOUR_ALARM_INACTIVE
			
		else:
			colour = self.COLOUR_ALARM_ACTIVE
		
		receive_surface = self.square_font.render(status, False, colour)
		self.screen.blit(receive_surface, self.EFM100_RECEIVER_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250CloseArea(self, close_minute, close_total):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearLD250CloseArea()
		
		close_surface = self.small_number_font.render("%03d %06d" % (close_minute, close_total), False, self.CLOSE_TEXT_COLOUR)
		self.screen.blit(close_surface, self.LD250_CLOSE_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250CloseAlarmArea(self, status):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearLD250CloseAlarmArea()
		
		text = ""
		colour = None
		
		
		if status == 0:
			text = "Inactive"
			colour = self.COLOUR_ALARM_INACTIVE
			
		else:
			text = "Active"
			colour = self.COLOUR_ALARM_ACTIVE
		
		close_surface = self.square_font.render(text, False, colour)
		self.screen.blit(close_surface, self.LD250_CLOSE_ALARM_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250NoiseArea(self, noise_minute, noise_total):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearLD250NoiseArea()
		
		noise_surface = self.small_number_font.render("%03d %06d" % (noise_minute, noise_total), False, self.NOISE_TEXT_COLOUR)
		self.screen.blit(noise_surface, self.LD250_NOISE_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250ReceiverArea(self, status):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearLD250ReceiverArea()
		
		if status == "Active":
			colour = self.COLOUR_ALARM_INACTIVE
			
		else:
			colour = self.COLOUR_ALARM_ACTIVE
		
		receive_surface = self.square_font.render(status, False, colour)
		self.screen.blit(receive_surface, self.LD250_RECEIVER_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250SevereAlarmArea(self, status):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearLD250SevereAlarmArea()
		
		text = ""
		colour = None
		
		
		if status == 0:
			text = "Inactive"
			colour = self.COLOUR_ALARM_INACTIVE
			
		else:
			text = "Active"
			colour = self.COLOUR_ALARM_ACTIVE
		
		severe_surface = self.square_font.render(text, False, colour)
		self.screen.blit(severe_surface, self.LD250_SEVERE_ALARM_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250SquelchArea(self, squelch):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearLD250SquelchArea()
		
		squelch_surface = self.square_font.render("%d" % squelch, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(squelch_surface, self.LD250_SQUELCH_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateLD250StrikeArea(self, strikes_minute, strikes_total, strikes_oor):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearLD250StrikeArea()
		
		strike_surface = self.small_number_font.render("%03d %06d %03d" % (strikes_minute, strikes_total, strikes_oor), False, self.STRIKE_TEXT_COLOUR)
		self.screen.blit(strike_surface, self.LD250_STRIKES_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateSSBTManifesto(self, status):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearSSBTManifestoArea()
		
		text = ""
		colour = None
		
		if status == self.MANIFESTO_ELECTION:
			text = "Election"
			colour = self.COLOUR_YELLOW
			
		elif status == self.MANIFESTO_PUBLISHED:
			text = "Published"
			colour = self.COLOUR_ALARM_INACTIVE
			
		elif status == self.MANIFESTO_UNPUBLISHED:
			text = "Unpublished"
			colour = self.COLOUR_ALARM_ACTIVE
		
		ssbt_surface = self.square_font.render(text, False, colour)
		self.screen.blit(ssbt_surface, self.SSBT_MANIFESTO_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateStrikeHistoryArea(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearStrikeHistoryArea()
		surface = None
		
		if self.os.path.exists(self.client.GRAPH_MBM_FULL_PATH):
			g = self.pygame.image.load(self.client.GRAPH_MBM_FULL_PATH).convert()
			self.screen.blit(g, self.STRIKE_GRAPH)
			
			surface = self.square_font.render("STRIKE HISTORY - LAST 60 MINUTES", False, self.UNIT_SECTION_COLOUR)
			
		else:
			surface = self.square_font.render("STRIKE HISTORY - NOT AVAILABLE", False, self.UNIT_SECTION_COLOUR)
		
		self.screen.blit(surface, self.STRIKE_GRAPH_HEADER)
		self.pygame.display.update(rect)
	
	def updateTime(self):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		t = self.datetime.now()
		
		current_time = str(t.strftime("%d/%m/%Y %H:%M:%S"))
		
		rect = self.clearTimeArea()
		time_surface = self.time_font.render(current_time, True, self.TIME_TEXT_COLOUR)
		self.screen.blit(time_surface, self.TIME_TEXT)
		
		self.pygame.display.update(rect)
	
	def updateTRACClosestArea(self, trac_closest):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearTRACClosestArea()
		
		surface = self.square_font.render("%s" % trac_closest, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(surface, self.TRAC_CLOSEST_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateTRACMostActiveArea(self, trac_most_active):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearTRACMostActiveArea()
		
		surface = self.square_font.render("%s" % trac_most_active, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(surface, self.TRAC_MOST_ACTIVE_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateTRACStatus(self, isactive):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearTRACArea()
		
		text = ""
		colour = None
		
		if not isactive:
			text = "Inactive"
			colour = self.COLOUR_ALARM_INACTIVE
			
		elif isactive:
			text = "Active"
			colour = self.COLOUR_ALARM_ACTIVE
			
		else:
			text = "Busy"
			colour = self.COLOUR_YELLOW
		
		trac_surface = self.square_font.render(text, False, colour)
		self.screen.blit(trac_surface, self.TRAC_STATUS_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateTRACStormsArea(self, trac_storms_total):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearTRACStormsArea()
		
		surface = self.square_font.render("%d" % trac_storms_total, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(surface, self.TRAC_STORMS_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateTRACStormWidthArea(self, storm_width):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearTRACStormWidthArea()
		
		surface = self.square_font.render("%d" % storm_width, False, self.COLOUR_ALARM_INACTIVE)
		self.screen.blit(surface, self.TRAC_STORM_WIDTH_VALUE)
		
		self.pygame.display.update(rect)
	
	def updateTRACVersionArea(self, version):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		rect = self.clearTRACVersionArea()
		
		surface = self.square_font.render("TRAC v%s" % version, False, self.UNIT_SECTION_COLOUR)
		self.screen.blit(surface, self.TRAC_HEADER)
		
		self.pygame.display.update(rect)
	
	def updateUptime(self, uptime):
		if self.DEBUG_MODE:
			self.log.info("Starting...")
		
		
		days = int(uptime / self.DAY)
		hours = int((uptime % self.DAY) / self.HOUR)
		minutes = int((uptime % self.HOUR) / self.MINUTE)
		seconds = int(uptime % self.MINUTE)
		
		suptime = "%04d:%02d:%02d:%02d" % (days, hours, minutes, seconds)
		
		rect = self.clearUptimeArea()
		uptime_surface = self.uptime_font.render(suptime, True, self.UPTIME_TEXT_COLOUR)
		self.screen.blit(uptime_surface, self.UPTIME_TEXT)
		
		self.pygame.display.update(rect)

class XRGraphs():
	def __init__(self):
		from danlog import DanLog
		
		import os
		
		
		self.log = DanLog("XRGraphs")
		self.mpl_available = False
		self.mpl_pyplot = None
		self.numpy = None
		self.os = os
		self.square_font = None
		
		
		try:
			import matplotlib.font_manager
			import matplotlib.pyplot
			import numpy
			
			
			self.mpl_fontman = matplotlib.font_manager
			self.mpl_pyplot = matplotlib.pyplot
			self.numpy = numpy
			self.square_font = self.mpl_fontman.FontProperties(fname = self.os.path.join("ttf", "micron55.ttf"))
			
			self.mpl_available = True
			
		except Exception, ex:
			self.dispose()
			
			self.log.error("Graphs will not be available due to import exception, please ensure \"matplotlib\" and \"numpy\" have been installed.")
			self.log.error(str(ex))
	
	def available(self):
		return self.mpl_available
	
	def dispose(self):
		self.mpl_available = False
		self.mpl_pyplot = None
		self.numpy = None
		self.square_font = None
	
	def lastHourOfStrikesByMinute(self, rows, filename):
		if self.available():
			try:
				plt = self.mpl_pyplot
				
				
				# 316x232
				fig = plt.figure(figsize = (3.16, 2.32))
				ax = fig.add_subplot(111)
				
				for child in ax.get_children():
					if hasattr(child, "set_color"):
						child.set_color("#000000")
				
				
				# Transpose the data
				xdata = []
				ydata = []
				
				for x in xrange(0, 60):
					xdata.append(x)
					ydata.append(0)
				
				for x in rows:
					ydata[int(x["StrikeAge"])] = int(x["NumberOfStrikes"])
				
				
				# Plot the data and alter the graph apperance
				plt.plot(xdata, ydata, marker = None, color = "#00ff00")
				
				
				# Adjust the y-axis min and max range to avoid it from going negative (happens when there is no strikes in the dataset)
				cx = plt.axis()
				
				if float(cx[3]) < 1.:
					plt.axis([int(cx[0]), int(cx[1]), 0, 1])
					
				else:
					plt.axis([int(cx[0]), int(cx[1]), 0, int(cx[3])])
				
				ax.spines["top"].set_color("white")
				ax.spines["bottom"].set_color("white")
				ax.spines["left"].set_color("white")
				ax.spines["right"].set_color("white")
				
				
				# Can't get the font to NOT use antialiasing, so need to make the font slightly better to make it readable
				for tick in ax.xaxis.get_major_ticks():
					tick.label1.set_fontproperties(self.square_font)
				
				for tick in ax.yaxis.get_major_ticks():
					tick.label1.set_fontproperties(self.square_font)
				
				ax.tick_params(axis = "x", colors = "white", labelsize = 7)
				ax.tick_params(axis = "y", colors = "white", labelsize = 7)
				
				plt.savefig(filename, facecolor = "black", edgecolor = "none")
				
			except Exception, ex:
				self.log.error(str(ex))


########
# Main #
########
if __name__ == "__main__":
	l = None
	
	try:
		from danlog import DanLog
		
		
		l = DanLog("Main")
		l.info("Preparing...")
		
		sxr = SXRClient()
		sxr.main()
		sxr = None
		
	except Exception, ex:
		if l is not None:
			l.fatal(str(ex))
			
		else:
			print "Exception: %s" % str(ex)
