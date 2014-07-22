#!/bin/python

# Authors: Petr Spacek <pspacek@redhat.com>
#
# Copyright (C) 2013  Red Hat
# see file 'COPYING' for use and warranty information
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; version 2 or later
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#

import ldif
import sys
import StringIO

import dns.zone
import dns.rdatatype
import pdb


class Name:
    def __init__(self, name, zone, base):
        self.name = name
        self.zone = zone
        self.base = base
        self.ttl = None
        self.records = {}
        self.ldap_obj = {'objectClass': ['idnsRecord', 'top']}

    def is_origin(self):
        '''Return True iff name == zone.origin'''
        result = self.name.derelativize(self.zone.origin).fullcompare(self.zone.origin)
        if result[:2] == (dns.name.NAMERELN_EQUAL, 0):
            return True
        else:
            return False

    def update_ttl(self, rrset):
        if self.ttl:
            self.ttl = min(self.ttl, rrset.ttl)
        else:
            self.ttl = rrset.ttl

    def add_normal_record(self, rr):
        t = dns.rdatatype.to_text(rr.rdtype)
        t += 'record'
        rrset = self.records.setdefault(t, [])
        rrset.append(rr.to_text())

    def add_soa_record(self, rr):
        self.records['idnsSOAexpire'] = [str(int(rr.expire))]
        self.records['idnsSOAminimum'] = [str(int(rr.minimum))]
        self.records['idnsSOAmName'] = [str(rr.mname)]
        self.records['idnsSOArefresh'] = [str(int(rr.refresh))]
        self.records['idnsSOAretry'] = [str(int(rr.retry))]
        self.records['idnsSOArName'] = [str(rr.rname)]
        self.records['idnsSOAserial'] = [str(int(rr.serial))]
        self.records['idnsZoneActive'] = ['TRUE']
        self.ldap_obj['objectClass'].append('idnsZone')

    def add_record(self, rr):
        #pdb.set_trace()
        if rr.rdtype == dns.rdatatype.SOA:
            self.add_soa_record(rr)
        else:
            self.add_normal_record(rr)

    def __str__(self):
        if self.is_origin():
            self.dn = 'idnsName={z},{b}'.format(z=zone.origin, b=base)
            self.ldap_obj['idnsName'] = [str(zone.origin)]
        else:
            self.dn = 'idnsName={n},idnsName={z},{b}'.format(n=name, z=zone.origin,
                                                             b=base)
            self.ldap_obj['idnsName'] = [str(name)]

        self.ldap_obj.update(self.records)

        if self.ttl:
            self.ldap_obj['DNSTTL'] = [str(self.ttl)]

        buff = StringIO.StringIO()
        ldifw = ldif.LDIFWriter(buff)
        ldifw.unparse(self.dn, self.ldap_obj)
        return buff.getvalue()

#pdb.set_trace()

if len(sys.argv) != 4:
    print 'Usage:   ' + sys.argv[0] + ' <zone file> <zone origin> <LDAP DNS base>'
    print 'Example: ' + sys.argv[0] + ' /var/named/zone.example.com.db zone.example.com. "cn=dns, dc=ipa, dc=example, dc=com"'
    sys.exit(1)

infile = open(sys.argv[1])
zone = dns.zone.from_file(infile, origin=sys.argv[2])

#base = 'cn=dns, dc=e, dc=test'
base = sys.argv[3]

for name in zone:
    n = Name(name, zone, base)
    for rrset in zone[name]:
        n.update_ttl(rrset)
        for rr in rrset.items:
            n.add_record(rr)
    print n
