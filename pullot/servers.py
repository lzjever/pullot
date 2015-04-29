# -*- coding: utf-8 -*-
"""   """

from pullot import FrameBuffer
#from shangjie.foundation.substrate.utils.logger import logger

import socket
import select
import traceback
import queue
import threading



class SelectServer(object):

             
    def __init__(self,host='127.0.0.1', port=18755,frame_decoder = None):

        self.port = int(port)
        self.host = host
        self.server_address = (host,port)
        self.frame_decoder = frame_decoder
 
        self.s_lock = threading.RLock()


        self.to_close_socks = []

        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setblocking(False)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR  , 1)
            self.server.bind(self.server_address)
            self.server.listen(0)
            
            # Collection of peers , every connection will be added to the inbound dic.
            self.inbound = {}
            self.outbound = {}

        except socket.error as e:
            traceback.print_exc()
            
            logger.ods ('Could not listen on port @%d' % self.port ,lv='dev',cat = 'foundation.tcp')
            raise RuntimeError('Could not listen on port @%d' % self.port) 

    def _get_inputs (self):
        inputs = [self.server]
        for peer in self.inbound:
            inputs.append(peer)
        return inputs

    def _get_outputs (self):
        outputs = []
        for peer in self.outbound:
            outputs.append(peer)
        return outputs
        
                    
        
    
    def pop_inbound (self):
        try:
            self.s_lock.acquire()
            self.do_select_comm()
            for peer in self.inbound:
                df = self.inbound[peer].pop_frame()
                if df is not None:
                    return {'peer': peer, 'frame':df}

            return None
        finally:
            self.s_lock.release()
        #raise RuntimeError('[pop_inbound] has to be implemented at derived class.')
        
    def push_outbound (self,peer,frame):
        try:
            self.s_lock.acquire()
            # connection has been lost , no need to send. return a false
            if self.inbound.get(peer) == None:
                return False

            if self.outbound.get(peer) == None:
                self.outbound[peer] = TSFrameBuffer()

            self.outbound[peer].push_frame(frame)
            self.do_select_comm()
        finally:
            self.s_lock.release()
        
    def shutdown (self):
        try:
            self.s_lock.acquire()

            self.server.shutdown(socket.SHUT_RDWR)
            self.server.close()
        finally:
            self.s_lock.release()

    def _clear_peer (self,peer_sock):
        if peer_sock in self.inbound:
            del(self.inbound[ peer_sock ])

        if peer_sock in self.outbound:
            del(self.outbound[ peer_sock ])

        if peer_sock in self.to_close_socks:
            self.to_close_socks.remove(peer_sock)
        
        try:

            peer_sock.shutdown(socket.SHUT_RDWR)
            peer_sock.close()
        except Exception as e:
            logger.ods ('Exception @ [_clear_peer]. Ignored.'  ,lv='dev',cat = 'foundation.tcp'  )
                
    def close_peer (self,peer_sock):
        try:
            self.s_lock.acquire()
            if (not( peer_sock in self.to_close_socks)) and (peer_sock in self.inbound):
                self.to_close_socks.append(peer_sock)
        finally:
            self.s_lock.release()

    def _chk_to_close (self,peer_sock):
        return peer_sock in self.to_close_socks
        
            
    
    def _proc_input (self,rlist):
        for sock in rlist :
            # if receiving a new connection
            if sock is self.server:
                peer, client_address = sock.accept()
                peer.setblocking(0)
                

                self.inbound[ peer ] = TSFrameBuffer(self.frame_decoder)
                #self.outbound[ client ] = TSFrameBuffer()
            else:
                try:
                    buf = sock.recv(1024)
                    data = buf
                    # got a disconnecting msg.
                    if not buf:
                        self._clear_peer(sock)
                        break
                    else:
                        while len(buf) == 1024:
                            buf = sock.recv(1024)
                            data += buf
                        self.inbound[ sock ].append_buffer(data)
                except BlockingIOError as err:
                    logger.ods ('BlockingIOError @ [_proc_input]'  ,lv='dev',cat = 'foundation.tcp'  )
                    return
                except Exception as err:
                    logger.ods (traceback.format_exc()  ,lv='error',cat = 'foundation.tcp'  )
                    self._clear_peer(sock)

                

    def _proc_output (self,wlist):
        for sock in wlist:
            try:

                to_send = self.outbound[ sock ].get_buffer()
                self.outbound[ sock ].clear_buffer()
                if len(to_send) == 0:
                    #print ( str( sock.getpeername()) +  ' outbound buffer empty')
                    # stop reading temporarily
                    if sock in self.outbound :
                        del (self.outbound[sock])

                    if self._chk_to_close(sock):
                        self._clear_peer(sock)
                            
                else:
                    logger.ods ("sending " + str(to_send) + " to " + str(sock.getpeername() )  ,lv='dev',cat = 'foundation.tcp'  )
                    sock.send(to_send)
            except BlockingIOError as err:
                logger.ods ('BlockingIOError @ [_proc_output]'  ,lv='dev',cat = 'foundation.tcp'  )
            except Exception as err:
                logger.ods (traceback.format_exc()  ,lv='error',cat = 'foundation.tcp'  )
                self._clear_peer(sock)

    def _proc_exception(self,xlist):
        for sock in xlist:        
            logger.ods ("exception condition on " + str( sock.getpeername() ) ,lv='dev',cat = 'foundation.tcp'  )
            self._clear_peer(sock)
                            
    def do_select_comm(self):
        try:
            self.s_lock.acquire()

            try:        
                inputready, outputready,exceptrdy = select.select(self._get_inputs(), self._get_outputs(), self._get_inputs(),0.1)

                self._proc_input(inputready)
                self._proc_output(outputready)
                self._proc_exception(exceptrdy)

                                        
            except Exception as err:
                logger.ods (traceback.format_exc()  ,lv='error',cat = 'foundation.tcp'  )
                raise RuntimeError('[do_select_comm] failed.') 
        finally:
            self.s_lock.release()

        







class _test_frame(object):
    def marshal (self):
        return bytes('show me the money'.encode('utf-8'))

def _test_decoder (data_in):
    if len(data_in) < 5:
        return 0, None
    print (str(data_in[0:5]))
    return 5 ,  str(data_in[0:5])
    

if __name__ == '__main__':
    server = SelectServer(frame_decoder = _test_decoder)
    while True:
        server.do_select_comm()
        logger.ods ("123",lv='dev',cat = 'foundation.tcp'  )
        in_frame = server.pop_inbound()
        if in_frame is not None:
            print (in_frame)
            server.push_outbound(in_frame['peer'],_test_frame())

        
        
        
