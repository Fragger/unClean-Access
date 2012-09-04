import urllib, urllib2, ConfigParser, re, platform, getpass, _winreg
from lxml.html import etree

def setCreds(regKey):
    userName = raw_input('Enter Username: ')
    password = getpass.getpass('Enter Password: ')
    if platform.system()=='Windows':
        try:
            key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, regKey, 0, _winreg.KEY_ALL_ACCESS)
        except:
            key = _winreg.CreateKey(_winreg.HKEY_CURRENT_USER, regKey)
        _winreg.SetValueEx(key, 'Username', 0, _winreg.REG_SZ, userName)
        _winreg.SetValueEx(key, 'Password', 0, _winreg.REG_SZ, password)
        _winreg.CloseKey(key)
    return (userName, password)

def auth(user, passwd):
    os = 'Linux'
    useragent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:14.0) Gecko/20100101 Firefox/14.0.1'
    AuthCheckURL = 'http://google.com/'

    parser = etree.HTMLParser()

    config = ConfigParser.SafeConfigParser({'os': os, 'useragent': useragent, 'debug': 'False'})
    config.read('unCleanAccess.cfg')
    if not config.has_section('login'):
        config.add_section('login')

    debug = config.get('login', 'debug') in ('True', 'true')

    print 'Checking if Authenticated'
    if not debug:
        responseAuthCheck = urllib2.urlopen(AuthCheckURL)
        AuthCheckhtml = responseAuthCheck.read()
    else:
        f = open('unCleanAuthCheckunauthed.html','r')
        AuthCheckhtml = f.read()
        f.close()

    if AuthCheckhtml.find('/auth/perfigo_weblogin.jsp') != -1:
        print 'Not Authenticated Yet'
        urlSplit = AuthCheckhtml.split('URL=')
        if len(urlSplit) != 2:
            print 'Error extracting redirect URL (1)'
        else:
            urlSplit = re.split("'>|;", urlSplit[1])
            if len(urlSplit) < 2:
                print 'Error extracting redirect URL (2)'
            else:
                print 'Fetching Login Page'
                if not debug:
                    responseAuthPage = urllib2.urlopen(urlSplit[0])
                    AuthPagehtml = etree.parse(responseAuthPage, parser)
                else:
                    f = open('authPage.html','r')
                    AuthPagehtml = etree.parse(f, parser)
                    f.close()

                print 'Parsing Login Page'
                POSTDataItems = dict()
                for formInput in AuthPagehtml.xpath(".//form[@name='loginform']//input"):
                    if formInput.get('name'):
                        POSTDataItems[formInput.get('name')] = formInput.get('value')
        
                POSTDataItems['pm'] = config.get('login', 'os')
                POSTDataItems['username'] = user
                POSTDataItems['password'] = passwd

                authData = urllib.urlencode(POSTDataItems)
                authHeaders = {'Referer' : urlSplit[0].split('perfigo_weblogin.jsp', 1)[0], 'User-Agent' : config.get('login', 'useragent')}

                print 'Logging in'
                authReq = urllib2.Request(urlSplit[0].split('auth/perfigo_weblogin.jsp', 1)[0] + AuthPagehtml.xpath(".//form[@name='loginform']")[0].get('action').split('/', 1)[1], authData, authHeaders)
                responseAuthReq = urllib2.urlopen(authReq)
                authReqhtml = responseAuthReq.read()

                if authReqhtml.find('You have been successfully logged on the network') != -1:
                    print 'Successfuly Authenticated!'
                else:
                    print 'Invalid credentials'
                    (userName, password) = setCreds(regKeyVal)
                    auth(userName, password)
                    
                
    else:
        print 'Already Authenticated'

regKeyVal = 'Software\unClean Access'

try:
    key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, regKeyVal, 0, _winreg.KEY_ALL_ACCESS)
    userName = _winreg.QueryValueEx(key, 'Username')[0]
    password = _winreg.QueryValueEx(key, 'Password')[0]
except:
    (userName, password) = setCreds(regKeyVal)

auth(userName, password)

raw_input('Press ENTER to continue...\n')
