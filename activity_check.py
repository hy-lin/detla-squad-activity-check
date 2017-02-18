'''
Created on Jul 2, 2016

@author: Cog Vokan
'''
import urllib.request
import datetime
import xml.etree.ElementTree as ET
import json
import gzip


class RattingTick(object):
    def __init__(self, amount, time):
        self.amount = float(amount)
        self.time = datetime.datetime(1, 1, 1).strptime(time, '%Y-%m-%d %H:%M:%S')
        self.duration = self._getDuration()
        
    def _getDuration(self):
        scaler = self.amount / 1200.0 # assuming typical tick is 12m
    
        scaler = abs(scaler)
        if scaler >= 1.0:
            scaler = 1.0
            
        return datetime.timedelta(minutes = 20) * scaler 
    
    def __str__(self):
        return 'date: {}, amount: {}, duration: {}'.format(self.time, self.amount, self.duration)

class ZKillRequest(urllib.request.Request):
    def __init__(self, character_ID, page):
        url = 'https://zkillboard.com/api/characterID/{}/page/{}/no-items/'.format(character_ID, page)
        urllib.request.Request.__init__(self, url = url, \
            headers = {'User-Agent': 'https://pleaseignore.com Maintainer: CogVokan@pleaseignore.com', \
                       'Accept-Encoding': 'gzip'})
        
class ZKillStatsRequest(urllib.request.Request):
    def __init__(self, character_ID):
        url = 'https://zkillboard.com/api/stats/characterID/{}/'.format(character_ID)
        urllib.request.Request.__init__(self, url = url, \
            headers = {'User-Agent': 'https://pleaseignore.com Maintainer: CogVokan@pleaseignore.com', \
                       'Accept-Encoding': 'gzip'})
        
class KillMail(object):
    def __init__(self, zkb_info, owner_id):
        self.zkb_info = zkb_info
        self._parseZKBInfo(owner_id)
        
    def _parseZKBInfo(self, owner_id):
        self.time = datetime.datetime(1, 1, 1).strptime(self.zkb_info['killTime'], '%Y-%m-%d %H:%M:%S')
        
        if self.zkb_info['victim']['characterID'] == int(owner_id):
            self.kill = False
        else:
            self.kill = True
            
        self.duration = datetime.timedelta(hours = 1)
        
        
class Member(object):
    def __init__(self, main_character):
        self.main_character = main_character
        self.alts = []
        self.kms = []
        self.ratting_ticks = []
        
    def addAlt(self, alt_name):
        self.alts.append(alt_name)
            
    def getCorpName(self):
        main_ID = getID(self.main_character)
        self.corp_name = getCorpName(main_ID)
        
        return self.corp_name
    
    def pullKillMails(self):
        self.kms = []
        
        main_ID = getID(self.main_character)
        self.kms += getKillMails(main_ID)
        
        for alt in self.alts:
            alt_ID = getID(alt)
            self.kms += getKillMails(alt_ID)
            
        self.kms.sort(key = lambda km: km.time)
            
    def pullRattingTicks(self):
        self.ratting_ticks = []
        
        main_ID = getID(self.main_character)
        self.ratting_ticks += getRattingHistory(main_ID)
        
        for alt in self.alts:
            alt_ID = getID(alt)
            self.ratting_ticks += getRattingHistory(alt_ID)
        
        self.ratting_ticks.sort(key = lambda tick:tick.time)
            
    def getKrabScore(self):
        if len(self.kms) == 0:
            self.pullKillMails()
            
        if len(self.ratting_ticks) == 0:
            self.pullRattingTicks()
            
        ratting_time = self._getDuration(self.ratting_ticks)
        killing_time = self._getDuration(self.kms)
        
        print('Ratting time: {}; Killing time: {}; Ratio: {}'.format(ratting_time.total_seconds()/60, killing_time.total_seconds()/60, ratting_time/killing_time))
        
    def _getDuration(self, events):
        activity = datetime.timedelta(0, 0)
        
        last_event_time = datetime.datetime(1969, 7, 20)
        
        for event in events:
            
            
            if event.time - last_event_time < event.duration:
                activity += (event.time - last_event_time)
            else:
                activity += event.duration
                                
            last_event_time = event.time
                
        return activity

def _getWalletJournalThroughAPI(character_ID):
    '''
    Placeholder code
    Please replace this part with your own API thingy.
    '''
    api_address = "https://api.eveonline.com/char/WalletJournal.xml.aspx?characterID=94853925&rowCount=2560&keyID=6005092&vCode=VrTqRSYz7UqiIE1oQXvWoD6tjtRyN83nLqEbMVAOhbLtblgAxH7LWOzoSuwWBzr6"
    respond = urllib.request.urlopen(api_address)
    return respond.read()
        
def getRattingHistory(character_ID):
    journal_history = _getWalletJournalThroughAPI(character_ID)
    
    xml_tree = ET.fromstring(journal_history)
    ratting_ticks = []
    for row in xml_tree.iter('row'):
        if row.get('refTypeID') == '85': # 85 is the bounty reference type
            ratting_ticks.append(RattingTick(row.get('amount'), row.get('date')))
            
    return ratting_ticks

def getXMLAPIResponse(address, tries = 0):
    
    if tries >= 5:
        print('fail to retrieve address: {}'.format(address))
        return 'fail'
    
    try:
        respond = urllib.request.urlopen(address, timeout=5)
        return respond.read()
    except:
        return getXMLAPIResponse(address, tries + 1)

def getID(character_name):
    character_name = character_name.replace(' ', '%20')
    api_address =  'https://api.eveonline.com/eve/CharacterID.xml.aspx?names={}'.format(character_name)

    character_info = getXMLAPIResponse(api_address)
    
    xml_tree = ET.fromstring(character_info)
    for row in xml_tree.iter('row'):
        ID = row.get('characterID')

    return int(ID)

def getCorpName(character_ID):
    api_address =  'https://api.eveonline.com//eve/CharacterInfo.xml.aspx?characterID={}'.format(character_ID)
    character_info = getXMLAPIResponse(api_address)
    
    xml_tree = ET.fromstring(character_info)
    
    for row in xml_tree.iter('corporation'):
        corp_name = row.text
        
    return corp_name

def getKillMails(character_ID):
    kms = []
    page = 1
    current_time = datetime.datetime(1111, 11, 11)
    current_time = current_time.today()
    
    keep_pulling = True
    while keep_pulling:
        km_request = ZKillRequest(character_ID, page)
        respond = urllib.request.urlopen(km_request)
        new_kms = json.loads(gzip.decompress(respond.read()).decode('utf-8'))
        
        if len(new_kms) <= 0:
            keep_pulling = False
            break
        
        for new_km in new_kms:
            km = KillMail(new_km, character_ID)
            diff = current_time - km.time
            if diff.days >= 30:
                keep_pulling = False
                break
            kms.append(km)
        
        if len(new_kms) < 200:
            keep_pulling = False    

                
        page += 1
        
    return kms
    
def test():
    ticks = getRattingHistory(999)
    for tick in ticks:
        print(tick)

if __name__ == '__main__':
    cog = Member('Cog Vokan')
    cog.getKrabScore()
    
    pass