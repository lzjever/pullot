# -*- coding: utf-8 -*-
""" 尚捷科技 """

from pullot import FrameBuffer
#from shangjie.foundation.substrate.utils.logger import logger

import socket
import select
import traceback

class SelectClient(object):

    
    def __init__(self,host='127.0.0.1', port=3490,frame_decoder = None):
        self.connected = False
        self.frame_decoder = frame_decoder

        self.outbound = FrameBuffer()
        self.inbound = FrameBuffer(self.frame_decoder)
        self.port = int(port)
        self.host = host

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            self.sock.connect((self.host, self.port))
            self.connected = True
        except socket.error as e:
            #logger.ods ('Could not connect to tcp server @%d' % self.port ,lv='dev',cat = 'foundation.tcp')
            raise RuntimeError('Could not connect to tcp server @%s' % str( (self.host, self.port) )) 

        
    def pop_inbound (self):
        self.do_select_comm()
        return self.inbound.pop_frame()
        
    def push_outbound (self,frame):
        self.outbound.push_frame(frame)
        self.do_select_comm()

        
    def shutdown (self):
        self.connected = False
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
                
    def do_select_comm(self):

        try:
            inputready, outputready,exceptrdy = select.select([self.sock], [ ],[ ],0.01)
            self.sock.send(self.outbound.get_buffer())
            self.outbound.clear_buffer()
            # only one socket descripter has been selected.
            for s in inputready:
                if s == self.sock:
                    buf = self.sock.recv(1024)
                    data = buf
                    if not buf:
                        logger.ods ('Socket is shutting down.' ,lv='dev',cat = 'foundation.tcp')
                        self.sock.close()
                        self.connected = False
                        break
                    else:
                        while len(buf) == 1024:
                            buf = self.sock.recv(1024)
                            data += buf
                        self.inbound.append_buffer(data)


        except BlockingIOError as err:
            #logger.ods (err ,lv='info',cat = 'foundation.tcp')
            return
                        
        except Exception as err:
            traceback.print_exc()
            self.sock.close()
            self.connected = False
            raise RuntimeError('[do_select_comm] failed.') 



if __name__ == '__main__':
    client = SelectClient(port=18755)
    while True:
        client.push_outbound('12345'.encode('utf-8'))
        client.do_select_comm()
        in_frame = client.pop_inbound()
        while in_frame is not None:
            print (bytes([in_frame]).decode('utf-8'))
            in_frame = client.pop_inbound()
        
        