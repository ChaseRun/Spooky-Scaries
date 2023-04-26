import os
from utils.audio.google import generate_audio
from utils.runtime import print_runtime
from utils.databse import MongoDB
from utils.youtube import upload_to_youtube
from utils.video import generate_background_images, generate_video

SCREENSHOT_WIDTH_RATIO = 0.8


# TODO: Fix Backgrounds
# TODO: Schedule Upload Date
#

@print_runtime
def generate():
    mongoDB = MongoDB("story")
    # get relevant story

    # add an update_upload_date for all story's not posted
    # should be okay to overide if the date is in the past
    story = mongoDB.highest_priority_video()
    dir = f"{os.path.dirname(os.path.abspath(__file__))}/{story['_id']}"
    os.makedirs(dir, exist_ok=True)

    # print(f"Starting Video Generation for {story['title']}")
    # generate_audio(story, dir)
    # generate_background_images(story, dir)
    # generate_video(dir)
    upload_to_youtube(story, dir)

    # delete directory

    print(" - Finished!")

if __name__ == "__main__":
    generate()