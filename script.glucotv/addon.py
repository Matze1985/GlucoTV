#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc, xbmcaddon, xbmcgui
import urllib2, json

# Addon
__addon__ = xbmcaddon.Addon()
addonname = __addon__.getAddonInfo('name')
addonid = __addon__.getAddonInfo('id')
addonicon = xbmc.translatePath(__addon__.getAddonInfo('icon'))

# Info dialog for starting progran
xbmcgui.Dialog().notification(addonname, 'Program started successfully!', xbmcgui.NOTIFICATION_INFO)

while 1:
	# Settings
	sNightscout = __addon__.getSetting('nightscout')
	sAlarm = __addon__.getSetting('alarm')
	sNotification = __addon__.getSetting('notification')

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
	iMsServerTimeEpochDate = iServerTimeEpoch - iDate
	iMin = iMsServerTimeEpochDate / 60000

	# Calculate ms for waiting
	iMsWait = ''
	if iMin == 0:
		iMsWait = iMsServerTimeEpochDate + 60000
	else:
		iMsWait = iMsServerTimeEpochDate / iMin

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
	sMessage1 = str('just now')
	sMessage2 = str(iMin) + str(' min ago')

	if sNotification == '1 sec':
		iNotificationTime = 1000
	if sNotification == '2 sec':
		iNotificationTime = 2000
	if sNotification == '3 sec':
		iNotificationTime = 3000
	if sNotification == '4 sec':
		iNotificationTime = 4000
	if sNotification == '5 sec':
		iNotificationTime = 5000
	if sNotification == '6 sec':
		iNotificationTime = 6000
	if sNotification == '7 sec':
		iNotificationTime = 7000
	if sNotification == '8 sec':
		iNotificationTime = 8000
	if sNotification == '9 sec':
		iNotificationTime = 9000
	if sNotification == '10 sec':
		iNotificationTime = 10000

	# Alarm
	bAlarm = ''
	if iSgv <= iBgLow or iSgv >= iBgHigh or iSgv <= iBgTargetBottom or iSgv >= iBgTargetTop or iMin >= 10:
		bAlarm = True
	else:
		bAlarm = False
	
	if iMin == 0:
		xbmcgui.Dialog().notification(sHeader, sMessage1, addonicon, iNotificationTime, bAlarm)
	if iMin >= 10:
		xbmcgui.Dialog().notification(sHeader, sMessage2, addonicon, iNotificationTime, bAlarm)
	
	# Close url
	urlEntries.close()
	urlStatus.close()

	# Sleep and execute
	xbmc.sleep(iMsWait)