from __future__ import print_function
import requests
from requests import ConnectionError
import webbrowser
from astropy.io import ascii
import astropy.units as u
from astropy.table import Table, vstack
import numpy as np

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

def fix_table(tab):
    fix_column(tab, 'APP_EXP', 'float64', 'ks')
    fix_column(tab, 'CHARGE_CYCLE', 'uint64')
    fix_column(tab, 'COUNT_RATE', 'float64', 's**-1')
    fix_column(tab, 'DITHER', 'U1')
    fix_column(tab, 'EST_CNT_RATE', 'float64', 's**-1')
    fix_column(tab, 'EVENT_COUNT', 'uint64')
    fix_column(tab, 'EVFIL_LO', 'float64', 'keV')
    fix_column(tab, 'EVFIL_RA', 'float64', 'keV')
    fix_column(tab, 'EXP_TIME', 'float64', 'ks')
    fix_column(tab, 'F_TIME', 'float64', 's')
    fix_column(tab, 'FORDER_CNT_RATE', 'float64', 's**-1')
    fix_column(tab, 'GRID_NAME', 'U')
    fix_column(tab, 'NUDGE', 'U1')
    fix_column(tab, 'OBS_CYCLE', 'uint64')
    fix_column(tab, 'PR_NUM', 'U')
    fix_column(tab, 'PROP_CYCLE', 'uint64')
    fix_column(tab, 'SOE_ROLL', 'float64', 'degree')
    fix_column(tab, 'STRT_ROW', 'uint64')
    fix_column(tab, 'ROW_CNT', 'uint64')
    fix_column(tab, 'UNINT', 'U1')
    fix_column(tab, 'VMAG', 'float64')
    fix_column(tab, 'X_SIM', 'float64', 'mm')
    fix_column(tab, 'Y_AMP', 'float64')
    fix_column(tab, 'Y_FREQ', 'float64')
    fix_column(tab, 'Y_OFF', 'float64', 'arcmin')
    fix_column(tab, 'Y_PHASE', 'float64')
    fix_column(tab, 'Z_OFF', 'float64', 'arcmin')
    fix_column(tab, 'Z_SIM', 'float64', 'mm')
    fix_column(tab, 'DROPPED_CHIP_CNT', 'uint64')

def fix_column(tab, name, new_type, unit=None):
    new_arr = ensure_numpy_array(tab[name].data).astype(new_type)
    if unit is not None:
        new_arr = new_arr * u.Unit(unit)
    tab.replace_column(name, new_arr)
    if unit is not None:
        tab[name].unit = u.Unit(unit)

class ObscatEntry(object):
    def __init__(self, row):
        self.row = row
        self.id = row["OBSID"]

    def __str__(self):
        return self.id

    def __repr__(self):
        return "ObsID %s: %s" % (self.id, self['TARGET_NAME'])

    def __getitem__(self, item):
        return self.row[item.upper()]

    def __contains__(self, item):
        return item.upper() in self.row

    def get(self, item, default=None):
        return self.row.get(item.upper(), default)

    def __getattr__(self, item):
        return self[item.upper()]

    def keys(self):
        return self.row.colnames

    def open_chaser(self):
        """
        Get the obsid information from ChaSeR in a web browser.
        """
        url = "http://cda.cfa.harvard.edu/chaser/"
        url += "startViewer.do?menuItem=details&obsid=%s" % self.id
        webbrowser.open(url)

urlbase = "http://cda.harvard.edu/srservices/ocatDetails.do?format=text"

class ChandraObscat(object):
    def __init__(self):
        self.table = Table()
        self.obsid_map = {}

    def keys(self):
        return self.obsid_map.keys()

    def items(self):
        return [(k, self[k]) for k in self.keys()]

    def values(self):
        return [self[k] for k in self.keys()]

    def __getitem__(self, item):
        obsid = str(item)
        if obsid not in self.obsid_map:
            self._fetch_ocat_data({"obsid": obsid})
        return ObscatEntry(self.table[self.obsid_map[obsid]])

    def __contains__(self, obsid):
        return str(obsid) in self.obsid_map

    def __iter__(self):
        for obsid in self.obsid_map:
            yield obsid

    def __len__(self):
        return len(self.table)

    def _fetch_ocat_data(self, params):
        resp = requests.get(urlbase, params=params)
        tab = ascii.read(resp.text)
        tab.remove_row(0)
        fix_table(tab)
        if len(tab) == 0:
            raise RuntimeError("No ObsIDs with these criteria were found: %s" % params)
        self.obsid_map.update(dict((obsid, i+len(self)) for i, obsid in enumerate(tab["OBSID"])))
        if len(self) == 0:
            self.table = tab
        else:
            self.table = vstack([self.table, tab])

    def find_obs_with(self, *args, **kwargs):
        self._fetch_ocat_data(kwargs)

    def clear(self):
        print("Clearing this ChandraObscat.")
        self.table = Table()

    def as_table(self):
        return self.table

    def __repr__(self):
        return "ChandraObscat (%d ObsIDs)" % len(self)
