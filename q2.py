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
    Prints the total number of openings used in the bracket of l to h.
    Returns a dictionary containing the counts.
    Calls setOpeningName()
'''
def findOpeningUsage(l, h):
    setOpeningName()
    games = {
        "$or": [
            { "$and": [ { "white_rating": { "$lt" : h } },
                    { "white_rating" : { "$gte" : l } },
                    { "white_rating" : { "$exists" : True} } ] },
            { "$and": [ { "black_rating": { "$lt" : h } },
                    { "black_rating" : { "$gte" : l } },
                    { "black_rating" : { "$exists" : True} } ] }
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

    print("-COUNTS OF EACH OPENING:\n--")
    for each in opening_names_temp:
        if opening_count_dict[each] == 0:
            continue
        print(" ", each, ": ", opening_count_dict[each])
    print("------------------------")
    return opening_count_dict



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
    count = findOpeningUsage(800,1100)
    findPopularOpening(count)
main()
