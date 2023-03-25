import os
from utils.runtime import print_runtime
from utils.db import MongoDB
from utils.video_assets import create_screenshots, create_video


@print_runtime
def generate_video():
    s3, mongo_db = S3(), MongoDB("story")

    # get relevant story
    story = MongoDB.highest_priority_video()
    story_id = story["_id"]
    num_audio_clips = len(story["tts_text"])

    # get audio files
    s3.download_story_audio(story_id, num_audio_clips)

    # make screenshots
    create_screenshots(story, story_id, story["reddit_id"])

    # create video
    create_video(story_id, num_audio_clips)

    # upload to youtube


    # mark as uploaded in db

if __name__ == "__main__":
    generate_video()
