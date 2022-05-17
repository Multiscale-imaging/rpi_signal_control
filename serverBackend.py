import threading
from datetime import datetime
import time
BUFFER_SIZE = 1024

inst = 'not set'
keys = {}
override_dict = {}
logfile = ''

def setup(inst_, keys_, logfile_):
    global inst, keys, logfile
    inst = inst_
    keys = keys_
    logfile = logfile_
    
def fprint(string):
    try:
        with open(logfile,'a') as log:
            log.write(string+'\n')
    except:
        with open(logfile,'w') as log:
            log.write(string+'\n')
    print(string)
    
def query(query):
    
    '''
    send query 
        or
    if key in override_dict.keys(), execute out=override_dict[key]()
    '''
    if query in override_dict.keys():
        out = override_dict[query]()
    else:
        # send query
        inst.write(query)

        # collect return
        out =''
        while True:
            line = inst.read_bytes(1)
            if line == b'1`':
                if len(out)>0:
                    break
                continue
            out += line.decode('utf-8')
            if b'\n' in line: # newline marks end of return
                break
    fprint(query+' '+out)
    return out.strip('\n')

def set_single_param(key, val):
    '''
    set single parameter on the signal generator
    '''
    if key in keys:
        #time.sleep(0.1)
        inst.write(key+' '+str(val))
        fprint(f'   set  {key}: {val}')
    else:
        fprint(f"ERROR: don't know what to do with {key}: {val}, skipping")
    # i.e. parameters['chopper:phase'] = 10 --> chopper.phase = 10
    
def set_params(parameters):
    '''
    set multiple parameters on the signal generator
    '''
    for key in parameters.keys():
        set_single_param(key, parameters[key])
        

def get_params():
    '''
    get all params from signal generator
    returns a dictionary of key:value for each key in keys
    '''
    parameters = {}
    for key in keys:
        fprint(f'    query {key}?')
        parameters[key] = query(key+'?')
        fprint(parameters[key])
    return parameters


def data_to_dict(inp):
    '''
    converts a string to a dictionary, splitting the data at ':' for each key/val pair
    the string is assumed to be generated by casting a dictionary to a string, i.e. str(dict)
    '''
    spl = inp.split("', '")
    spl[0] = spl[0][2:]
    spl[-1] = spl[-1][:-2]
    parameters = {}
    for i, sp in enumerate(spl):
        key_val = sp.split("': '")
        parameters[key_val[0]] = key_val[1]
    return parameters

def parse_parameters(parameters):
    for key in parameters.keys():
        set_single_param(key, parameters[key])


class server(threading.Thread):
    def __init__(self, socket, address):
        threading.Thread.__init__(self)
        self.sock = socket
        self.addr = address
        self.start()
        
    def run(self):
        data = self.sock.recv(BUFFER_SIZE).decode() # blocking until it recieves data
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        fprint("Current Time =", current_time)
        if data == '?':
            parameters = get_params()
            self.sock.send(str(parameters).encode())
            fprint('    sent parameters')
        elif '=' in data:
            key = data.split('=')[0].strip()
            val = data.split('=')[1].strip()
            set_single_param(key, val)
            self.reply_single(key)
        elif data[0] == '?' or data[-1]=='?':
            self.reply_single(data.strip('?'))
        else:
            parameters = data_to_dict(data)
            parse_parameters(parameters)
            #process(parameters)
            #conn.close()
            
    def reply_single(self, key):
        '''
        ask signal generator about key, send answer to the socket
        '''
        val = query(key+'?')
        self.sock.send(str(key+' = '+ str(val)).encode())
    
import subprocess
def get_ip(verbose = False):
    ifconfig = str(subprocess.check_output(['ifconfig'])).split('\\n')
    ip = ifconfig[1].split()[1] 
    if verbose:
        for line in ifconfig:
            print(line)
        print('ip = ',ip)
    return ip