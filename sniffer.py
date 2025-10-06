#!/usr/bin/env python3
from scapy.all import *

def print_pkt(pkt):
    pkt.show()

pkt = sniff(iface="docker0", filter="net 172.17.0.0/16", prn=print_pkt)