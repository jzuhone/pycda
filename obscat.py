from __future__ import print_function
import requests
from requests import ConnectionError
import webbrowser
from astropy.io import ascii
from astropy.units import Quantity

def type_check(item, ret):
    if ret is None or ret == "None":
        return ret
    elif item.upper() == "EXP_TIME":
        return Quantity(float(ret), "ks")
    else:
        return ret

class ObsID(object):
    def __init__(self, row):
        self.row = row
        self.id = row["OBSID"]

    def __str__(self):
        return self.id

    def __repr__(self):
        return "ObsID %s" % self.id

    def __getitem__(self, item):
        ret = self.row[item.upper()]
        return type_check(item, ret)

    def __contains__(self, item):
        return item.upper() in self.obsid

    def get(self, item, default=None):
        ret = self.row.get(item.upper(), default)
        return type_check(item, ret)

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

    def open_obscat_data_page(self):
        """
        Get the obsid information from ChaSeR in a web browser.
        """
        url = 'https://icxc.harvard.edu/cgi-bin/mp/'
        url += "target_param.cgi?%s" % self.id
        webbrowser.open(url)

urlbase = "http://cda.harvard.edu/srservices/ocatDetails.do?format=text"

class ChandraObscat(object):
    def __init__(self):
        self.ocat = {}

    def keys(self):
        return self.ocat.keys()

    def items(self):
        return self.ocat.items()

    def values(self):
        return self.ocat.values()

    def __getitem__(self, obsid):
        obsid = str(obsid)
        if obsid not in self.ocat:
            self._fetch_ocat_data({"obsid": obsid})
        return self.ocat[obsid]

    def __contains__(self, obsid):
        return str(obsid) in self.ocat

    def __iter__(self):
        for obsid in self.ocat:
            yield obsid

    def __len__(self):
        return len(self.keys())

    def _fetch_ocat_data(self, params):
        u = requests.get(urlbase, params=params)
        tab = ascii.read(u.text)
        tab.remove_row(0)
        if len(tab) == 0:
            raise RuntimeError("No ObsIDs with these criteria were found: %s" % params)
        for row in tab:
            self.ocat[row["OBSID"]] = ObsID(row)

    def find_obs_with(self, *args, **kwargs):
        self._fetch_ocat_data(kwargs)

    def clear(self):
        print("Clearing this ChandraObscat.")
        self.ocat = {}

    def __repr__(self):
        return "ChandraObscat (%d ObsIDs)" % len(self)
