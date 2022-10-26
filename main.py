import requests
import csv
import networkx as nx
import time


token = "vk1.a.rc5b6XeC04nvu8QJ-41A9Bd3H80uYuTiXwdFZ--UTE1_05iD4Exy-eNVjdjBBTy_Hxv4ptoNfPk4R7TcVXM-bDtetR5CxfIsEa3NfTziwfvBj6q2fpSzeFYWMXMinJnZOzEYVe6fxF0zDA5-VjvDT37HDYn88l0i3iIeTnb8DxejrbO2TmLakDBFeMcGIjFXNubgdaXEtRXDOjSbWxGraw"
version = 5.131


# Get data from a database and convert it to a list
def processing_cvs(DataBaseName):
    with open(DataBaseName, newline='') as csvfile:
        dataBase = list(csv.DictReader(csvfile, delimiter=';'))
    return dataBase


# Convert short names to ids
def convert_person_id(dataBase):
    idList = ''
    for row in dataBase:
        idList = idList + row['ID'] + ','
    request = requests.get('https://api.vk.com/method/users.get', params = {
            'access_token': token,
            'user_ids': idList,
            'v': version
        })
    for item, row in enumerate(dataBase):
        row['ID'] = request.json()['response'][item]['id']
    return dataBase


# Get each user's friends
def search_friends(dataBase):
    for row in dataBase:
        r = requests.get('https://api.vk.com/method/friends.get', params = {
            'access_token': token,
            'user_id': row['ID'],
            'v': version
        })
        row['friends'] = r.json()['response']['items']
        time.sleep(0.3)
    return dataBase


# Check for friendships between users, delete users without connections
def check_friendship(dataBase):
    relationsList = []
    for item, row in enumerate(dataBase):
        friendsCounter = 0
        for item2, row2 in enumerate(dataBase):
            for id in row2['friends']:
                if row['ID'] == id:
                    relationsList.append((item, item2))
                    friendsCounter = friendsCounter + 1
        if friendsCounter == 0:
            dataBase.pop(item)
    return relationsList, dataBase


# Create a user graph
def graph_formation(dataBase, relationList):
    G = nx.Graph()
    for item, row in enumerate(dataBase):
        G.add_node(item)
    G.add_edges_from(relationList)
    return(G)


# Find the most central user by betweennes
def betweenness_centrality(G, dataBase):
    centralityDict = nx.betweenness_centrality(G)
    v, k = max((v, k) for k, v in centralityDict.items())
    print('По посредничеству: ', dataBase[k]['ФИО'])


# Find the most central user by closeness
def closeness_centrality(G,dataBase):
    centralityDict = nx.closeness_centrality(G, wf_improved = False )
    v, k = min((v, k) for k, v in centralityDict.items())
    print('По близости: ', dataBase[k]['ФИО'])


# Find the most central user by eigenvector
def eigenvector_centrality(G, dataBase):
    centralityDict = nx.eigenvector_centrality(G)
    v, k = max((v, k) for k, v in centralityDict.items())
    print('По собственному вектору: ', dataBase[k]['ФИО'])


dataBase = processing_cvs('vk_database.csv')
conversionDataBase = convert_person_id(dataBase)
dataBaseWithFriends = search_friends(conversionDataBase)
relationList, clearDataBase = check_friendship(dataBaseWithFriends)
G = graph_formation(clearDataBase, relationList)
betweenness_centrality(G, clearDataBase)
closeness_centrality(G, clearDataBase)
eigenvector_centrality(G, clearDataBase)
