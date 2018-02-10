import cookielib
import json
import urllib2
import urllib
import ConfigParser
import httplib

config=ConfigParser.RawConfigParser()
config.read('spectrum.cfg')
username=config.get('credentials','username')
password=config.get('credentials','password')
serverList=config.get('spectrum','servers').split(',')
dburl=config.get('influxdb','db_url')
dbuser=config.get('influxdb','db_user')
dbuser=config.get('influxdb','db_password')
dbname=config.get('influxdb','db_name')

values = {'j_username' : username,
          'j_password' : password}

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

def writedb(data):
    pass


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
    url = 'https://' + server + ':9569/srm/REST/api/v1/StorageSystems/' + storageSystem['id'] + '/Pools'
    contentPOOLS=fetch(url)
    jsonContentPOOLS = json.loads(contentPOOLS.read())
    for storagePool in jsonContentPOOLS:
        print("\\-- Pool: %s, %s" % (storagePool['id'], storagePool['Name']))
    url = 'https://' + server + ':9569/srm/REST/api/v1/StorageSystems/' + storageSystem['id'] + '/Volumes'
    contentVols=fetch(url)
    jsonContentVols=json.loads(contentVols.read())
    for volum in jsonContentVols:
        print("\\-- Volume: %s, %s (Pool: %s)" % (volum['id'], volum['Name'], volum['Pool']))
    
	
