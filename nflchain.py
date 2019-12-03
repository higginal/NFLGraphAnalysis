import requests
import plotly
import plotly.express as px
import pandas as pd

from lxml import html
from bs4 import BeautifulSoup as Soup
import sys
#from soupselect import select

def cmp_to_key(mycmp):
    'Convert a cmp= function into a key= function'
    class K:
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
    return K
#No real use yet
def findLongestPath(adj, n):  
   
    # Dp array  
    #dp = [0] * (n + 1)  
    seq = []
    dp = {}
    # Visited array to know if the node  
    # has been visited previously or not  
    #vis = [False] * (adj[0]) 
    vis = {}
    for i in adj:
        dp[i] = 0
        vis[i] = False
      
    # Call DFS for every unvisited vertex  
    for i in adj:   
        if not vis[i]:  
            dfs(i, adj, dp, vis, seq)  
       
    ans = 0 
    
    print(seq)
    # Traverse and find the maximum of all dp[i]  
    for i in adj:   
        ans = max(ans, dp[i])  
       
    return ans  
#calculates the strength of the team based on the degree of the teams its defeated.
def calculateSOS(team, duplicates=True):

    points = 0
    seenTeams = set()
    for t in graph[team]:
        #print(t)
        #print(len(graph[t[0]]))
        if not duplicates:
            if t[0] not in seenTeams:
                points += len(graph[t[0]])
                seenTeams.add(t[0])
        else:
            if(t[0] in graph):
                points += len(graph[t[0]])
            else:
                points += 0

        
    return points

#comparator for ordering the graph
def cmp_highest_degree(x, y):
    if(calculateSOS(x) > calculateSOS(y)):
        return -1;
    else:
        return 1;
  
#generates graph for weeks 1 - 18 for the given year
def fillGraph(year, graph):

    all_teams = {'Philadelphia Eagles', 'Baltimore Ravens', 'Jacksonville Jaguars','New England Patriots', 'Tampa Bay Buccaneers', 
                'Minnesota Vikings', 'Miami Dolphins', 'Cincinnati Bengals', 'Kansas City Chiefs', 'Carolina Panthers', 'Denver Broncos',
                'Washington Redskins', 'Green Bay Packers', 'New York Jets', 'Los Angeles Rams', 'Los Angeles Chargers', 'Atlanta Falcons',
                'Indianapolis Colts', 'Tennessee Titans', 'New Orleans Saints', 'San Francisco 49ers', 'Dallas Cowboys', 'Chicago Bears',
                'Cleveland Browns', 'Buffalo Bills', 'New York Giants', 'Seattle Seahawks', 'Detroit Lions', 'Pittsburgh Steelers',
                'Houston Texans', 'Oakland Raiders', 'Arizona Cardinals'}
    #print(len(all_teams))

    found_teams = set()

    url = "https://www.pro-football-reference.com/years/" + str(year) + "/week_"

    for x in range (1, 18):
    #print(x)
        scores[x] = requests.get(url + str(x) + ".htm")
        soup = Soup(scores[x].text)

        winners = []

        for game in soup.find_all('div', {'class':'game_summary expanded nohover'}):
            winner = game.find('tr', {'class': 'winner'})
            loser = game.find('tr', {'class': 'loser'})
            if winner != None and loser != None:
                team = winner.find('a').text
                found_teams.add(team)
                if team not in graph:
                    graph[team] = []
                
                graph[team].append((loser.find('a').text, x))
    
    non_winning_teams = all_teams - found_teams
    print(non_winning_teams)
    for x in non_winning_teams:
        graph[x] = []


scores = {}

graph = {}


if(len(sys.argv) < 2):
    print("use 'a' for graph")
    print("use 'b' for years")
    exit()

#parser = HTMLParser()
if(sys.argv[1] == 'b'):
    highestDiff = (0, "", 0, 0)
    lowerBound = int(input("Enter the start year: "))
    upperBound = int(input("Enter the end year: "))

    for x in range(lowerBound, upperBound):
        graph = {}
        fillGraph(x, graph)

        teamNames = [str(x) for x in graph.keys()]
        teamNames = sorted(teamNames, key= cmp_to_key(cmp_highest_degree))
        teamPoints = [calculateSOS(name) for name in teamNames]
        if teamPoints[0] - teamPoints[1] > highestDiff[3]:
            highestDiff = (teamPoints[0], teamNames[0], x, teamPoints[0] - teamPoints[1])


    print("Team with highest difference is the " + str(highestDiff[2]) + " " + str(highestDiff[1]))
    print("with a difference of " + str(highestDiff[3]) + " and " + str(highestDiff[0]) + " points")


if(sys.argv[1] == 'a'):

    year = int(input("Enter year: "))
    fillGraph(year, graph)

    teamNames = [str(x) for x in graph.keys()]
    teamNames = sorted(teamNames, key= cmp_to_key(cmp_highest_degree))
    teamPoints = [calculateSOS(name) for name in teamNames]


    team_data = pd.DataFrame(dict(teams=teamNames, points=teamPoints))

    writer = pd.ExcelWriter('/Users/averyhiggins/Desktop/nfl study/' + str(year) + '.xlsx', engine='xlsxwriter')
    team_data.to_excel(writer, sheet_name='Week13')
    writer.save()

    team_data = team_data.melt(id_vars="teams")

    fig = px.bar(team_data, x="teams", y= "value")

    fig.show()

if(sys.argv[1] == 'c'):
    lowerBound = int(input("Enter the start year: "))
    upperBound = int(input("Enter the end year: "))

    best_teams = dict()

    for x in range(lowerBound, upperBound):
        graph = {}
        fillGraph(x, graph)

        teamNames = [str(x) for x in graph.keys()]
        teamNames = sorted(teamNames, key= cmp_to_key(cmp_highest_degree))
        if teamNames[0] not in best_teams:
            best_teams[teamNames[0]] = 0
        
        best_teams[teamNames[0]] = best_teams[teamNames[0]] + 1

    for x in best_teams:
        print(x + " " + str(best_teams[x]))