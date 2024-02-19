from instagrapi import Client
import json
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import time


# Function to fetch data from the firebase store and convert it to a Python dictionary
def fetch_followees_to_set(collection):
  docs = db.collection(collection).get()
  for doc in docs:
    followee_set.add(doc)
  return followee_set


# Function to follow a document_id
def updateDoc(document_id):

  # Get a reference to the document
  doc_ref = db.collection(collection).document(document_id)

  # Get the current date and time
  current_date_time = datetime.now()

  # Convert the current date to a string using the strftime method
  # You can customize the format string as needed
  date_string = current_date_time.strftime("%Y-%m-%d %H:%M:%S")

  # Update the document
  update_data = {
      'followdate': date_string,
  }

  doc_ref.update(update_data)


#==============================================================
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
db.close()
#==============================================================
#######################################################
#follow those users who have not been folllowed
#######################################################
cl = Client()
cl.login("Jmcclain1234", "42163Jmc!@#$")

try:
  cnt = 0
  numToFollow = 5

  for usrDoc in followee_set:

    try:
      docId = usrDoc.id
      usr = usrDoc.to_dict()
      followdate = usr["followdate"]
      unfollowdate = usr["unfollowdate"]
      followee = usr["followee"]

      if (followdate == "" and unfollowdate == "" and cnt < numToFollow):
        cnt = cnt + 1
        followeeInfo = cl.user_info_by_username(followee).model_dump()
        followeeId = followeeInfo["pk"]
        cl.user_follow(followeeId)
        print(f"following: {followee}")
        time.sleep(5)
        updateDoc(docId)

    except Exception as e:
      print(f"Error: Hashtag  not found or access denied: {e}")
except Exception as f:
  print(f"Error: {f}")
finally:
  cl.logout()
