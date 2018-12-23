#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcaddon, xbmcgui
import urllib2, json, time

# Addon
__addon__ = xbmcaddon.Addon()
addonname = __addon__.getAddonInfo('name')
addonid = __addon__.getAddonInfo('id')
addonicon = xbmc.translatePath(__addon__.getAddonInfo('icon'))

# Settings
sNightscout = __addon__.getSetting('nightscout')
sAlarm = __addon__.getSetting('alarm')

# Load JSON from url
urlEntries = urllib2.urlopen(sNightscout + '/api/v1/entries/sgv.json?count=2')
jsonEntries = json.load(urlEntries)
urlStatus = urllib2.urlopen(sNightscout + '/api/v1/status.json')
jsonStatus = json.load(urlStatus)

# Read glucose values
iSgv = int(jsonEntries[0]['sgv'])
iLastSgv = int(jsonEntries[1]['sgv'])

# Read unix date values diff
iDate = int(jsonEntries[0]['date'])
iLastDate = int(jsonEntries[1]['date'])
iServerTimeEpoch = int(jsonStatus['serverTimeEpoch'])
iMsServerTimeEpoch = iServerTimeEpoch - iDate
iMin = iMsServerTimeEpoch / 60000
iSec = iMsServerTimeEpoch / 6000

sStatus = str(jsonStatus['status'])
sName = str(jsonStatus['name'])
sUnits = str(jsonStatus['settings']['units'])

# Alarm with int values
iBgHigh = int(jsonStatus['settings']['thresholds']['bgHigh'])
iBgTargetTop = int(jsonStatus['settings']['thresholds']['bgTargetTop'])
iBgTargetBottom = int(jsonStatus['settings']['thresholds']['bgTargetBottom'])
iBgLow = int(jsonStatus['settings']['thresholds']['bgLow'])

# Check status of Nightscout
if sStatus <> 'ok':
	xbmcgui.Dialog().notification(addonname, 'Please check the settings and the availability of URL! • ' + 'Status: [' + sStatus + ']', xbmcgui.NOTIFICATION_ERROR)

# Check if sUnits: mmol
i_fSgv = ''
i_fLastSgv = ''
if sUnits == 'mmol':
	i_fSgv = round(float(iSgv * 0.0555), 1)
	i_fLastSgv = round(float(iLastSgv * 0.0555), 1)
else:
	i_fSgv = iSgv
	i_fLastSgv = iLastSgv

# Calculate delta
i_fDelta = float(i_fSgv - i_fLastSgv)
sDelta = ''
if i_fDelta > 0:
	sDelta = str('+')
if i_fDelta == 0:
	sDelta = str('±')

# Notification
sHeader = str(i_fSgv) + ' ' + sUnits + ' • ' + sDelta + str(i_fDelta)
sMessage = 'just now'

# Alarm
bAlarm = ''
if iSgv <= iBgLow or iSgv >= iBgHigh or iSgv <= iBgTargetBottom or iSgv >= iBgTargetTop:
	bAlarm = True
else:
	bAlarm = False

if iMin == 0 and iSec == 0 or iSec == 1 or iSec == 2:
	xbmcgui.Dialog().notification(sHeader, sMessage, addonicon, 5000, bAlarm)
	
# Close url
urlEntries.close()
urlStatus.close()

# Sleep and execute
xbmc.sleep(1000)
xbmc.executebuiltin("XBMC.RunAddon(" + addonid + ")")