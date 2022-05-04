# rpi_signal_control
signal control of instruments we bring to beamtime.
The signal generator (HMF2525) and oscilloscope (DSOX2014A) are connected via USB to a Raspberry pi. 
The RPI is placed in the huch and conneted to the network. 

The signal generator is set up to listen on port 5006 with the following commands available:
```
HMF2525_keys = [
    'FUNC',
    'OUTPut',
    'FREQuency',
    'PERiod',
    'VOLTage',
    'VOLTage:UNIT',
    'VOLTage:HIGH',
    'VOLTage:LOW',
    'VOLTage:OFFSet',
    'FUNCtion:PULSe:WIDTh:HIGH',
    'FUNCtion:PULSe:WIDTh:LOW',
    'FUNCtion:PULSe:DCYCle',
    'FUNCtion:PULSe:ETIMe',
    'TRIGger:SOURce',# {IMMediate | EXTernal}
    'BURSt:MODE',# TRIGgered | GATed
    'BURSt:NCYCles',
    'BURSt:INTernal:PERiod',
    'BURSt:PHASe', #0 to 360
    'BURSt:STATe',
    ]
```

The oscilloscope listens on port 5007, with the following available keys:
```
osc_keys = [
    'CHANnel1:DISPlay',
    'CHANnel2:DISPlay',
    'CHANnel3:DISPlay',
    'CHANnel4:DISPlay',
    'DIGitize',
    'WAVeform:SOURce', # CHANnel1
    'WAVeform:FORMat',# BYTE, ASCii
    'WAVeform:POINts', # 500
    'WAVeform:DATA', #?
    'RUN', #?
    'STOP', #?
    ] 
```
