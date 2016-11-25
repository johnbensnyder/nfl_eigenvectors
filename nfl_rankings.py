# -*- coding: utf-8 -*-
"""
Created on Thu Nov 24 02:07:04 2016

@author: johnsnyder
"""


from bs4 import BeautifulSoup
import requests
import pandas as pd


def get_results(a_matchup):
    teams = [i.string for i in a_matchup.findAll('span',{'class':'team-name'})]
    scores = [int(i.string) for i in a_matchup.findAll('span',{'class':'team-score'})]
    return [teams, scores]   
    

def get_all_results(some_matchups):
    team_a = []
    team_b = []
    score_a = []
    score_b = []    
    for a_matchup in some_matchups:
        some_results = get_results(a_matchup)
        team_a.append(some_results[0][0])
        team_b.append(some_results[0][1])
        score_a.append(some_results[1][0])
        score_b.append(some_results[1][1])
    return pd.DataFrame({'team_a':team_a,'team_b':team_b,'score_a':score_a,'score_b':score_b})
        

def get_a_page(num):
    url = 'http://www.nfl.com/schedules/2016/REG'+str(num)
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.76 Safari/537.36"
    
    headers = { 'User-Agent' : user_agent }
    response = requests.get(url, headers=headers)
    html = response.text.encode('utf-8')
    soup = BeautifulSoup(html,"lxml")
    
    matchups = soup.findAll('div',{'class':'list-matchup-row-team'})
    return get_all_results(matchups)
    
nfl_df = pd.DataFrame({'team_a':[],'team_b':[],'score_a':[],'score_b':[]})

page = 1 
while True:
    try:
       nfl_df = nfl_df.append(get_a_page(page))
       page+=1
    except:
        break

winning_team = []
lossing_team = []
weight = []
for i,j,k,l in zip(nfl_df['score_a'],nfl_df['score_b'],nfl_df['team_a'],nfl_df['team_b'],):
    if i>j:
        winning_team.append(k)
        lossing_team.append(l)
        weight.append(i-j)
    elif j>i:
        winning_team.append(l)
        lossing_team.append(k)
        weight.append(j-i)

edgelist = pd.DataFrame({'winning_team':winning_team,'lossing_team':lossing_team,'weight':weight,'tie':1})

import networkx as nx

G = nx.DiGraph()

G = nx.from_pandas_dataframe(edgelist,'lossing_team','winning_team','tie',G)

centrality = nx.eigenvector_centrality(G)

rankings = pd.DataFrame({'team':list(centrality.keys()),'eigen':list(centrality.values())}).sort_values('eigen',ascending=False)

rankings['rank'] = [i+1 for i in range(len(rankings))]

print(rankings)

rankings.to_csv('nfl_rankings.csv')
