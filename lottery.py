from __future__ import print_function
import httplib2
import os
import numpy as np 

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from random import *

SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'West House Lottery'


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    normal_canidate = [] #applicant without a special weighting rule
    prob = np.empty(0, dtype= "f")
    priority_weightlist = [] #applicants with special rules who didn't get chosen

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1bBlOIAcssCXsiibNXK2h4s7sk_-wdRzDS4EukNaHakc'
    rangeName = 'FOR LOTTERY!B2:C'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print("Winners:\n")
        total = 8
        for row in values:
            if not len(row): #we have reached the end of the candiate data
                break
            if int(row[0]) == 20:
                x = randint(0,1)
                if x == 0:
                    print(row[1])
                    total-=1
                else:
                    priority_weightlist.append(row[1])
            else: #generate list of non-special canidates and associated weigths
                if int(row[0]) == 4:
                    normal_canidate.insert(0, row[1])
                    prob = np.insert(prob, 0, 4)
                elif int(row[0]) == 5:
                    normal_canidate.insert(0, row[1])
                    prob = np.insert(prob, 0, 5)
                else:
                    print("invalid weight on", row[1])
        prob = prob/sum(prob)
        second_prob = np.random.choice(normal_canidate, total, replace=False, p=prob)
        for lucky_winner in second_prob:
            print(lucky_winner)
        print("\nWeight List:")
        shuffle(priority_weightlist)
        for priority_weightlisted in priority_weightlist:
            print(priority_weightlisted)
        shuffle(normal_canidate)
        normal_canidate = [person for person in normal_canidate if person not in lucky_winner]
        for weight_listed in normal_canidate:
            print(weight_listed)
if __name__ == '__main__':
    main()
