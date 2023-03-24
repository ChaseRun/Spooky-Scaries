# -*- coding: utf-8 -*-
"""This Module creates video elements


"""
import os

import toml
from database import get_multiple_stories

# TODO: Look at https://github.com/python-diamond/Diamond for performance
#  metrics
SECTION_CHAR = "\n\n&#x200B;\n\n"
PARAGRAPH_CHAR = "\n\n"
P_TAGS = "</p><p>"
MAX_HTML_CHARS = 1850
SCREENSHOT_WIDTH_RATIO = 0.75
VOICE = "geralt"
PRESET = "standard"


def get_video_data(reddit_id):
    collection = get_mongo_collection()
    story = collection.find_one({"_id": reddit_id})
    if story:
        {
            "id": story["_id"],
            "title": story["title"],
            "title_flair": story["title_flair"],
            "author": story["author"],
            "author_flair": story["author_flair"],
            "awards": story["awards"],
            "url": story["url"],
            "created": story["created_text"],
            "html_text": story["html_text"],
        }
    exit(1)


def upload_videos(num_videos: int) -> None:
    """Generated videos based on their series_id in the database
    Videos with the lowest series_id and series_part have the highest priority

    Args:
        num_videos: The number of videos to create
    """

    # Create directory if it doesn't because it doesn't exist
    path = toml.load("config/config.toml")["ASSETS"]["PATH"]

    if not os.path.exists(path):
        os.makedirs(path)

    for story in get_multiple_stories(num_videos):
        html_templates, audio_clips = format_video_text(story["text"])

        # create a screenshot for each text segment and title
        # create_screenshots(story, html_templates, path)

        kaggle_upload_audio_text(story["id"], audio_clips)

        # # create audio clips for each text segment and title
        # create_audio_clips(
        #     audio_clips=audio_clips,
        #     voice=VOICE,
        #     preset=PRESET,
        #     output_path=path,
        # )

        # create final video
        # create_video(path, len(ssml))

        # post to YouTube

        # mark as posted


upload_videos(6)
