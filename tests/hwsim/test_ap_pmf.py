#!/usr/bin/python
#
# Protected management frames tests
# Copyright (c) 2013, Jouni Malinen <j@w1.fi>
#
# This software may be distributed under the terms of the BSD license.
# See README for more details.

import time
import subprocess
import logging
logger = logging.getLogger(__name__)

import hwsim_utils
import hostapd
from wlantest import Wlantest

ap_ifname = 'wlan2'
bssid = "02:00:00:00:02:00"

def test_ap_pmf_required(dev):
    """WPA2-PSK AP with PMF required"""
    ssid = "test-pmf-required"
    wt = Wlantest()
    wt.flush()
    wt.add_passphrase("12345678")
    params = hostapd.wpa2_params(ssid=ssid, passphrase="12345678")
    params["wpa_key_mgmt"] = "WPA-PSK-SHA256";
    params["ieee80211w"] = "2";
    hostapd.add_ap(ap_ifname, params)
    dev[0].connect(ssid, psk="12345678", ieee80211w="1", key_mgmt="WPA-PSK WPA-PSK-SHA256", proto="WPA2")
    hwsim_utils.test_connectivity(dev[0].ifname, ap_ifname)
    dev[1].connect(ssid, psk="12345678", ieee80211w="2", key_mgmt="WPA-PSK WPA-PSK-SHA256", proto="WPA2")
    hwsim_utils.test_connectivity(dev[1].ifname, ap_ifname)
    hapd = hostapd.Hostapd(ap_ifname)
    hapd.request("SA_QUERY " + dev[0].p2p_interface_addr())
    hapd.request("SA_QUERY " + dev[1].p2p_interface_addr())
    wt.require_ap_pmf_mandatory(bssid)
    wt.require_sta_pmf(bssid, dev[0].p2p_interface_addr())
    wt.require_sta_pmf_mandatory(bssid, dev[1].p2p_interface_addr())
    time.sleep(0.1)
    if wt.get_sta_counter("valid_saqueryresp_tx", bssid,
                          dev[0].p2p_interface_addr()) < 1:
        raise Exception("STA did not reply to SA Query")
    if wt.get_sta_counter("valid_saqueryresp_tx", bssid,
                          dev[1].p2p_interface_addr()) < 1:
        raise Exception("STA did not reply to SA Query")

def test_ap_pmf_optional(dev):
    """WPA2-PSK AP with PMF optional"""
    ssid = "test-pmf-optional"
    wt = Wlantest()
    wt.flush()
    wt.add_passphrase("12345678")
    params = hostapd.wpa2_params(ssid=ssid, passphrase="12345678")
    params["wpa_key_mgmt"] = "WPA-PSK";
    params["ieee80211w"] = "1";
    hostapd.add_ap(ap_ifname, params)
    dev[0].connect(ssid, psk="12345678", ieee80211w="1", key_mgmt="WPA-PSK WPA-PSK-SHA256", proto="WPA2")
    hwsim_utils.test_connectivity(dev[0].ifname, ap_ifname)
    dev[1].connect(ssid, psk="12345678", ieee80211w="2", key_mgmt="WPA-PSK WPA-PSK-SHA256", proto="WPA2")
    hwsim_utils.test_connectivity(dev[1].ifname, ap_ifname)
    wt.require_ap_pmf_optional(bssid)
    wt.require_sta_pmf(bssid, dev[0].p2p_interface_addr())
    wt.require_sta_pmf_mandatory(bssid, dev[1].p2p_interface_addr())

def test_ap_pmf_optional_2akm(dev):
    """WPA2-PSK AP with PMF optional (2 AKMs)"""
    ssid = "test-pmf-optional-2akm"
    wt = Wlantest()
    wt.flush()
    wt.add_passphrase("12345678")
    params = hostapd.wpa2_params(ssid=ssid, passphrase="12345678")
    params["wpa_key_mgmt"] = "WPA-PSK WPA-PSK-SHA256";
    params["ieee80211w"] = "1";
    hostapd.add_ap(ap_ifname, params)
    dev[0].connect(ssid, psk="12345678", ieee80211w="1", key_mgmt="WPA-PSK WPA-PSK-SHA256", proto="WPA2")
    hwsim_utils.test_connectivity(dev[0].ifname, ap_ifname)
    dev[1].connect(ssid, psk="12345678", ieee80211w="2", key_mgmt="WPA-PSK WPA-PSK-SHA256", proto="WPA2")
    hwsim_utils.test_connectivity(dev[1].ifname, ap_ifname)
    wt.require_ap_pmf_optional(bssid)
    wt.require_sta_pmf(bssid, dev[0].p2p_interface_addr())
    wt.require_sta_key_mgmt(bssid, dev[0].p2p_interface_addr(), "PSK-SHA256")
    wt.require_sta_pmf_mandatory(bssid, dev[1].p2p_interface_addr())
    wt.require_sta_key_mgmt(bssid, dev[1].p2p_interface_addr(), "PSK-SHA256")

def test_ap_pmf_negative(dev):
    """WPA2-PSK AP without PMF (negative test)"""
    ssid = "test-pmf-negative"
    wt = Wlantest()
    wt.flush()
    wt.add_passphrase("12345678")
    params = hostapd.wpa2_params(ssid=ssid, passphrase="12345678")
    hostapd.add_ap(ap_ifname, params)
    dev[0].connect(ssid, psk="12345678", ieee80211w="1", key_mgmt="WPA-PSK WPA-PSK-SHA256", proto="WPA2")
    hwsim_utils.test_connectivity(dev[0].ifname, ap_ifname)
    try:
        dev[1].connect(ssid, psk="12345678", ieee80211w="2", key_mgmt="WPA-PSK WPA-PSK-SHA256", proto="WPA2")
        hwsim_utils.test_connectivity(dev[1].ifname, ap_ifname)
        raise Exception("PMF required STA connected to no PMF AP")
    except Exception, e:
        logger.debug("Ignore expected exception: " + str(e))
    wt.require_ap_no_pmf(bssid)