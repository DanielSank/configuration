#!/usr/bin/env python

# system imports
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

import matplotlib as mpl
mpl.rcParams['lines.linestyle']=None
mpl.rcParams['axes.grid'] = True
mpl.rcParams['lines.marker'] = '.'
mpl.rcParams['legend.numpoints'] = 1
plt.ion()

# Username prefix for datavault and registry path
# i.e. what data configures your experiment
USERNAME = "Daniel"

# Set up labrad, pyle, and servers paths
SOURCENAME = "Daniel"

if os.name == "posix":
    base_path = os.environ["HOME"] + "/src"
elif os.name == "nt":
    base_path = "~/src"

PYLABRAD_PATH = 'pylabrad'
PYLE_PATH = 'pyle'

sys.path.insert(1, os.path.join(base_path))
sys.path.insert(1, os.path.join(base_path, PYLABRAD_PATH))
sys.path.insert(1, os.path.join(base_path, PYLE_PATH))


import labrad
import labrad.units as U
from labrad.units import Unit, Value
rad, ns, us, MHz, GHz, mV, V, Ohm, dBm = (Unit(s) for s in \
    ['rad','ns','us','MHz','GHz','mV','V','Ohm','dBm'])
from labrad.units import ValueArray


if os.name == "nt":
    try:
        import thread, ctypes, imp
        import win32api
        basepath = imp.find_module('numpy')[1]
        lib1 = ctypes.CDLL(os.path.join(basepath, 'core', 'libmmd.dll'))
        lib2 = ctypes.CDLL(os.path.join(basepath, 'core', 'libifcoremd.dll'))
        def handler(sig, hook=thread.interrupt_main):
            hook()
            return 1
        win32api.SetConsoleCtrlHandler(handler, 1)
    # If something goes wrong, it's probably a missing dll, in which case
    # we can procede.
    except Exception as e:
        print e


# pyle
import pyle.util.registry as registry
import pyle.envelopes as env
import pyle.util.sweeptools as st
import pyle.workflow as workflow
import pyle.datavault as datavault
import pyle.dataking.readout as pdr


def switchSession(session=None, user=None):
    """Switch the current session, using the global connection object"""
    global s
    if user is None:
        user = s._dir[1]
    s = workflow.switchSession(cxn, user, session)


def pipe_filling_factor(board_group=('DR Direct Ethernet', 1)):
    """Download performance data from the GHz DACs and calculate
    the fraction of time that the GHz DAC pipeline is full.
    """
    with labrad.connect() as cxn:
        perf = dict(cxn.ghz_dacs.performance_data())
    times = perf[board_group][3].asarray
    error_rate = sum(times == 0) / float(len(times))
    return 1 - error_rate


# connect to labrad and setup a wrapper for the current sample
cxn = labrad.connect()
switchSession(user='Daniel')

