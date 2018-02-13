import time
import cookielib
import string
from string import replace
import json
import urllib2
import urllib
import ConfigParser
import httplib
timest=(repr(time.time()).replace(".","")+'0000000')[0:19]

config=ConfigParser.RawConfigParser()
config.read('spectrum.cfg')
username=config.get('credentials','username')
password=config.get('credentials','password')
serverList=config.get('spectrum','servers').split(',')
dburl=config.get('influxdb','db_url')
dbuser=config.get('influxdb','db_user')
dbpassword=config.get('influxdb','db_password')
dbname=config.get('influxdb','db_name')

values = {'j_username' : username,
          'j_password' : password}

writebuff=''

data = urllib.urlencode(values)

cookies = cookielib.LWPCookieJar()
handlers = [
    urllib2.HTTPHandler(),
    urllib2.HTTPSHandler(),
    urllib2.HTTPCookieProcessor(cookies)
    ]
opener = urllib2.build_opener(*handlers)

def fetch(uri):
    req = urllib2.Request(uri)
    return opener.open(req)

def fetchp(uri, data):
    req = urllib2.Request(uri, data)
    return opener.open(req)

def dump():
    for cookie in cookies:
        print cookie.name, cookie.value

def flushbuf():
    global writebuff
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    try:
       conn=httplib.HTTPConnection(dburl)
       conn.request('POST', '/write?db=' + dbname + '&u=' + dbuser + '&p=' + dbpassword, writebuff, headers)
       respi=conn.getresponse()
       print respi.read()
       conn.close()
    except:
       pass
    writebuff='' 

def writedb(data):
    global writebuff
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    writebuff=writebuff + data  + ' ' + timest + '\n'
    print data
    if len(writebuff) > 5000:
       flushbuf()
       

for server in serverList:
  print server

  url = 'https://' + server + ':9569/srm/j_security_check'
  print url
  content = fetchp (url,data)
  dump()
  #print content.read()
  url = 'https://' + server + ':9569/srm/REST/api/v1/StorageSystems'
  print url
  content = fetch(url)
  #print content.read()

  jsonContentSS = json.loads(content.read())
  for storageSystem in jsonContentSS:
    print("Sys: %s, %s" % (storageSystem['id'], storageSystem['Name']))
    insertion='storagesystem,server=' + server + ',id=' + storageSystem['id'] + ',name=' + replace(storageSystem['Name'],' ','') + ' PhysicalAllocation=' + replace(storageSystem['Physical Allocation'], ',','')
    writedb(insertion)
    url = 'https://' + server + ':9569/srm/REST/api/v1/StorageSystems/' + storageSystem['id'] + '/Pools'
    contentPOOLS=fetch(url)
    jsonContentPOOLS = json.loads(contentPOOLS.read())
    for storagePool in jsonContentPOOLS:
        insertion='pool,server=' + server + ',id=' + storagePool['id'] + ',name=' + replace(storagePool['Name'],' ','') + ',storagesystem=' + replace(storagePool['Storage System'],' ','') + ' PhysicalAllocation=' + replace(storagePool['Physical Allocation'],',','')
        writedb(insertion)
        print("\\-- Pool: %s, %s" % (storagePool['id'], storagePool['Name']))
    url = 'https://' + server + ':9569/srm/REST/api/v1/StorageSystems/' + storageSystem['id'] + '/Volumes'
    contentVols=fetch(url)
    jsonContentVols=json.loads(contentVols.read())
    for volum in jsonContentVols:
        insertion='volume,server=' + server + ',id=' + volum['id'] + ',name=' + replace(volum['Name'],' ','') + ',storagesystem=' + replace(volum['Storage System'],' ','') + ',pool=' + replace(volum['Pool'],' ','') + ' capacity=' + replace(volum['Capacity'],',','') + ',allocatedspace=' + replace(volum['Allocated Space'],',','')
        writedb(insertion)
        print("\\-- Volume: %s, %s (Pool: %s)" % (volum['id'], volum['Name'], volum['Pool']))
    
flushbuf()
	
