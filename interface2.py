import pymongo
 

#Get DB connection and the chess collection
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient.chess
posts = db.posts

#global list of opening names
opening_names = []
#global dict of opening counts 
o_counts = {}
#global dict of opening with win/losses
o_win_loss = {}


#Gets the opener with the highest win rate given 'n' amount of games played using it
def findHighestWinrate(n):
    opening_count_dict = o_win_loss.copy()
    mostWinOpening = ""
    mostWinCount = 0

    #loop through openers and their win/loss counts 
    for opening, count in opening_count_dict.items():
        games_played = count["wins"] + count["losses"]
        if(games_played == 0):
            continue
        win_percentage = round((count["wins"]/games_played) * 100,2)

        #keep track of highest win percentage opener
        if(win_percentage > mostWinCount and games_played >= n):
            mostWinCount = win_percentage
            mostWinOpening = opening

    print("-The highest winrate opening, with ", mostWinCount, " win percentage in atleast ",n ," games: ",mostWinOpening)





#Counts the # of times each opening move was used 
def findOpeningUsage(l, h, whitemove):
    #selects all games within the bracket 
    games = {
        "$and" : [
            {"$or": [
                { "$and": [ { "white_rating": { "$lt" : h } },
                        { "white_rating" : { "$gte" : l } },
                        { "white_rating" : { "$exists" : True} } ] },
                { "$and": [ { "black_rating": { "$lt" : h } },
                        { "black_rating" : { "$gte" : l } },
                        { "black_rating" : { "$exists" : True} } ] }
            ]},
            {"moves":{ "$regex" : '^'+whitemove}}
        ]
    }

    result_cursor = posts.find(games)

    #Make a copy of the opening names list
    #Set up a dict to count each type of opening
    opening_count_dict = {}
    opening_names_temp = opening_names.copy()
    
    #sets all openers to 0 
    for opening_name in opening_names_temp:
        opening_count_dict[opening_name] = 0

    #loops through cursos and counts each time opener is used 
    for each in result_cursor:
        trimmed_name = each['opening_name'].split(':')[0].split('|')[0].split('#')[0].rstrip()
        try:
            opening_count_dict[trimmed_name] = 1 + opening_count_dict[trimmed_name]
        except IndexError:
            print("Error in printOpeningUsage(): out of bounds, opening read doesn't match")
    
    #store result in global var
    global o_counts
    o_counts = opening_count_dict.copy() 
    

#gets the total count of all games played within the selected bracket 
def totalCount():
    o_c = o_counts.copy()
    total = 0; 
    for each in o_c.keys():
        total += o_c[each]
    print("total count is ",total)
    return total
    
#Gets the top five most played openings 
def getTopFive():
    #get copy of dict
    opening_count_dict = o_counts.copy()
    topFive = {}
    
    #loop 5 times to get the 5 most played openers 
    while(len(topFive) != 5):
        curName = ""
        curmax = 0
        #find a max
        for each in opening_count_dict.keys():
            if opening_count_dict[each] > curmax:
                curmax = opening_count_dict[each]
                curName = each
                
        #found a max
        topFive[curName] = curmax
        #delete current max from dict
        del opening_count_dict[curName]
    return topFive


#Finds the winrate for every opening move and sets the result to a global dict
def findBlackOpeningWinrate(l, h, whitemove):
    #select all games within the bracket
    games = {
        "$and" : [
            {"$or": [
                { "$and": [ { "white_rating": { "$lt" : h } },
                        { "white_rating" : { "$gte" : l } },
                        { "white_rating" : { "$exists" : True} } ] },
                { "$and": [ { "black_rating": { "$lt" : h } },
                        { "black_rating" : { "$gte" : l } },
                        { "black_rating" : { "$exists" : True} } ] }
            ]},
            {"moves":{ "$regex" : '^'+whitemove}}
        ]
    }

    result_cursor = posts.find(games)

    opening_count_dict = {}
    opening_names_temp = opening_names.copy()
    
    #Creates a dictionary for W/L
    for opening_name in opening_names_temp:
        opening_count_dict[opening_name] = {"wins":0, "losses":0} 

        
    #Add in the wins and losses for each opening name 
    for each in result_cursor:
        trimmed_name = each['opening_name'].split(':')[0].split('|')[0].split('#')[0].rstrip()
        try:
            if(each['winner'] == "black"):
                opening_count_dict[trimmed_name]["wins"] = 1 + opening_count_dict[trimmed_name]["wins"]
            elif(each['winner'] == "white"):
                opening_count_dict[trimmed_name]["losses"] = 1 + opening_count_dict[trimmed_name]["losses"]
        except IndexError:
            print("Error in printOpeningUsage(): out of bounds, opening read doesn't match")
    
    #set global var
    global o_win_loss 
    o_win_loss = opening_count_dict


   
    
#get the top 5 most used openings win percentages        
def getTopFivePercentages(topFive):
    #get copies of opening names and o_win_loss global vars
    opening_names_temp = opening_names.copy()
    opening_count_dict = o_win_loss.copy() 
    
    #append win rates to the top five most used openers
    for each in topFive:
        games_played = opening_count_dict[each]["wins"] + opening_count_dict[each]["losses"]
        win_percentage = round((opening_count_dict[each]["wins"]/games_played) * 100,2)
        topFive[each] = [topFive[each], win_percentage] 

    return topFive



#Sets the opening moves list in the global var and removes all variations 
def setOpeningName():
    result = posts.find()

    #Get 143 openings by removing variations 
    for each in result:
        #removes all variations 
        name = each['opening_name'].split(':')[0].split('|')[0].split('#')[0].rstrip()
        if(name not in opening_names):
            opening_names.append(name)
    # sort list of names
    opening_names.sort()
    
    
    
    
#Sets user inputs for the interface
def getInputs():
    white_move = input("Enter in white player's move> ")
    lower_bound = int(input("Enter in lower rating bound> "))
    upper_bound = int(input("Enter in upper rating bound> "))
    return [white_move,lower_bound,upper_bound]
    
def main():
    setOpeningName() #query called by default
    white_move, lower_bound, upper_bound = getInputs() 
    
    user_input = ""
    while(user_input != "quit"):
        findOpeningUsage(lower_bound,upper_bound,white_move)
        findBlackOpeningWinrate(lower_bound,upper_bound,white_move)
        
        print("\nQuerying for move: ",white_move," and rating bounds [",lower_bound,",",upper_bound,"]")
        print("Enter desired query. Type 'quit' to quit.")
        print("1: See total # of games in bracket")
        print("2: See top five most used moves")
        print("3: Find number of upsets, Find number of rating consistent wins.")
        print("4: Enter in new bracket and move")
        print("Enter 'quit' to exit")
        user_input = input("> ")
        print("\n")
        
        if(user_input == "1"):
            print("Total games in bracket")
            print(totalCount())
        elif(user_input == "2"):
            print("Top 5 most used openers")
            print(getTopFive())
        elif(user_input == "3"):
            print("Top 5 most used openers with their counts and win rates")
            print(getTopFivePercentages(getTopFive()));
        elif(user_input == "4"):
            white_move, lower_bound, upper_bound = getInputs()
main()