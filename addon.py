#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcaddon, xbmcgui
import urllib2, json

# Addon
__addon__ = xbmcaddon.Addon()
addonname = __addon__.getAddonInfo('name')
addonid = __addon__.getAddonInfo('id')
addonicon = xbmc.translatePath(__addon__.getAddonInfo('icon'))

# Settings and API from Nightscout
nightscout = __addon__.getSetting('nightscout')

# Load JSON from url 
urlEntries = urllib2.urlopen(nightscout + '/api/v1/entries/sgv.json?count=2')
jsonEntries = json.load(urlEntries)
urlStatus = urllib2.urlopen(nightscout + '/api/v1/status.json')
jsonStatus = json.load(urlStatus)

# Read all values
sDirection = str("DoubleUp")
iSgv = int(jsonEntries[0]['sgv']) 
iLastSgv = int(jsonEntries[1]['sgv']) 
sStatus = str(jsonStatus['status'])
sName = str(jsonStatus['name'])
sUnits = str(jsonStatus['settings']['units'])

# Alarm with int values
iBgHigh = int(jsonStatus['settings']['thresholds']['bgHigh'])
iBgTargetTop = int(jsonStatus['settings']['thresholds']['bgTargetTop'])
iBgTargetBottom = int(jsonStatus['settings']['thresholds']['bgTargetBottom'])
iBgLow = int(jsonStatus['settings']['thresholds']['bgLow'])

# Check if sUnits: mmol
i_fSgv = ''
i_fLastSgv = ''
if sUnits == 'mmol':
	i_fSgv = round(float(iSgv / 18.01559 * 10 / 10), 1)
	i_fLastSgv = round(float(iLastSgv / 18.01559 * 10 / 10), 1)
	
# Calculate delta
i_fDelta = round(float(i_fSgv - i_fLastSgv), 1)	

# Notification
xbmc.executebuiltin('Notification(%s, %s, %s, %s)'%(sName, str(i_fSgv) + ' ' + sUnits + " " + str(i_fDelta), sTrend, addonicon))

# Close url
urlStatus.close()
urlEntries.close()