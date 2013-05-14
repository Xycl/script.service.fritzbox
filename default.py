# Open Source Initiative OSI - The MIT License (MIT):Licensing
#[OSI Approved License]
#The MIT License (MIT)

#Copyright (c) 2011 N.K.

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


# ################################################################################
# author: Xycl, nk
# ################################################################################


__addonname__    = "script.service.fritzbox"

import xbmc, xbmcaddon
import socket
import os
import errno
from types import *
from time import sleep
import threading

# own imports
import resources.lib.fritzAddressbook as fritzAddressbook
import resources.lib.common as common
from resources.lib.service import IncomingCallThread

# Addressbook for lookup
xbmctelefonbuch = {}





DEFAULT_IMG = xbmc.translatePath(os.path.join( "special://home/", "addons", __addonname__, "media","default.png"))

# Get settings
ip = common.getaddon_setting( "S_IP" ) # return FritzIP setting value 
dur = common.getaddon_setting( "S_DURATION" ) # return Anzeigedauer
durdict = {'0': '1000','1': '2000' ,'2':'3000','3':'4000','4':'5000','5':'8000','6':'10000','7':'15000','8':'0'}
duration = durdict.get(dur, 5000) # Unit conversion Seconds_2_Milliseconds, NotificationDialog wants Milliseconds

useFritzAB = common.getaddon_setting( "AB_Fritzadress" )
fritzAddressURL = common.getaddon_setting( "AB_Adressbookpath")
PicFolder = common.getaddon_setting( "AB_Pics" )
#debuggen = __settings__.getSetting("S_DEBUG")

parameterstring = "Fritzbox: Ip Adresse definiert als '%s'" % ( ip)
common.log('',parameterstring)


def errorMsg(aList):
    xbmc.log("Unhandled State")


def handleOutgoingCall(aList):
    #datum;CALL;ConnectionID;Nebenstelle;GenutzteNummer;AngerufeneNummer;
    #[192.168.178.1] 03.01.12 22:09:56;CALL;0;0;123456;017500000;SIP1;
    datum, funktion, connectionID, Nebenstelle, GenutzteNummer, AngerufeneNummer, sip,  leer = aList
    logtext = ('Ausgehender Anruf an %s von Nr: %s, am %s' % (AngerufeneNummer, GenutzteNummer, datum))
    heading = "Ausgehender Anruf"
    text = "Angerufene Nr. %s von Apparat Nr: %s" % (AngerufeneNummer, GenutzteNummer)
    common.log('',logtext)
    #xbmc.executebuiltin("Notification("+heading+","+text+","+duration+","+DEFAULT_IMG+")")
    common.show_notification(heading, text, duration, DEFAULT_IMG)


def handleIncomingCall(aList):
    #datum;RING;ConnectionID;Anrufer-Nr;Angerufene-Nummer;sip;
    #[192.168.178.1] 03.01.12 21:52:21;RING;0;017100000;012345;SIP2;
    datum, funktion, connectionID, anruferNR, angerufeneNR, sip, leer = aList
    logtext = ('Eingehender Anruf von %s auf Apparat %s' % (aList[3], aList[4]))
    heading = 'Eingehender Anruf'
    anrufer = xbmctelefonbuch.get(aList[3],'Unbenannt')
    PIC = xbmc.translatePath(os.path.join(PicFolder,aList[3]+".png"))
    text = 'von %s [%s]' % (anrufer, aList[3])
    common.log('',"FRIIIITZ: " + PIC)
    common.log('',logtext)
    try:
        open(PIC)
    except:
        PIC = DEFAULT_IMG
     
    #xbmc.executebuiltin("Notification("+heading+","+text+","+duration+","+PIC+")")
    common.show_notification(heading, text, duration, PIC)
    

def handleConnected(aList):
    #datum;CONNECT;ConnectionID;Nebenstelle;Nummer;
    datum, funktion, connectionID, nebenstelle, nummer, leer = aList
    logtext = ('Verbunden mit %s' % (nummer))
    #print text
    heading = 'Verbindung hergestellt'
    text = 'mit %s' % (nummer)
    common.log('',logtext)
    #xbmc.executebuiltin("Notification("+heading+","+text+","+duration+","+DEFAULT_IMG+")")
    common.show_notification(heading, text, duration, DEFAULT_IMG)
    

def handleDisconnected(aList):
    #datum;DISCONNECT;ConnectionID;dauerInSekunden;
    #[192.168.178.1] 03.01.12 22:12:56;DISCONNECT;0;0;
    datum, funktion, connectionID, dauer,  leer = aList
    text = ('Anrufdauer: %i Minuten' % (int(int(dauer)/60)))
    heading = "Verbindung beendet"
    #print text
    common.log('',text)
    #xbmc.executebuiltin("Notification(XBMC-Fritzbox,"+text+","+duration+","+DEFAULT_IMG+")")
    common.show_notification(heading, text, duration, DEFAULT_IMG)

fncDict = {'CALL': handleOutgoingCall, 'RING': handleIncomingCall, 'CONNECT': handleConnected, 'DISCONNECT': handleDisconnected}


if useFritzAB: 
    tmp=fritzAddressbook.Fritzboxtelefonbuch(xbmctelefonbuch,fritzAddressURL)
    xbmctelefonbuch = tmp.getTelefonbuch()
    
common.log('',"ABFritzbox: "+ str(useFritzAB))


try:
    common.log(__addonname__,'started', xbmc.LOGNOTICE)    
    response = ''
    worker_thread = IncomingCallThread(ip)
    common.log(__addonname__,'IncomingCallThread', xbmc.LOGNOTICE)    
    worker_thread.setDaemon(True)
    common.log(__addonname__,'setDaemon', xbmc.LOGNOTICE)    
    worker_thread.start()
    common.log(__addonname__,'start', xbmc.LOGNOTICE)    
    
    while (not xbmc.abortRequested):
        try:
            sleep(0.5)
            common.log(__addonname__,'Loop', xbmc.LOGNOTICE)    
            
            IncomingCallThread.response_lock.acquire()
            response = IncomingCallThread.response
            common.log(__addonname__,'Response ' +  response, xbmc.LOGNOTICE)    
            IncomingCallThread.response = ''
            IncomingCallThread.response_lock.release()            
            if response != '':
                log= "[%s] %s" % (ip,response)
                common.log('', log)
                items = response.split(';')
                fncDict.get(items[1], errorMsg)(items)
                response = ''
        except IndexError:
            text = 'ERROR: Something is wrong with the message from the fritzbox. unexpected firmware maybe'
            common.log(__addonname__,text)

        except Exception, msg:
            common.log(__addonname__,msg)
    common.log(__addonname__,'XBMC sent an abort request')
    
except Exception, msg:
    common.log(__addonname__,msg)