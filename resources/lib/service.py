import threading 
import resources.lib.common as common
import xbmc, xbmcaddon
import socket
from types import *

class IncomingCallThread(threading.Thread): 

    response = ''
    response_lock = threading.Lock() 

    def __init__(self, ip): 
        threading.Thread.__init__(self) 
        self.ip = ip

    def run(self): 

        common.log('IncomingCallThread','started', xbmc.LOGNOTICE)    
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        
        try:
            s.connect((self.ip, 1012))
            common.log('IncomingCallThread','Connected to fritzbox callmonitor at %s'%self.ip)
            s.setblocking(1)
            while True:
                try:
                    complete = False
                    self.response = s.recv(1024) 
                    # check for completness of response data
                    while not complete:
                        items = response.split(';')
                        
                        if items[1] == 'CALL':
                            if length(items) < 8:
                                self.response += s.recv(1024) 
                            else:
                                complete = True
                                
                        elif items[1] == 'RING':
                            if length(items) < 7:
                                self.response += s.recv(1024) 
                            else:
                                complete = True
                                
                        elif items[1] == 'CONNECT':
                            if length(items) < 6:
                                self.response += s.recv(1024) 
                            else:
                                complete = True
                                
                        elif items[1] == 'DISCONNECT':
                            if length(items) < 5:
                                self.response += s.recv(1024) 
                            else:
                                complete = True
                        else:   
                            complete = True
                            
                    # critical section
                    IncomingCallThread.response_lock.acquire()
                    IncomingCallThread.response = self.reponse
                    IncomingCallThread.response_lock.release()
                except socket.error, exception:
                    common.log('IncomingCallThread','ERROR: Could not connect to fritz.box on port 1012', xbmc.LOGERROR)
                except Exception, msg:
                    pass
        except Exception, msg:
            common.log('IncomingCallThread','Connection Error', xbmc.LOGERROR)
            common.log('IncomingCallThread',msg, xbmc.LOGERROR)

        s.close()    
