import pymongo
import os
import json 
import csv 
import sys, getopt, pprint
import pandas as pd 
from pprint import pprint

#Get DB connection and the chess collection
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient.chess
posts = db.posts

#global list of opening names 
opening_names = []


'''
    Prints the total lower rated and higher rated wins 
    Calls printWins() 
'''
def printTotals(l, h):
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
    printWins(l,h)
    
    
    
    
    
'''
    Prints the wins due to each opening move 
    Calls setOpeningMove()
'''
def printWins(l, h):
    setOpeningName()
    openingListCopy = opening_names.copy()
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
    
    #Get the counts of each of the 143 openings 
    nameCounts = [0 for x in range(len(opening_names))]
    for each in result_cursor:
        name = each['opening_name'].split(':')[0].split('|')[0].split('#')[0].rstrip()
        if(name in openingListCopy):
            ind = openingListCopy.index(name)
            nameCounts[ind] = nameCounts[ind] + 1
    
    print(len(openingListCopy), " ", len(nameCounts))
    #remove the opening_moves with 0 counts 
    for i in range(len(nameCounts)):
        if nameCounts[i] == 0:
            openingListCopy[i] ='rm'
    newOpening= [i for i in openingListCopy if i != 'rm']
    newCounts = [i for i in nameCounts if i != 0]
    
    #print the names with coresponding counts 
    for i in range(len(newCounts)):
        print("name: ", newOpening[i], " COUNT: ", newCounts[i])
            
    
    
    
    
    
    
    
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
    print(len(opening_names))
    opening_names.sort()
    
    
    
    
    
    
    

def main():
    #print bracket 
    printTotals(800,1100)
main()