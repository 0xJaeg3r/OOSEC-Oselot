# Tools

### Recon agents  (Subdomains and Apex Domains)

## Finding ASN's
url: bgp.he.net (This is their owned infrastructure)
url: dnschecker.org 

## Tenant Domains
tenant-domains.sh

## ASN to Port scans
'''
echo AS394161 | asnmap -silent | naabu -silent --nmap-cli 'nmap -sV'

'''
Naabu
asnmap
nmapcli

## Passive Port Scanning 
SMAP
Shodan but Use Karma v2 (Its a shodan wrapper)

## Karma Signature Creation


## Aquisitions
tracxn.com
pitchbook.com

## Cloud recon
https://github.com/lord-alfred/blob/main/all/ipv4_merged.txt
get ip ranges here

scanning the cloud for certs
Caduceous - takes long to scan

kaeferjaeger.gay

gungnir - github

## Subdomain scraping
Subfinder
bbot finds 5 to 8% more subdomains

chaos ## dns scanning free. add as a source to subfinder
add github api key to subfinder to find  company repos
you can hook shodan into subfinder too  
