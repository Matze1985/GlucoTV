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
xbmcgui.Dialog().notification(addonname, str('Add-on started ...'), xbmcgui.NOTIFICATION_INFO)

while 1:
	# Settings
	sNightscout = __addon__.getSetting('nightscout')
	sSound = __addon__.getSetting('sound')
	sNotification = __addon__.getSetting('notification')

	# Load JSON from url
	try:
		urlEntries = urllib2.urlopen(sNightscout + str('/api/v1/entries/sgv.json?count=2'))
		jsonEntries = json.load(urlEntries)	
		urlStatus = urllib2.urlopen(sNightscout + str('/api/v1/status.json'))
		jsonStatus = json.load(urlStatus)
	except urllib2.HTTPError, e:
		xbmcgui.Dialog().notification(addonname, str('HTTP-Error: ') + str(e.code), xbmcgui.NOTIFICATION_ERROR)
		#sys.exit()
	except urllib2.URLError, e:
		xbmcgui.Dialog().notification(addonname, str('URL-Error: ') + str(e.args), xbmcgui.NOTIFICATION_ERROR)
		#sys.exit()

	# Read glucose values
	iSgv = int(jsonEntries[0]['sgv'])
	iLastSgv = int(jsonEntries[1]['sgv'])

	# Read unix date values diff
	iDate = int(jsonEntries[0]['date'])
	iLastDate = int(jsonEntries[1]['date'])
	iServerTimeEpoch = int(jsonStatus['serverTimeEpoch'])
	
	# Calculate and strings
	iMsServerTimeEpochDate = int(iServerTimeEpoch - iDate)
	iMsInterval = int(iDate - iLastDate)
	iMinInterval = int(iMsInterval / 60000 + 1)
	iMinSecondInterval = int(iMinInterval * 2)
	iMin = int(iMsServerTimeEpochDate / 60000)

	# Calculate ms for sleep 
	iMsWait = ''
	if iMin == 0:
		iMsWait = int(60000 - iMsServerTimeEpochDate)
	else:
		iMsWait = int(iMsServerTimeEpochDate / iMin)

	sStatus = str(jsonStatus['status'])
	sName = str(jsonStatus['name'])
	sUnits = str(jsonStatus['settings']['units'])

	# Alarm with int values
	iBgHigh = int(jsonStatus['settings']['thresholds']['bgHigh'])
	iBgTargetTop = int(jsonStatus['settings']['thresholds']['bgTargetTop'])
	iBgTargetBottom = int(jsonStatus['settings']['thresholds']['bgTargetBottom'])
	iBgLow = int(jsonStatus['settings']['thresholds']['bgLow'])

	# Check status of Nightscout
	if 'ok' not in sStatus:
		xbmcgui.Dialog().notification(addonname, str('Please check the settings and the availability of URL! • ') + str('Status: [' + sStatus + ']'), xbmcgui.NOTIFICATION_ERROR)

	# Check if sUnits: mmol
	i_fSgv = ''
	i_fLastSgv = ''
	if sUnits == str('mmol'):
		i_fSgv = round(float(iSgv * 0.0555), 1)
		i_fLastSgv = round(float(iLastSgv * 0.0555), 1)
	else:
		i_fSgv = iSgv
		i_fLastSgv = iLastSgv

	# Calculate delta
	sTmpDelta = ''
	i_fDelta = float(i_fSgv - i_fLastSgv)
	sDirection = str(jsonEntries[0]['direction'])
	if i_fSgv < i_fLastSgv:
		if sDirection == str('FortyFiveUp') or sDirection == str('SingleUp') or sDirection == str('DoubleUp'):
			sTmpDelta = sTmpDelta.replace('-', '')
			i_fDelta = float(sTmpDelta)
	
	sDelta = ''
	if i_fDelta > 0:
		sDelta = str('+')
	if i_fDelta == 0:
		sDelta = str('±')

	if sUnits == str('mg/dl'):
		i_fDelta = int(i_fDelta)
	else:
		i_fDelta = round(i_fDelta, 1)

	# Notification
	sMin = str(iMin)
	sGlucose = str(i_fSgv) + str(' ') + sUnits + str(' • ') + sDelta + str(i_fDelta)
	sJustNow = str('just now')
	sMinAgo = str(iMin) + str(' min ago')
	
	# Color of strings
	sColorYellow = str('[COLOR yellow]')
	sColorRed = str('[COLOR red]')
	sColor = str('[/COLOR]')

	# Alerts - Red color
	if iSgv <= iBgLow or iSgv >= iBgHigh or iSgv <= iBgTargetBottom or iSgv >= iBgTargetTop:
		sGlucose = sColorRed + sGlucose + sColor
	
	# Sound - Notification
	bSound = False
	if sSound == str('On'):
		bSound = True

	# Check of glucose after every interval for new updates
	if sMin.endswith(str(iMinInterval)[-1:]) or sMin.endswith(str(iMinSecondInterval)[-1:]):
		for i in range(6):
			xbmc.sleep(int(1000))
			if iMin == 0:
				break

	# Check of glucose
	if iMin == 0:
		xbmcgui.Dialog().notification(sGlucose, sJustNow, addonicon, 5000, bSound)
	if sMin.endswith(str(iMinInterval)[-1:]) or sMin.endswith(str(iMinSecondInterval)[-1:]) and iMin >= iMinInterval:
		sMinAgo = sColorYellow + sMinAgo + sColor
		xbmcgui.Dialog().notification(sGlucose, sMinAgo, addonicon, 5000, bSound)
	xbmc.sleep(int(iMsWait))
	
	# Close url
	urlEntries.close()
	urlStatus.close()