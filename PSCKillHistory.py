import urllib.request
import datetime
import xml.etree.ElementTree as ET
import json
import gzip
import time

class KillMail(object):
    def __init__(self, zkb_info, owner_id):
        self.zkb_info = zkb_info
        self._parseZKBInfo(owner_id)
        
    def _parseZKBInfo(self, owner_id):
        self.time = datetime.datetime(1, 1, 1).strptime(self.zkb_info['killmail_time'], '%Y-%m-%dT%H:%M:%SZ')
        
        if self.zkb_info['victim']['corporation_id'] == int(owner_id):
            self.kill = False
            self.alliance = 'PSC'
        else:
            self.kill = True
            try:
                self.alliance = GetAllianceName(self.zkb_info['victim']['alliance_id']).get()['ticker']
            except:
                self.alliance = 'None'

        self.solarSystemID = self.zkb_info['solar_system_id']
        self.shipTypeID = self.zkb_info['victim']['ship_type_id']
        
class ZKillRequest(urllib.request.Request):
    def __init__(self, corporation_ID, page):
        url = 'https://zkillboard.com/api/corporationID/{}/page/{}/no-items/no-attackers/'.format(corporation_ID, page)
        urllib.request.Request.__init__(self, url = url, \
            headers = {'User-Agent': 'https://pleaseignore.com Maintainer: CogVokan@pleaseignore.com', \
                       'Accept-Encoding': 'gzip'})

class GetAllianceName(urllib.request.Request):
    def __init__(self, alliance_id):
        url = 'https://esi.evetech.net/latest/alliances/{}/?datasource=tranquility'.format(alliance_id)
        urllib.request.Request.__init__(self, url = url)

    def get(self):
        respond = urllib.request.urlopen(self)
        return json.loads(respond.read())

class GetName(urllib.request.Request):
    def __init__(self, alliance_id):
        url = 'https://esi.evetech.net/latest/alliances/{}/?datasource=tranquility'.format(alliance_id)
        urllib.request.Request.__init__(self, url = url)

    def get(self):
        respond = urllib.request.urlopen(self)
        return json.loads(respond.read())


def getKillMails(corporation_ID, output_file):
    kms = []
    page = 1
    earliest_time = datetime.datetime(1111, 11, 11)
    earliest_time = earliest_time.today()

    
    keep_pulling = True
    while keep_pulling:
        km_request = ZKillRequest(corporation_ID, page)
        respond = urllib.request.urlopen(km_request)
        new_kms = json.loads(gzip.decompress(respond.read()).decode('utf-8'))

        # if len(new_kms) <= 0:
        #     keep_pulling = False
        #     break
        
        for new_km in new_kms:
            km = KillMail(new_km, corporation_ID)
            kms.append(km)

            if km.time < earliest_time:
                earliest_time = km.time

            output_string = ''
            output_string += '{}\t'.format(km.alliance)
            output_string += '{}\t'.format(km.shipTypeID)
            output_string += '{}\t'.format(km.solarSystemID)
            output_string += '{}\n'.format(km.time)

            output_file.write(output_string)
        
        if len(new_kms) < 200:
            keep_pulling = False

        print('finished page {}'.format(page))
        time.sleep(30)
        page += 1
    return kms, earliest_time

def outputToFile(kms, earliest_time):
    output_file = open('kms.txt', 'w')

    for km in kms:
        diff_time = km.time - earliest_time
        output_string = ''
        output_string += '{}\t'.format(km.alliance)
        output_string += '{}\t'.format(km.shipTypeID)
        output_string += '{}\t'.format(km.solarSystemID)
        output_string += '{}\n'.format(diff_time.days)

        output_file.write(output_string)

    output_file.close()

def main():
    output_file = open('tmp_kms.txt', 'w')
    psc_kms, earliest_time = getKillMails(98469752, output_file)
    output_file.close()
    outputToFile(psc_kms, earliest_time)


    
if __name__ == '__main__':
    main()
    
    pass