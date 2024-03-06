from riotwatcher import LolWatcher, ApiError
from urllib.request import urlretrieve
import os


def getGameName(discord_username):

    users = {
    'Theeight':                    {'name': 'Theeightc',           'region': 'EUW1'},
    'ladymorgie':                  {'name': 'Lady Morgie',         'region': 'EUW1'},
    'AGRIS':                       {'name': 'YOU GUYS ARE BAD',    'region': 'EUW1'},
    'ifchix':                      {'name': 'botinjsh',            'region': 'EUW1'},
    'MitraisBandīts':              {'name': 'Kapars420',           'region': 'EUW1'},
    'Warksman':                    {'name': '4dren4linRush',       'region': 'EUW1'},
    'kampulis':                    {'name': 'BoneLord69',          'region': 'EUW1'},
    'MissGoldfish':                {'name': 'MissGoldfish',        'region': 'EUW1'},
    'Karma':                       {'name': 'That Karma',          'region': 'EUW1'},
    'Eternal Wanderer':            {'name': 'Binoklis',            'region': 'EUW1'},
    'gesmen':                      {'name': 'gesmenits',           'region': 'EUW1'},
    'EddyThe3agle':                {'name': 'JustifyEA',           'region': 'EUW1'},
    'FatAndBeautiful':             {'name': 'Proctologist',        'region': 'EUW1'},
    'Rodzs/Mini':                  {'name': 'Rodzs',               'region': 'EUW1'},
    'WhiteCave':                   {'name': 'WhiteCave',           'region': 'EUW1'},
    'notacop':                     {'name': 'Erronnannet',         'region': 'EUW1'},
    'Shabba':                      {'name': 'JZX Shabba',          'region': 'EUN1'},
    'eidukS':                      {'name': 'eidukxx',             'region': 'EUN1'},
    'Antidisestablishmentaria':    {'name': 'deporteetaa Dora',    'region': 'EUW1'},
    'Legendary Citronskeys':       {'name': 'Citronskeys',         'region': 'EUW1'},
    'b1bop':                       {'name': 'b1bop',               'region': 'EUW1'},
    'goofinjsh':                   {'name': 'Goofinjsh',           'region': 'EUW1'},
    'Lv_Chigorins':                {'name': 'Lvchigorins',         'region': 'EUW1'},
    'vitaminz88':                  {'name': 'vitaminz88',          'region': 'EUW1'},
    'Milkyu':                      {'name': 'Milkyu',              'region': 'EUW1'},
    'mr.fr3aky':                   {'name': 'Mr Fr3aky',           'region': 'EUW1'},
    'gunchiks':                    {'name': 'Gunchiks',            'region': 'EUW1'},
    'Sleeplessness':               {'name': 'Sleeplessness',       'region': 'EUW1'},
    'Jaanisjc':                    {'name': 'YOU GUYS ARE BAD',    'region': 'EUW1'},
    'Cucumburgers':                {'name': 'GD DomesticAbuse',    'region': 'EUW1'},
    'musty122':                    {'name': 'eidukxx',             'region': 'EUN1'},
    'dimonius':                    {'name': 'DJ NiknaiS PapS',     'region': 'EUW1'},
    'haskijs':                     {'name': 'Haskijs',             'region': 'EUW1'}
 }
    
    user = users.get(discord_username)
    if user is None:
        return None, None
  
    return user['name'], user['region']



def getImage(champ_N, champ_da):
    champ_name = champ_N
    champion_data = champ_da
    
    if not os.path.exists("images_LoL"):
        os.mkdir("images_LoL")

    file_name = os.path.join("images_LoL", f"{champ_name}.png")
    if os.path.exists(file_name):
        print(f"Champion picture already exists at {file_name}")
    else:
        url = f"http://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champion_data['id']}_0.jpg"
        file_name = os.path.join("images_LoL", f"{champ_name}.png")
        urlretrieve(url, file_name)

def getStats(user_id):

   api_key = os.getenv('LOL')
   watcher = LolWatcher(api_key)

    # retrieve data about a summoner
   summoner_name, region = getGameName(user_id) #@#
   if summoner_name is None: #@#
        return None, None #@#
   try:
    summoner = watcher.summoner.by_name(region, summoner_name)

    #print(summoner)

    # retrieve the summoner's match history
    match_history = watcher.match.matchlist_by_puuid(region, summoner['puuid'])

    # retrieve the most recent match from the match history
    match_id = match_history[0]
    match = watcher.match.by_id(region, match_id)
    participant = None
    for p in match['info']['participants']:
        if p['summonerId'] == summoner['id']:
         participant = p
         break

  # find the participant corresponding to the summoner
    participant_id = None
    for participant in match['info']['participants']:
        if participant['summonerName'] == summoner_name:
            participant_id = participant['participantId']
            break
    
    if participant_id is None:
        print(f"Error: could not find participant matching summoner name {summoner_name}")
        return None, None
    else:
        # extract the number of kills for the participant
        for participant_stats in match['info']['participants']:
            if participant_stats['participantId'] == participant_id:
                num_kills = participant_stats['kills']
                break
    champ_name = participant['championName']

    

    # Get the list of all champions
    champions = watcher.data_dragon.champions("10.22.1")["data"]
    
    # Loop through the list of champions and find the one with the matching name
    for champion_id, champion_data in champions.items():
        if champion_data["name"] == champ_name:
            # Found the matching champion, get its title
            champion_title = champion_data["title"]
            print(champion_title)
            break
        else: champion_title = None
    
    if champion_title is not None:
        champ_name = champ_name + ", " + champion_title
    getImage(champ_name, champion_data)
    
    # Loop through the player's recent matches and check if they won with the specified champion
   # for match in matchlist["matches"]:
    #    if match["champion"] == champion["id"] and match["win"]:
    #        # Retrieve information on the champion's abilities
    #        abilities = "\n".join([f"{ability['name']}: {ability['description']}" for ability in champion["spells"]])
            # Print a tailored congratulations message for the player, including information on the champion's abilities
     #       print(f"Congratulations, {summoner_name}! You won a game with {champion['name']} ({champion['title']}).\n\n{abilities}")
    return champ_name , num_kills

   except ApiError as e:
    print(f"Error: {e}")
    return None, None

   