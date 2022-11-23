import requests, json, base64, sys, time
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import xml.etree.ElementTree as ET
from datetime import datetime
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    
def backup_machine(address, username, password, soma_port, domains2backup, ignore_tls_issues):
    print('Trying to access ' + address + '\'s XML Management Interface...')
    url = 'https://' + address + ':' + str(soma_port) + '/service/mgmt/3.0'
    headers = {'Authorization' : 'Basic ' + str(base64.b64encode((username + ':' + password).encode()).decode())}
    payload = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:man="http://www.datapower.com/schemas/management"><soapenv:Header/><soapenv:Body><man:request domain="default"><man:do-backup format="ZIP">'
    for domain in domains2backup:
        payload += '<man:domain name="' + domain + '"/>'
    payload += '</man:do-backup></man:request></soapenv:Body></soapenv:Envelope>'
    response = requests.post(url, data = payload, headers = headers, verify = not ignore_tls_issues)
    print('Got response, looking for the ZIP content...')
    root = ET.fromstring(response.content)
    fetch_xml_element(root)
    output_file = 'backup_' + datetime.today().strftime('%Y-%m-%d') + '_' + address + '.zip'
    if (file_content == ''):
        output_file = 'backup-' + address + '.xml'
        print('No ZIP file returned, please check response content.')
    else:
        print('ZIP found, saving to disk...')
    with open(output_file, "wb") as backup_file:
        backup_file.write(base64.b64decode(file_content))
    print('Done!')
    
def secure_backup_machine(address, username, password, soma_port, crypto_certificate_name, backup_destination, ignore_tls_issues):
    print('Trying to access ' + address + '\'s XML Management Interface...')
    url = 'https://' + address + ':' + str(soma_port) + '/service/mgmt/amp/3.0'
    headers = {'Authorization' : 'Basic ' + str(base64.b64encode((username + ':' + password).encode()).decode())}
    payload = '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ns="http://www.datapower.com/schemas/appliance/management/3.0"><soapenv:Header/><soapenv:Body><ns:SecureBackupRequest><ns:CryptoCertificateName>' + crypto_certificate_name + '</ns:CryptoCertificateName><ns:SecureBackupDestination>' + backup_destination + '</ns:SecureBackupDestination></ns:SecureBackupRequest></soapenv:Body></soapenv:Envelope>'
    response = requests.post(url, data = payload, headers = headers, verify = not ignore_tls_issues)
    if b'<amp:Status>ok</amp:Status>' in response.content:
        print('Secure backup done successfully.')
    else:
        print('Secure backup failed.')

file_content = ''
def fetch_xml_element(node):
    global file_content
    for child in node.findall('*'):
        if (child.tag == '{http://www.datapower.com/schemas/management}file'):
            file_content = child.text
        else:
            fetch_xml_element(child)


backup_machine('machine1', 'user', 'pass', 5550, ['domain1', 'domain2'], True)
#backup_machine('machine2', 'user', 'pass', 5550, ['domain1', 'domain2', 'domain3'], True)

secure_backup_machine('machine1', 'user', 'pass', 5550, 'backup', 'ftp://username:password@ftpserver/datapowerbackup', True)
#secure_backup_machine('machine1', 'user', 'pass', 5550, 'backup', 'temporary:///securebackup', True)
