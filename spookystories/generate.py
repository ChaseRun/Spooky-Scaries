import os
from utils.audio.google import generate_audio
from utils.runtime import print_runtime
from utils.databse import MongoDB
from utils.youtube import upload_to_youtube
from utils.video import generate_background_images, generate_video

SCREENSHOT_WIDTH_RATIO = 0.8


# TODO: Switch Google Credentials for TTS
# TODO: Fix Backgrounds
# TODO: Lambda Script Once a Day: Call Import Top 20 of month and generate


@print_runtime
def generate():
    # add option for custom story
    mongoDB = MongoDB("story")
    # if no story available, get top 5 from month that aren't in DB
    story = mongoDB.highest_priority_video()
    dir = f"{os.path.dirname(os.path.abspath(__file__))}/{story['_id']}"
    os.makedirs(dir, exist_ok=True)

    # print(f"Starting Video Generation for {story['title']}")
    generate_audio(story, dir)
    generate_background_images(story, dir)
    generate_video(dir)
    upload_to_youtube(story, dir)

    # delete directory

    print(" - Finished!")

if __name__ == "__main__":
    generate()