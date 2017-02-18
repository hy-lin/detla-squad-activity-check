'''
Created on Jul 2, 2016

@author: Cog Vokan
'''
import urllib.request
import datetime
import xml.etree.ElementTree as ET
import json

def _getWalletJournalThroughAPI(character_ID):
    '''
    Placeholder code
    Please replace this part with your own API thingy.
    '''
    api_address = "https://api.eveonline.com/char/WalletJournal.xml.aspx?characterID=94853925&rowCount=2560&keyID=6005092&vCode=VrTqRSYz7UqiIE1oQXvWoD6tjtRyN83nLqEbMVAOhbLtblgAxH7LWOzoSuwWBzr6"
    respond = urllib.request.urlopen(api_address)
    return respond.read()
    
class RattingTick(object):
    def __init__(self, amount, time):
        self.amount = float(amount)
        self.time = time
        
    def getDuration(self):
        scaler = self.amount / 1200.0 # assuming typical tick is 12m
        
        if scaler >= 1.0:
            scaler = 1.0
            
        scaler = abs(scaler)
            
        return datetime.timedelta(0, 20) * scaler 
    
    def __str__(self):
        return 'date: {}, amount: {}, duration: {}'.format(self.time, self.amount, self.getDuration())
        
def getRattingHistory(character_ID):
    journal_history = _getWalletJournalThroughAPI(character_ID)
    
    xml_tree = ET.fromstring(journal_history)
    ratting_ticks = []
    for row in xml_tree.iter('row'):
        if row.get('refTypeID') == '15': # 85 is the bounty reference type
            ratting_ticks.append(RattingTick(row.get('amount'), row.get('date')))
            
    return ratting_ticks

def getID(character_name):
    character_name = character_name.replace(' ', '%20')
    api_address =  'https://api.eveonline.com/eve/CharacterID.xml.aspx?names={}'.format(character_name)
    respond = urllib.request.urlopen(api_address)
    character_info = respond.read()
    
    xml_tree = ET.fromstring(character_info)
    for row in xml_tree.iter('row'):
        ID = row.get('characterID')
    

    return int(ID)

def getCorpName(character_ID):
    api_address =  'https://api.eveonline.com/eve/CharacterInfo.xml.aspx?characterID={}'.format(character_ID)
    respond = urllib.request.urlopen(api_address)
    character_info = respond.read()
    
    xml_tree = ET.fromstring(character_info)
    
    for row in xml_tree.iter('corporation'):
        corp_name = row.text
        
    return corp_name

class ZKillRequest(urllib.request.Request):
    def __init__(self, character_ID, page):
        url = 'https://zkillboard.com/api/characterID/{}/page/{}/no-items/'.format(character_ID, page)
        urllib.request.Request.__init__(self, url = url, \
            headers = {'User-Agent': 'https://pleaseignore.com Maintainer: CogVokan@pleaseignore.com'})
        
class ZKillStatsRequest(urllib.request.Request):
    def __init__(self, character_ID):
        url = 'https://zkillboard.com/api/stats/characterID/{}/'.format(character_ID)
        urllib.request.Request.__init__(self, url = url, \
            headers = {'User-Agent': 'https://pleaseignore.com Maintainer: CogVokan@pleaseignore.com'})
        
class Member(object):
    def __init__(self, main_character):
        self.main_character = main_character
        self.alts = []
        
    def addAlt(self, alt_name):
        self.alts.append(alt_name)
        
    def getKillCounts(self, year_and_month):
        main_ID = getID(self.main_character)
        self.kill_count = getKillPerMonth(main_ID, year_and_month)
        
        for alt in self.alts:
            alt_id = getID(alt)
            self.kill_count += getKillPerMonth(alt_id, year_and_month)
            
        return self.kill_count
            
    def getCorpName(self):
        main_ID = getID(self.main_character)
        self.corp_name = getCorpName(main_ID)
        
        return self.corp_name

def getKillMails(character_ID):
    kms = []
    page = 1
    current_time = datetime.datetime(1111, 11, 11)
    current_time = current_time.today()
    
    keep_pulling = True
    while keep_pulling:
        km_request = ZKillRequest(character_ID, page)
        respond = urllib.request.urlopen(km_request)
        new_kms = eval(respond.read())
        
        km_time = datetime.datetime(1111, 11, 11)
        km_time = km_time.strptime(new_kms[-1]['killTime'], '%Y-%m-%d %H:%M:%S')
        
        diff = current_time - km_time
        if diff.days >= 30:
            keep_pulling = False
        
        if len(new_kms) < 200:
            keep_pulling = False    
            
        kms += new_kms
        if len(kms) >= 800:
            keep_pulling = False
        
        page += 1
        
    return kms

def getKillPerMonth(character_ID, month = '201606'):
    stats_request = ZKillStatsRequest(character_ID)
    respond = urllib.request.urlopen(stats_request)
    stats = json.loads(respond.read().decode('utf-8'))
    try:
        return stats['months'][month]['shipsDestroyed']
    except:
        return 0
    
def checkActivity(year_and_month, member_list):
    output_file = open('activity_{}.txt'.format(year_and_month), 'w')
    
    for member in member_list:
        try:
            corp_name = member.getCorpName()
        except:
            corp_name = 'coupbois'
        kill_count = member.getKillCounts(year_and_month)
        
        output_file.write('{}\t{}\t{}\n'.format(member.main_character, corp_name, kill_count))
        print('{}\t{}\t{}'.format(member.main_character, corp_name, kill_count))
        
    output_file.close()
        
def main():
    month = input('Input the month you want to check (e.g. 201611): ')
    input_file = open('member_list.txt', 'r')
    members = []
    for line in input_file:
        new_line = line.strip()
        names = new_line.split('\t')
        
        new_member = Member(names[0])
        for i in range(1, len(names)):
            new_member.addAlt(names[i])
        
        members.append(new_member)
        
    checkActivity(month, members)
        

def test():
    ticks = getRattingHistory(999)
    for tick in ticks:
        print(tick)

if __name__ == '__main__':
    test()
    
    pass