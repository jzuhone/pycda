import requests
from requests import ConnectionError
from astropy.io import ascii
import astropy.units as u
from astropy.table import Table, vstack
import numpy as np


urlbase = "https://cda.harvard.edu/srservices/ocatDetails.do?format=text"

converters = {
    "APP_EXP": [ascii.convert_numpy(np.float64)],
    "CHARGE_CYCLE": [ascii.convert_numpy(np.uint64)],
    "COUNT_RATE": [ascii.convert_numpy(np.float64)],
    "EST_CNT_RATE": [ascii.convert_numpy(np.float64)],
    "EVENT_COUNT": [ascii.convert_numpy(np.uint64)],
    "EVFIL_LO": [ascii.convert_numpy(np.float64)],
    "EVFIL_RA": [ascii.convert_numpy(np.float64)],
    "EXP_TIME": [ascii.convert_numpy(np.float64)],
    "F_TIME": [ascii.convert_numpy(np.float64)],
    "FORDER_CNT_RATE": [ascii.convert_numpy(np.float64)],
    "OBS_CYCLE": [ascii.convert_numpy(np.uint64)],
    "PROP_CYCLE": [ascii.convert_numpy(np.uint64)],
    "SOE_ROLL": [ascii.convert_numpy(np.float64)],
    "STRT_ROW": [ascii.convert_numpy(np.uint64)],
    "ROW_CNT": [ascii.convert_numpy(np.uint64)],
    "VMAG": [ascii.convert_numpy(np.float64)],
    "X_SIM": [ascii.convert_numpy(np.float64)],
    "Y_AMP": [ascii.convert_numpy(np.float64)],
    "Y_FREQ": [ascii.convert_numpy(np.float64)],
    "Y_OFF": [ascii.convert_numpy(np.float64)],
    "Y_PHASE": [ascii.convert_numpy(np.float64)],
    "Z_OFF": [ascii.convert_numpy(np.float64)],
    "Z_SIM": [ascii.convert_numpy(np.float64)],
    "DROPPED_CHIP_CNT": [ascii.convert_numpy(np.uint64)],
}

units = {
    "APP_EXP": "ks",
    "COUNT_RATE": "s**-1",
    "EST_CNT_RATE": "s**-1",
    "EVFIL_LO": "keV",
    "EVFIL_RA": "keV",
    "EXP_TIME": "ks",
    "F_TIME": "s",
    "FORDER_CNT_RATE": "s**-1",
    "SOE_ROLL": "degree",
    "X_SIM": "mm",
    "Y_OFF": "arcmin",
    "Z_OFF": "arcmin",
    "Z_SIM": "mm",
}


def ensure_numpy_array(obj):
    """
    This function ensures that *obj* is a numpy array. Typically used to
    convert scalar, list or tuple argument passed to functions using Cython.
    """
    if isinstance(obj, np.ndarray):
        if obj.shape == ():
            return np.array([obj])
        # We cast to ndarray to catch ndarray subclasses
        return np.array(obj)
    elif isinstance(obj, (list, tuple)):
        return np.asarray(obj)
    else:
        return np.asarray([obj])


def fetch_ocat_data(params):
    resp = requests.get(urlbase, params=params)
    tab = ascii.read(resp.text, format='basic', converters=converters,
                     delimiter='\t', header_start=0, data_start=2)
    if len(tab) == 0:
        raise RuntimeError(f"No ObsIDs with these criteria were found: {params}")
    for name in tab.colnames:
        if name in units:
            tab[name].unit = units[name]
    return tab