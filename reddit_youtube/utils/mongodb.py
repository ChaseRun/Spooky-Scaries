from datetime import datetime
import os
import pymongo
import toml

AUDIO_GENERATED = {"$set": {"audio_generated": True}}
VIDEO_GENERATED = {"$set": {"video_generated": True}}
POSTED = {"$set": {"posted": True, "posted_date": datetime.utcnow()}}
START_AUDIO_GENERATION = {"$set": {"processing_audio": True}}
START_VIDEO_GENERATION = {"$set": {"processing_video": True}}
STOP_AUDIO_GENERATION = {"$set": {"processing_audio": False}}
STOP_VIDEO_GENERATION = {"$set": {"processing_video": False}}


class MongoDB:
    def __init__(self, collection):
        print("Creating MongoDB client")
        cwd = os.path.dirname(os.path.abspath(__file__))
        config_file = f"{cwd}/../config/config.toml"
        config = toml.load(config_file)["MONGO_DB"]
        client = pymongo.MongoClient(config["URI"])
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

    # TODO: Fire generate video script?
    # TODO: Fire youtube upload?
    # TODO: Lambda function on spot instance termination?
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
                {"audio_generated": False, "processing_audio": False}
            ).sort(
                [
                    ("series_id", pymongo.ASCENDING),
                    ("series_part", pymongo.ASCENDING),
                ]
            )
            return story_list[0]["_id"], story_list[0]["tts_text"]
        except IndexError as e:
            print("All stories have tts audio generated")
            print(e)
            pass
        return None, None
