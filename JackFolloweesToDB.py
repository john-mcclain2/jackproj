import instaloader
from instagrapi import Client
from instaloader import Hashtag, Profile
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime


#######################################################
#sign into firebase, create crud methods, initialize the set of current followees
#######################################################
# Function to create a document in the firebase store
def create_document(collection, document_data):
  print("in create_document")
  doc_ref = db.collection(collection).add(document_data)
  print("Document created with ID:", doc_ref[1].id)


# Function to fetch data from the firebase store and convert it to a Python dictionary
def fetch_followees_to_set(collection):
  print("in fetch_followees_to_set")
  docs = db.collection(collection).get()
  for doc in docs:
    followee_set.add(doc.to_dict()["followee"])
  return followee_set


# Initialize Firebase with your credentials and get a reference
cred = credentials.Certificate(
    "jackproj-a9250-firebase-adminsdk-xiiqt-9ee4eafaf5.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

#create set of current followees from the firebase db
#collection = "jackproj-a9250"
collection = "jackproj-1"

followee_set = set()
fetch_followees_to_set(collection)

#######################################################
#get Jack static vars via instaloader
#######################################################
USERNAME = "jack_mcclain"

jackFollowList = []

L = instaloader.Instaloader()
#L.login("johnmcclain497", "42163Jmc@")
L.login("Jmcclain1234", "42163Jmc!@#$")

profile = Profile.from_username(L.context, USERNAME)

for follower in profile.get_followers():
  jackFollowList.append(follower.username)
jackNumFollowers = len(jackFollowList)

#######################################################
#process instagram data into firebase via instagrapi
#######################################################
#list of tags to search
hashtagList = [
    'gym', 'fitness', 'fit', 'workout', 'weightlifting', 'pickleball'
]
hashtagList.append('athlete')

numPostsPerTag = 10
#login to instagram and get posts having those tags above
#from those posts, get their users
#but only get users if they have > 1 tag in their listing of posts
#put the users in that list to a firebase database
cl = Client()
cl.login("Jmcclain1234", "42163Jmc!@#$")

#map of users to their posts having tags above, for those users that are already not in
#the database, and if the post is not tagged with an already used tag
#i.E., create {<user1> : (post1 having any tag[1-6], post2 having any tag[1-6] that is
#not in post1)),..., <userx> : (post1 having any tag[1-6], post2 having any tag[1-6]
#that is not in post1)),...},
userTagMap = {}
try:
  for tag in hashtagList:
    lst = cl.hashtag_medias_top(tag, amount=numPostsPerTag)
    for post in lst:
      postUser = post.user.username
      print(f"checking: {postUser}")
      if (postUser not in followee_set):
        if (postUser not in userTagMap):
          postSet = set()
          postSet.add("https://www.instagram.com/p/" + post.code + "," + tag)
          userTagMap[postUser] = postSet
        else:
          not_contained_tag = all(tag not in postUrlAndTag for postUrlAndTag in userTagMap[postUser])
          #tagPost = "https://www.instagram.com/p/" + post.code
          #not_contained_post = all(tagPost not in postUrlAndTag
          #for postUrlAndTag in userTagMap[postUser])
          #if (not_contained_tag and not_contained_post):
          if (not_contained_tag):
            postSet = userTagMap[postUser]
            postSet.add("https://www.instagram.com/p/" + post.code + "," + tag)
            userTagMap[postUser] = postSet

  #ensure that map of users to their posts ONLY contains users who have > 1 post
  #(i.e. > 1 tag) in their post listings
  filtered_userTagMap = {
      key: value
      for key, value in userTagMap.items() if len(value) > 1
  }

  #for each user in the filtered_userTagMap, create a document in the firebase database
  #holding the followee and the list of posts having >= 1 of the tags
  #for key, value in filtered_userTagMap.items():
  for key, value in userTagMap.items():
    document_data = {
        "followdate": "",
        "followee": key,
        "unfollowdate": "",
        "postList": value
    }
    create_document(collection, document_data)

except Exception as e:
  print(f"Error: Hashtag  not found or access denied: {e}")
finally:
  cl.logout()
  db.close()
