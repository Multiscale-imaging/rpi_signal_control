import numpy as np
import time
import matplotlib.pyplot as plt
import datetime
import pickle

class OscilloscopeEvent:
    def __init__(self, time, ch1, ch2, ch3):
        self.time = time
        self.ch1 = ch1
        self.ch2 = ch2
        self.ch3 = ch3
    def __str__(self):
        return f'{time}, channel 1 (voltage) {ch1:.2f}, channel 2(current) {ch2:.2f}, channel 3(voltage) {ch3:.2f}'
    
    def __lt__(self, other):
        if hasattr(other,'time'):
            return self.time < other.time
        return self.time < other
    def __gt__(self, other):
        if hasattr(other,'time'):
            return self.time > other.time
        return self.time > other

times = []
events = []
probe_events = []

try: # try reading actual log
    with open('oscilloscope.log','r') as f:
        past_time = 0
        for i, line in enumerate(f):
            if i<800:
                continue
            if 'Current Time' in line:
                t = line.split(' ')[-1].split(':')
                past_time = float(t[0])*3600+float(t[1])*60+float(t[2])
            if 'AvgC1?' in line:
                val = line.split()
                probe_events.append(past_time)
            if 'AvgC1C2' in line:
                val = line.split()
                val.append('0')
                events.append([past_time,float(val[1][:-1]), float(val[2].strip(',')), float(val[3].strip())])
    with open('oscilloscope.log.pickle','wb') as f:
        pickle.dump((probe_events, events), f)
except: # try reading pickled log
    with open('oscilloscope.log.pickle','rb') as f:
        probe_events, events = pickle.load(f)
        
events = np.array(events)
date_string = f'2022-05-24 00:00:00'
date_0 = datetime.datetime.fromisoformat(date_string)
tadd = 0

osc_events = []
for i, event in enumerate(events[:-1]):
    inc = False
    if events[i+1,0]<events[i,0]:
        inc = True
    osc_events.append(OscilloscopeEvent(date_0 + datetime.timedelta(seconds = events[i,0]+tadd), events[i,1], events[i,2], events[i,3]))
    if inc:
        tadd += 24*3600        
osc_events.append(OscilloscopeEvent(date_0 + datetime.timedelta(seconds = events[-1,0]+tadd), events[-1,1], events[-1,2], events[-1,3]))

query_events = []
tadd = 0
for i, event in enumerate(probe_events[:-1]):
    inc = False
    if probe_events[i+1]<probe_events[i]:
        inc = True
    query_events.append(date_0 + datetime.timedelta(seconds = event+tadd))
    if inc:
        tadd += 24*3600        
query_events.append(date_0 + datetime.timedelta(seconds = probe_events[-1]+tadd))

class MultimeterEvent:
    def __init__(self, time, current):
        self.time = time
        self.current = current
    def __str__(self):
        return f'{time}, current {current:.2f}'
    
    def __lt__(self, other):
        if hasattr(other,'time'):
            return self.time < other.time
        return self.time < other
    def __gt__(self, other):
        if hasattr(other,'time'):
            return self.time > other.time
        return self.time > other
times = []
mm_events = []
with open('multimeter.log','r') as f:
    past_time = 0
    for i, line in enumerate(f):
        if i<1000:
            continue
        if 'Current Time' in line:
            t = line.split(' ')[-1].split(':')
            past_time = float(t[0])*3600+float(t[1])*60+float(t[2])
        if 'READ?' in line:
            val = line.split()
            mm_events.append([past_time, float(val[-1].strip())])
mm_events = np.array(mm_events)   
multimeter_events = []
tadd = 0
for i, event in enumerate(mm_events[:-1]):
    inc = False
    if mm_events[i+1][0]<mm_events[i][0]:
        inc = True
    multimeter_events.append(MultimeterEvent(date_0 + datetime.timedelta(seconds = event[0]+tadd), event[1]))
    if inc:
        tadd += 24*3600        
multimeter_events.append(MultimeterEvent(date_0 + datetime.timedelta(seconds = mm_events[-1,0]+tadd),mm_events[-1,1]))

def plot_near(datetime_as_string, window_in_s = 300):
    relevant_time = datetime.datetime.fromisoformat(datetime_as_string)
    mask = np.array([abs(event.time-relevant_time)<datetime.timedelta(seconds = window_in_s) for event in osc_events], dtype = bool)
    dates = []
    V = []
    I = []
    V2 = []
    for i, event in enumerate(osc_events):
        if mask[i]:
            dates.append(event.time)
            V.append(event.ch1)
            I.append(event.ch2)
            V2.append(event.ch3)
            

    fig, ax = plt.subplots(1,1,figsize = (20,3), dpi = 300)
    ax.plot(dates, V, color = [0,0.3,1], lw = 1, label = 'Ch1')   
        
    ax.plot(dates, np.array(V2), color = [0,0.1,0.5], lw = 1, label = 'Ch3')
        
    ax.set_ylabel('Ch1 [V], Ch3 [V]', color = [0,0.3,1])  
    ax.set_xlabel('Date, Time')
    ax.legend(loc = 3)
    
    ylim = (0,np.max(V)*1.1)
    ax.plot([relevant_time,relevant_time],ylim, '--', color = [0,0,0])
    ax.set_ylim(ylim)
    ax2 =ax.twinx()
    ax2.plot(dates, I, color = [1,0.3,0], lw = 0.5, label = 'Ch2 [V]')  
    ax2.set_ylabel('Ch2 [V], multimiter[A]', color = [1,0.3,0])
    
    
    '''
    query_mask = np.array([abs(event-relevant_time)<datetime.timedelta(seconds = window_in_s) for event in query_events], dtype = bool)
    print(sum(query_mask))
    query_dates = []
    for i, event in enumerate(query_events):
        if query_mask[i]:
            query_dates.append(event)
    ax.plot(query_dates,np.ones(len(query_dates))*0.5*ylim[1], 'x', color = [0,0,0])
    '''
    
    mm_mask = np.array([abs(event.time-relevant_time)<datetime.timedelta(seconds = window_in_s) for event in multimeter_events], dtype = bool)
    mm_dates = []
    mm_I = []
    for i, event in enumerate(multimeter_events):
        if mm_mask[i]:
            mm_dates.append(event.time)
            mm_I.append(event.current)
    ax2.plot(mm_dates, mm_I, 'x-', color = [1,0.3,0],lw = 1, label = 'multimeter')   
    ax2.legend(loc = 4)
    
def get_near(datetime_as_string, window_in_s = 300):
    relevant_time = datetime.datetime.fromisoformat(datetime_as_string)
    mask = np.array([abs(event.time-relevant_time)<datetime.timedelta(seconds = window_in_s) for event in osc_events], dtype = bool)
    dates = []
    V = []
    I = []
    V2 = []
    for i, event in enumerate(osc_events):
        if mask[i]:
            dates.append(event.time)
            V.append(event.ch1)
            I.append(event.ch2)
            V2.append(event.ch3)
    mm_mask = np.array([abs(event.time-relevant_time)<datetime.timedelta(seconds = window_in_s) for event in multimeter_events], dtype = bool)
    mm_dates = []
    mm_I = []
    for i, event in enumerate(multimeter_events):
        if mm_mask[i]:
            mm_dates.append(event.time)
            mm_I.append(event.current)
            
    return dates, np.array(V), np.array(I), np.array(V2), mm_dates, np.array(mm_I)