from datetime import datetime
import os
import pymongo
from dotenv import load_dotenv

load_dotenv()


class MongoDB:

    def __init__(self, collection):
        print("Creating MongoDB client")
        client = pymongo.MongoClient(os.getenv("MONGO_URI"))
        if client:
            print("Connected to DB")
        else:
            print("Not Connected to DB")
        self.collection = client.spookystories[collection]

    def delete_collection(self):
        self.collection.drop()

    def insert(self, story) -> None:
        try:
            resp = self.collection.insert_one(story)
        except pymongo.errors.DuplicateKeyError:
            print("Story already in data_storage")
            return False
        else:
            if resp.acknowledged and resp.inserted_id:
                print(f"inserted story successfully")
                return True
            else:
                print("Did not insert story successfully")
                return False

    def get(self, story_id):
        story = self.collection.find_one({"_id": story_id})
        if story:
            print(f"reddit id: {story_id} is in the table")
        else:
            print(f"Reddit_id is not in the table")
        return story

    def update(self, story_id, query):
        resp = self.collection.update_one({"_id": story_id}, query)
        if resp.acknowledged and resp.matched_count:
            return True
            print(f"Successfully updated story with id: {story_id}")
        else:
            return False
            print(f"Did not update story with id: {story_id}")

    def get_series_id(self, add_to_front=False) -> int:
        if add_to_front:
            self.shift_series_ids()
            return 0

        find_result = self.collection.find_one(
            sort=[("series_id", pymongo.DESCENDING)]
        )
        if not find_result:
            return 0
        return find_result["series_id"] + 1

    def shift_series_ids(self) -> None:
        update_result = self.collection.update_many(
            {}, {"$inc": {"series_id": 1}}
        )
        if update_result.acknowledged:
            print(f"successfully incremented all series ids")
        else:
            print("did not successfully incremented all series ids")

    def highest_priority_tts(self, reddit_id=None):
        # get story with the lowest series_id and series_part where audio hasn't
        # been generated
        # if specific reddit id is provided, generate that one
        if reddit_id:
            story = self.get(reddit_id)
            if not story["audio_generated"] and not story["processing_audio"]:
                return story["_id"], story["tts_text"]
            else:
                print("Story has been processed or is being processed")
                return None, None
        try:
            story_list = self.collection.find(
                {"upload_date": None}).sort(
                [
                    ("series_id", pymongo.ASCENDING),
                    ("series_part", pymongo.ASCENDING),
                ]
            )
            return story_list[0]["_id"], story_list[0]["tts_text"], story_list[0]["voice"]
        except IndexError as e:
            print("All stories have audio audio generated")
            print(e)
            pass
        return None, None, None

    def highest_priority_video(self, reddit_id=None):
        # get story with the lowest series_id and series_part where audio has
        # been generated
        # if specific reddit id is provided, generate that one
        if reddit_id:
            story = self.get(reddit_id)
            if not story["audio_generated"] and not story["processing_audio"]:
                return story["_id"], story["tts_text"]
            else:
                print("Story has been processed or is being processed")
                return None, None
        try:
            story_list = self.collection.find(
                {"upload_date": None}).sort(
                [
                    ("series_id", pymongo.ASCENDING),
                    ("series_part", pymongo.ASCENDING),
                ]
            )
            return story_list[0]
        except IndexError as e:
            print("All stories have audio audio generated")
            print(e)
            pass
        return None

    def audio_generated(self, story_id):
        return self.update(story_id, {"$set": {"audio_generated": True}})

    def start_processing_audio(self, story_id):
        return self.update(story_id, {"$set": {"processing_audio": True}})

    def stop_processing_audio(self, story_id):
        return self.update(story_id, {"$set": {"processing_audio": False}})

    def uploaded(self, story_id):
        return self.update(story_id, {"$set": {"uploaded": True}})

    def update_playlist(self, story_id, playlist_id):
        return self.update(story_id, {"$set": {"playlist_id": playlist_id}})
