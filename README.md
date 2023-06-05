# zone2ldap

This hacky script reads DNS master file (RFC 1035 section 5)
and outputs LDIF file with data suitable for bind-dyndb-ldap plugin.

## Usage
```bash
zone2dyndb-ldif.py <zone file> <zone origin> <LDAP DNS base>
``` 

### Example
- Zone (master) file: `/var/named/zone.example.com.db`
- Zone name (origin): `zone.example.com.`
- DN of DNS container in your LDAP tree: `"cn=dns, dc=ipa, dc=example, dc=com"`
  - This example corresponds to FreeIPA domain `"ipa.example.com."`
- Command: 
  ```bash
  zone2dyndb-ldif.py /var/named/zone.example.com.db zone.example.com. "cn=dns, dc=ipa, dc=example, dc=com"
  ```

### How to get the `DN` in your FreeIPA LDAP tree

1. If needed create a kerberos ticket
    ```bash
    # admin can be replaced with a user of course
    kinit admin 
    ```

2. Run a search against your ldap for the `ipaDNSContainer`
    ```bash
    ldapsearch objectClass=ipaDNSContainer dn
    ```

## Depedencies

- DNSpython: http://dnspython.org/ (Fedora package python-dns)
- python-ldap: http://www.python-ldap.org/ (Fedora package python-ldap)

## Useful links

- bind-dyndb-ldap - LDAP backend for BIND 9: https://fedorahosted.org/bind-dyndb-ldap/
- FreeIPA - domain controller for Linux/Unix world: http://www.freeipa.org/
