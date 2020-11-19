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





'''
    Finds the winrate of each opening, from the black player's perspective.

    Needs setOpeningName() to be run first.
'''
def findBlackOpeningWinrate(l, h, whitemove, end = ""):
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
    for opening_name in opening_names_temp:
        opening_count_dict[opening_name] = {"wins":0, "losses":0} #Creates a dictionary for W/L

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
    o_win_loss = opening_count_dict.copy()
    if(end != ""):  #used to solely declare the global var (avoids prints)
        return

    print("-[",l,",",h,"] WINRATE OF EACH (",whitemove," move) OPENING:\n--")
    for each in opening_names_temp:
        if opening_count_dict[each]["wins"] == 0 and opening_count_dict[each]["losses"] == 0:
            continue
        games_played = opening_count_dict[each]["wins"] + opening_count_dict[each]["losses"]
        win_percentage = round((opening_count_dict[each]["wins"]/games_played) * 100,2)
        print(" ", each, ": ", opening_count_dict[each]["wins"],"/", opening_count_dict[each]["losses"],"\n     ",win_percentage,"% of ", games_played, " games.")
    print("------------------------")

    return opening_count_dict






'''
    Prints the highest winrate openings, given min of n games played.
    Takes a dict with the W/L of each opening,
    So must be used in combination with findBlackOpeningWinrateE4().

    Needs setOpeningName() to be run first.
'''

def findHighestWinrate(opening_count_dict, n):

    mostWinOpening = ""
    mostWinCount = 0

    for opening, count in opening_count_dict.items():
        games_played = count["wins"] + count["losses"]
        if(games_played == 0):
            continue
        win_percentage = round((count["wins"]/games_played) * 100,2)

        if(win_percentage > mostWinCount and games_played >= n):
            mostWinCount = win_percentage
            mostWinOpening = opening


    print("-The highest winrate opening, with ", mostWinCount, " win percentage in atleast ",n ," games:")
    print("--")
    print(" ",mostWinOpening)
    print("------------------------")






'''
    Prints the total number of openings used in the bracket of l to h.
    Returns a dictionary containing the counts.

    Needs setOpeningName() to be run first.
'''
def findOpeningUsage(l, h, whitemove, end = ""):

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
    for opening_name in opening_names_temp:
        opening_count_dict[opening_name] = 0

    for each in result_cursor:
        trimmed_name = each['opening_name'].split(':')[0].split('|')[0].split('#')[0].rstrip()
        try:
            opening_count_dict[trimmed_name] = 1 + opening_count_dict[trimmed_name]
        except IndexError:
            print("Error in printOpeningUsage(): out of bounds, opening read doesn't match")
            
    #store result in global var
    global o_counts
    o_counts = opening_count_dict.copy() 
    if(end != ""):
        return 

    print("-[",l,",",h,"] COUNTS OF EACH OPENING (",whitemove," first move):\n--")
    for each in opening_names_temp:
        if opening_count_dict[each] == 0:
            continue
        print(" ", each, ": ", opening_count_dict[each])
    print("------------------------")
    return opening_count_dict







'''
    Prints the least and most used openings.
    Takes a dict with the counts of each opening,
    So must be used in combination with findOpeningUsage().

    Needs setOpeningName() to be run first.
'''

def findPopularOpening(opening_count_dict):
    #opening is key, count is value
    mostPopularOpeningList = []
    mostPopularCount = 0

    for opening, count in opening_count_dict.items():
        if(count > mostPopularCount):
            mostPopularCount = count
            mostPopularOpeningList.clear()
            mostPopularOpeningList.append(opening)
        elif(count == mostPopularCount):
            mostPopularOpeningList.append(opening)

    print("-The most popular opening(s), with ", mostPopularCount, " uses:")
    print("--")
    for opening in mostPopularOpeningList:
        print(" ",opening)
    print("------------------------")

    leastPopularOpeningList = []
    leastPopularCount = 99999

    for opening, count in opening_count_dict.items():
        if(count < leastPopularCount and count != 0):
            leastPopularCount = count
            leastPopularOpeningList.clear()
            leastPopularOpeningList.append(opening)
        elif(count == leastPopularCount):
            leastPopularOpeningList.append(opening)

    print("-The least popular opening(s) (non-zero uses), with ", leastPopularCount, " use(s):")
    print("--")
    for opening in leastPopularOpeningList:
        print(" ",opening)
    print("------------------------")






'''
    Prints the total lower rated and higher rated wins
'''
def printRatingResults(l, h, move):
    #Get all games using move "x" in bracket [l,h)
    games = {
        "$and": [{
            "$or": [
                { "$and": [ { "white_rating": { "$lt" : h } },
                        { "white_rating" : { "$gte" : l } },
                        { "white_rating" : { "$exists" : True} } ] },
                { "$and": [ { "black_rating": { "$lt" : h } },
                        { "black_rating" : { "$gte" : l } },
                        { "black_rating" : { "$exists" : True} } ] }
            ]},
            { "moves": { "$regex": '^'+move} }
        ]
    }

    result_cursor = posts.find(games)
    
    #vars 
    lowerRatedWin = 0
    higherRatedWin = 0
    draw = 0

    #Keep track of upsets and rating consistent games
    for each in result_cursor:
        if (each["white_rating"] > each["black_rating"]) and (each['winner'] == "white"):
            higherRatedWin+=1
        elif (each["white_rating"] > each["black_rating"]) and (each['winner'] == "black"):
            lowerRatedWin+=1
        elif (each["black_rating"] > each["white_rating"]) and (each['winner'] == "black"):
            higherRatedWin+=1
        elif (each["black_rating"] > each["white_rating"]) and (each['winner'] == "white"):
            lowerRatedWin+=1
        else:
            draw+=1

    #print results 
    print("hrw: " ,higherRatedWin, " lrw: ", lowerRatedWin, " draws: ", draw)







'''
    Gets the top five most used openers in the bracket 
'''
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






'''
   get the top 5 most used openings win percentage along with their counts in dict
'''     
def getTopFivePercentages(topFive):
    #get copies of o_win_loss global vars
    opening_count_dict = o_win_loss.copy() 
    
    #append win rates to the top five most used openers
    for each in topFive:
        games_played = opening_count_dict[each]["wins"] + opening_count_dict[each]["losses"]
        win_percentage = round((opening_count_dict[each]["wins"]/games_played) * 100,2)
        topFive[each] = [topFive[each], win_percentage] 

    return topFive



'''
gets the total count of all games played within the selected bracket 
'''
def totalCount():
    o_c = o_counts.copy()
    total = 0; 
    for each in o_c.keys():
        total += o_c[each]
    print("total count is ",total)




'''
    Sets the global list opening_names to all 143 possible moves (according
    to this dataset with variations removed)

    NOTE*
    -a copy of the global list opening_names is used in other functions 
'''
def setOpeningName():
    result = posts.find()

    #Get 143 openings by removing variations 
    for each in result:
        name = each['opening_name'].split(':')[0].split('|')[0].split('#')[0].rstrip()
        if(name not in opening_names):
            opening_names.append(name)
    
    print(len(opening_names), " distinct openings.")
    # sort list of names
    opening_names.sort()







'''
    Sets user inputs for the interface
'''
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
        print("\nQuerying for move: ",white_move," and rating bounds [",lower_bound,",",upper_bound,"]")
        print("Enter desired query. Type 'quit' to quit.")
        print("1: Find opening usage, find least popular, find most popular.")
        print("2: Find opening winrate, find highest winrate.")
        print("3: Find number of upsets, Find number of rating consistent wins.")
        print("4: See total # of games in bracket")
        print("5: See top five most used moves with counts and win rates")
        print("6: Enter in new bracket and initial move")
        print("Enter in 'quit' to exit")
        
        user_input = input("> ")
        print("\n")

        if(user_input == "1"):
            count = findOpeningUsage(lower_bound, upper_bound, white_move)
            findPopularOpening(count)
        elif(user_input == "2"):
            min_games = int(input("Enter a minimum numper of games played> "))
            winrate_counts = findBlackOpeningWinrate(lower_bound, upper_bound, white_move)
            findHighestWinrate(winrate_counts,min_games)
        elif(user_input == "3"):
            printRatingResults(lower_bound, upper_bound, white_move)
        elif(user_input == "4"):
            findOpeningUsage(lower_bound, upper_bound, white_move, "zzz")
            print("Total games in bracket")
            print(totalCount())
        elif(user_input == "5"):
            findOpeningUsage(lower_bound, upper_bound, white_move, "zzz")
            findBlackOpeningWinrate(lower_bound, upper_bound, white_move, "zzz")
            print("Top 5 most used openers with their counts and win rates")
            print(getTopFivePercentages(getTopFive()));
        elif(user_input == "6"):
            white_move, lower_bound, upper_bound = getInputs() 

        print("____________________________________________\n\n")

main()
