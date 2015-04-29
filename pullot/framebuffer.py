# -*- coding: utf-8 -*-
# Copyright (c) @Lzjever.
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



# thread safe version!        
class TSFrameBuffer(FrameBuffer):
    def __init__(self,decoder = None):
        super(TSFrameBuffer,self).__init__(decoder)
        self.internal_lock = threading.RLock()

    def set_decoder (self,decoder = None):
        try:
            self.internal_lock.acquire()
            return super(TSFrameBuffer,self).set_decoder(decoder)
        finally:
            self.internal_lock.release()


    def pop_frame (self):
        try:
            self.internal_lock.acquire()
            return super(TSFrameBuffer,self).pop_frame()
        finally:
            self.internal_lock.release()



    def push_frame (self,frame):
        try:
            self.internal_lock.acquire()
            return super(TSFrameBuffer,self).push_frame(frame)
        finally:
            self.internal_lock.release()

                        

    def append_buffer (self,buf):
        try:
            self.internal_lock.acquire()
            return super(TSFrameBuffer,self).append_buffer(buf)
        finally:
            self.internal_lock.release()

    def pop_buffer (self):
        try:
            self.internal_lock.acquire()
            return super(TSFrameBuffer,self).pop_buffer()
        finally:
            self.internal_lock.release()

    def get_buffer (self):
        try:
            self.internal_lock.acquire()
            return copy.deepcopy( super(TSFrameBuffer,self).get_buffer() )
        finally:
            self.internal_lock.release()

    def clear_buffer (self):
        try:
            self.internal_lock.acquire()
            return super(TSFrameBuffer,self).clear_buffer()
        finally:
            self.internal_lock.release()
        
    def get_buffer_length(self):
        try:
            self.internal_lock.acquire()
            return super(TSFrameBuffer,self).get_buffer_length()
        finally:
            self.internal_lock.release()
    


if __name__ == '__main__':
    fb = FrameBuffer()
