import pymongo
import os
import json 
import csv 
import sys, getopt, pprint
import pandas as pd 


def main():
    #get connection
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    
    #create a database called chess
    db = myclient.chess
    
    #create a collection called posts in chess 
    posts = db.posts
    
   
    #open the csv file, NOTE CHANGE THE FILEPATH 
    csvfile = open('xxx')
    reader = csv.DictReader(csvfile)
    header = ["id", "rated", "created_at", "last_move_at", "victory_status", "winner", 
              "increment_code", "white_id", "white_rating", "black_id", "black_rating",
              "moves", "opening_eco", "opening_name", "opening_ply"]
    #insert in all the info into the database
    for each in reader:
        row = {}
        for field in header:
            row[field] = each[field]
        posts.insert_one(row.copy())  
    csvfile.close()
main()
