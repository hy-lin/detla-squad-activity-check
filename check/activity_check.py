'''
Created on Jul 2, 2016

@author: Cog Vokan
'''
import urllib.request
import datetime
import xml.etree.ElementTree as ET


def getID(character_name):
    character_name = character_name.replace(' ', '%20')
    api_address =  'https://api.eveonline.com/eve/CharacterID.xml.aspx?names={}'.format(character_name)
    respond = urllib.request.urlopen(api_address)
    character_info = respond.read()
    
    infos = character_info.split('\n')
    for line in infos:
        if 'row name' in line:
            character_info = ET.fromstring(line)
            

    return int(character_info.get('characterID'))

def getCorpName(character_ID):
    api_address =  'https://api.eveonline.com//eve/CharacterInfo.xml.aspx?characterID={}'.format(character_ID)
    respond = urllib.request.urlopen(api_address)
    character_info = respond.read()
    
    infos = character_info.split('\n')
    for line in infos:
        if '<corporation>' in line:
            character_info = ET.fromstring(line)

    return character_info.text

class ZKillRequest(urllib.request.Request):
    def __init__(self, character_ID, page):
        url = 'https://zkillboard.com/api/characterID/{}/page/{}/no-items/'.format(character_ID, page)
        urllib.request.Request.__init__(self, url = url, \
            headers = {'User-Agent': 'https://pleaseignore.com Maintainer: CogVokan@pleaseignore.com'}) 

def getKillMails(character_ID):
    kms = []
    page = 1
    current_time = datetime.datetime(1111, 11, 11)
    current_time = current_time.today()
    
    enough_km = False
    while not enough_km:
        km_request = ZKillRequest(character_ID, page)
        respond = urllib.request.urlopen(km_request)
        new_kms = eval(respond.read())
        
        km_time = datetime.datetime(1111, 11, 11)
        km_time = km_time.strptime(new_kms[-1]['killTime'], '%Y-%m-%d %H:%M:%S')
        
        diff = current_time - km_time
        if diff.days >= 100:
            enough_km = True
        
        if len(new_kms) < 200:
            enough_km = True    
            
        kms += new_kms
        if len(kms) >= 800:
            enough_km = True
        
        page += 1
        
    return kms

def getKillPerMonth(character_ID, month = '201606'):
    api_address = 'https://zkillboard.com/api/stats/characterID/{}'.format(character_ID, month)
    respond = urllib.request.urlopen(api_address)
    stats = eval(respond.read())
    try:
        return stats['months'][month]['shipsDestroyed']
    except:
        return 0

def checkActivity(year_and_month, member_list):
    # check if year_and_month is valid
    if len(year_and_month) != 6:
        raise ValueError('Invalid year_and_month value.')

    members = member_list.split('\n')
    
    output_text = '<table style="width:100%">'
    
    for member in members:
        member = member.replace('\r', '')
        try:
            character_id = getID(member)
            corp_name = getCorpName(character_id)
        except:
            character_id = "Failed to retrieve Character ID"
            corp_name = ''
            n_kills = None
        
        if character_id != "Failed to retrieve Character ID":
            try:
                n_kills = getKillPerMonth(character_id, year_and_month)
            except:
                n_kills = 'Failed to retrieve kills'

        
        output_text += '<tr><td>{}<//td><td>{}<//td><td>{}<//td><td>{}<//td><//tr>'.format(member, character_id, corp_name, n_kills)
        
    output_text += '<//table>'
    return output_text

if __name__ == '__main__':
    pass