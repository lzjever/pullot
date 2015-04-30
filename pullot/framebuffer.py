# -*- coding: utf-8 -*-

# The MIT License (MIT)
# Copyright (c) 2015 Percy Li
# See LICENSE for details.



import struct
import threading
import copy


class FrameBuffer(object):
    def __init__(self,decoder = None):
        self.data_buffer = bytes([])
        self.decoder = decoder
    
    def set_decoder (self,decoder = None):
        self.decoder = decoder
        
    def pop_frame (self):
        if self.decoder is not None:
            fe,df = self.decoder(self.data_buffer)
            self.data_buffer = self.data_buffer[fe:]
            if df:
                #logger.ods ('Decoded frame : \n ' + str(df) ,lv='dev',cat = 'foundation.tcp')
                pass
            
            return df  # None if fail
        else:
            # if no decoder was specified , return a single byte in the head of the buffer.
            return self.pop_buffer()



    def push_frame (self,frame):
        if hasattr(frame,'marshal'):
            self.data_buffer += frame.marshal()
            return 
        if isinstance(frame,bytes):
            self.data_buffer += frame
            return 

                        

    def append_buffer (self,buf):
        self.data_buffer += buf

    def pop_buffer (self):
        if self.get_buffer_length() == 0:
            return None
        
        _head = self.data_buffer[0]
        self.data_buffer = self.data_buffer[1:]
        return _head

    def get_buffer (self):
        return self.data_buffer

    def clear_buffer (self):
        self.data_buffer = bytes([])
        
    def get_buffer_length(self):
        return len(self.data_buffer)



# thread safe version
class TSFrameBuffer(FrameBuffer):
    def __init__(self,decoder = None):
        FrameBuffer.__init__(self,decoder)
        self.internal_lock = threading.RLock()

    def set_decoder (self,decoder = None):
        with self.internal_lock:
            return FrameBuffer.set_decoder(self,decoder)

    def pop_frame (self):
        with self.internal_lock:
            return FrameBuffer.pop_frame(self)




    def push_frame (self,frame):
        with self.internal_lock:
            return FrameBuffer.push_frame(self,frame)

                        

    def append_buffer (self,buf):
        with self.internal_lock:
            return FrameBuffer.append_buffer(self,buf)

    def pop_buffer (self):
        with self.internal_lock:
            return FrameBuffer.pop_buffer(self)

    def get_buffer (self):
        with self.internal_lock:
            return copy.deepcopy( FrameBuffer.get_buffer(self) )

    def clear_buffer (self):
        with self.internal_lock:
            return FrameBuffer.clear_buffer(self)
        
    def get_buffer_length(self):
        with self.internal_lock:
            return FrameBuffer.get_buffer_length(self)
    


if __name__ == '__main__':
    fb = FrameBuffer()
