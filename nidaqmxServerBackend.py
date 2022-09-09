import threading
from datetime import datetime
import time
import os
import queue
BUFFER_SIZE = 1024

inst = 'not set'
keys = {}
override_dict = {}
logfile = ''

def setup( logfile_):
    global logfile
    logfile = logfile_
    
def fprint(string):
    try:
        with open(logfile,'a') as log:
            log.write(string+'\n')
    except:
        with open(logfile,'w') as log:
            log.write(string+'\n')
    print(string)

def get_last_lines(file, n):
    with open(file, 'rb') as f:
        if os.path.getsize(file) > 1000:
            f.seek(-1000, 2)
        data = f.readlines()
        lines = []
        for i in range(n,0,-1):
            lines.append(data[-i].decode("utf-8"))
        lines = ' / '.join(lines).replace('\r\n', '').strip()
    return lines

class server(threading.Thread):
    def __init__(self, socket, address):
        threading.Thread.__init__(self)
        self.sock = socket
        self.addr = address
        self.start()
        
    def run(self):
        que = queue.Queue()
        vs = VoltageSetter(que)
        while True:
            data = self.sock.recv(BUFFER_SIZE).decode() # blocking until it recieves data
            if data == '':
                continue
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            fprint("Current Time = "+str(current_time))
            if data == 'VOLT?':
                reply = get_last_lines('nilog.txt', 2)
                self.sock.send(reply.encode())
                fprint(data + ' ' +reply)
            if data == 'CUR?':
                reply = get_last_lines('multimeter_log.txt', 2)
                self.sock.send(reply.encode())
                fprint(data + ' ' +reply)
            elif '=' in data:
                key = data.split('=')[0].strip()
                val = data.split('=')[1].strip()
                if key == 'VOLT':
                    que.put(val) # send it to process
                    reply = f'setting VOLT {float(val)}'
                    self.sock.send(reply.encode())
                    fprint(data + ' ' +reply)
            elif data == 'end':
                que.put('end')
                break
                    

import socket

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

import time
import nidaqmx
import threading
import nidaqmx.stream_writers
import numpy as np

class VoltageSetter(threading.Thread):
    def __init__(self, que):
        threading.Thread.__init__(self)
        self.que = que
        self.start()
        
    def run(self):
        while True:
            data = self.que.get()
            if data == 'end':
                break
            else:
                set_voltage(float(data))
            
def set_voltage(new_v, write_rate = 100, duration = 1):
    global old_v
    ramp = np.linspace(old_v, new_v, int(write_rate*duration))
    with nidaqmx.Task() as task:
        channel = task.ao_channels.add_ao_voltage_chan("Dev1/ao0")
        task.timing.cfg_samp_clk_timing(rate=write_rate,
                                            #source='/cDAQ1/ao/SampleClock',
                                            #active_edge=nidaqmx.constants.Edge.RISING,
                                            #sample_mode=nidaqmx.constants.AcquisitionType.FINITE,
                                        samps_per_chan= len(ramp)
                                       )
        writer = nidaqmx.stream_writers.AnalogMultiChannelWriter(task.out_stream)


        task.write(ramp, auto_start=False)
        task.start()
        with open('nilog_ao0.txt','a') as f:
            f.write(str(datetime.now())+'\n'+ f'rate {write_rate}, data: ' + ''.join([f'{s:.5f} ' for s in ramp]) +'\n')
        task.wait_until_done()
    old_v = new_v # reset        