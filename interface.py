import pymongo
import os
import json
import csv
import sys, getopt, pprint
from pprint import pprint

#Get DB connection and the chess collection
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient.chess
posts = db.posts

#global list of opening names
opening_names = []


'''
    Finds the winrate of each opening, from the black player's perspective.

    Needs setOpeningName() to be run first.
'''
def findBlackOpeningWinrate(l, h, whitemove):
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

        #print(opening_count_dict)

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


    print("-The highest winrate opening, with ", mostWinCount, " win percentage in atleast ",n ," moves:")
    print("--")
    print(" ",mostWinOpening)
    print("------------------------")

    return

'''
    Prints the total number of openings used in the bracket of l to h.
    Returns a dictionary containing the counts.

    Needs setOpeningName() to be run first.
'''
def findOpeningUsage(l, h, whitemove):

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
    lowerRatedWin = 0
    higherRatedWin = 0
    draw = 0

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


    print("hrw: " ,higherRatedWin, " lrw: ", lowerRatedWin, " draws: ", draw)


'''
    Sets the global list opening_names to all 143 possible moves (according
    to this dataset with variations removed)

    NOTE*
    -when the global list is used in a function, a copy is made
    -Creation of opening names list must be made into a separate function
        to reduce redundancy in the case in which users make multiple calls
        to printTotals()
'''
def setOpeningName():
    result = posts.find()

    #Get 143 openings
    for each in result:
        name = each['opening_name'].split(':')[0].split('|')[0].split('#')[0].rstrip()
        if(name not in opening_names):
            opening_names.append(name)
    print(len(opening_names), " distinct openings.")
    opening_names.sort()








def main():
    setOpeningName() #query called by default
    white_move = input("Enter in white player's move> ")
    lower_bound = int(input("Enter in lower rating bound> "))
    upper_bound = int(input("Enter in upper rating bound> "))

    user_input = ""
    while(user_input != "quit"):
        print("\nQuerying for move: ",white_move," and rating bounds [",lower_bound,",",upper_bound,"]")
        print("Enter desired query. Type 'quit' to quit.")
        print("1: Find opening usage, find least popular, find most popular.")
        print("2: Find opening winrate, find highest winrate.")
        print("3: Find number of upsets, Find number of rating consistent wins.")
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

        print("____________________________________________\n\n")


    '''
        count = findOpeningUsage(800,1100, 'd4')
        findPopularOpening(count)

        winrate_counts = findBlackOpeningWinrate(800,1100,'d4')
        findHighestWinrate(winrate_counts,10)

        printRatingResults(800,1100,'d4')
    '''
main()
