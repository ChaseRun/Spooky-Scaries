import os
import glob
import random
from utils.audio.google import generate_audio
from utils.runtime import print_runtime
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.VideoClip import ImageClip
from moviepy.editor import VideoFileClip
from PIL import Image
from playwright.sync_api import sync_playwright
import multiprocessing
from dotenv import load_dotenv


load_dotenv()
BACKGROUNDS = os.getenv("BACKGROUNDS_DIR")
CHANNEL_INTRO = os.getenv("CHANNEL_INTRO")
CWD = os.path.abspath(__file__)
IMAGE_TEMPLATE = os.getenv("HTML_TEMPLATE")
IMAGE_WIDTH_RATIO = 0.82
IMAGE_TRANSPARENCY = 210


@print_runtime
def generate_background_images(story: dict[str, str], dir) -> None:
    """Generates a png file that will be the background for a video segment
    Post data is used to create an HTML file based on a template. This HTML
    is used to create a screenshot.

    Args:
        story: Data containing a story's  id, tile, flair, created time,
               author, author flair, awards, and a text segment
    """
    print(" - Creating Background Images")

    # create a common "story" template
    with open(IMAGE_TEMPLATE, "r", encoding="utf8") as file:
        story_tmp = file.read()
        for key, value in sorted(story.items()):
            if type(value) == str:
                story_tmp = story_tmp.replace(key.upper(), value)

    # create each background image
    for idx, text in enumerate(story["html_text"]):

        image_file = f"{dir}/{idx}.png"
        tmp_file = f"{dir}/{idx}.html"
        if os.path.isfile(image_file): continue

        # create template
        with open(tmp_file, "w", encoding="utf8") as file:
            file.write(story_tmp.replace("TEXT", text))

        # get a browser screenshot using the template
        with sync_playwright() as p:
            browser = p.chromium.launch()
            image_taker = new_context(device_scale_factor=6).new_page()
            image_taker.goto(f"file://{CWD}/{tmp_file}")
            image_taker.query_seector(".screenshot-div")
            image_taker.screenshot(path=image_file,
                                   omit_background=True,
                                   animations="disabled")
        # resize the image
        image = Image.open(image_file)
        width, height = int(image.width), int(image.height)
        ratio = int((final_width * BACKGROUND_WIDTH_RATIO) / width)
        image = image.resize((width * ratio, height * ration))

        # adjust opacity
        clean_pixels = []
        for pixel in image.getdata():
            if pixel[3] != 255:
                clean_pixels.append((255, 255, 255, 0))
            else:
                clean_pixels.append((p[0], p[1], p[2], TRANSPARENCY))

        # save
        image.putdata(clean_pixels)
        image.save(image_file)
        os.remove(tmp_file)


@print_runtime
def generate_video(dir: str):
    file_name = f"{dir}/final.mp4"
    if os.path.isfile(file_name): return

    print(" - Creating Video")

    # combine each section's image and audio
    content, content_time = [], 0
    num_sections = len(glob.glob1(dir, "*.mp3"))
    for idx in range(1, num_sections):
        audio = AudioFileClip(f"{dir}/{idx}.mp3")
        section = (ImageClip(f"{dir}/{idx}.png")
                   .set_audio(audio)
                   .set_duration(audio.duration)
                   .set_start(start_time)
                   .set_pos(("center", "center")))
        content_time += audio.duration
        content.append(section)

    # get the background video
    num_backgrounds = len(glob.glob1(BACKGROUNDS, "*.mp4"))
    bg_file = random.randint(0, num_backgrounds)
    background = VideoFileClip(f"{BACKGROUNDS}/{bg_file}.mp4")

    # add background video to each sections
    background = background.without_audio()
    background = background.loop(duration=content_time)
    content.insert(0, background)
    content = CompositeVideoClip(content)

    # add channel intro
    intro = VideoFileClip(CHANNEL_INTRO)
    final_video = concatenate_videoclips([intro, content])

    # create video
    try:
        write_video(final_video, file_name)
        print(f"Saved .mp4 without Exception at {path}/final_video.mp4")
    except IndexError:
        # Short by one frame, so get rid on the last frame:
        final_video = final_video.subclip(
            t_end=(final_video.duration - 1.0 / 60)
        )
        write_video(final_video, file_name)
        print(f"Saved .mp4 after Exception at {path}/final_video.mp4")
    except Exception as e:
        print(f"Exception {e} was raised!!")


@print_runtime
def write_video(video_content, file_name):
    video_content.write_videofile(
        file_name,
        fps=60,
        audio_codec="aac",
        audio_bitrate="3000k",
        verbose=True,
        threads=multiprocessing.cpu_count(),
    )



#
# def resize_image(image_file):
#     final_width = 3840
#     final_height = 2160
#
#     image = Image.open(image_file)
#     new_width, new_height = int(image.width * ratio), int(image.height * ratio)
#     image = image.resize((new_width, new_height))
#     # image.save(image_file)
#     # return
#
#     # make borders transparent
#     rgba = image.convert("RGBA")
#     pixels = rgba.getdata()
#     new_pixels = []
#     for idx in range(len(pixels)):
#
#         p = pixels[idx]
#         new_p = (p[0], p[1], p[2], p)
#         if pixels[idx][3] != 255:
#             new_pixels.append((255, 255, 255, 0))
#         else:
#             new_pixels.append((p[0], p[1], p[2], 210))
#     rgba.putdata(new_pixels)
#     rgba.save(image_file)
#
#
#
# def generate_video_old():
#     final_video = []
#     # add channel intro
#     final_video.append(VideoFileClip(f"{dir}/../../assets/channel_intro.mp4"))
#     # add audio to screenshots
#     num_segments = len(glob.glob1(dir, "*.mp3"))
#     for idx in range(num_segments):
#         image_file, audio_file = f"{dir}/{idx}.jpeg", f"{dir}/{idx}.mp3"
#         video = ImageClip(image_file)
#         audio = AudioFileClip(audio_file)
#         video.duration = audio.duration
#         video.audio = audio
#         final_video.append(video)
#
#     final_video = concatenate_videoclips(final_video)
#     try:
#         write_video(final_video, dir)
#         print(f"Saved .mp4 without Exception at {path}/final.mp4")
#     except IndexError:
#         # Short by one frame, so get rid on the last frame:
#         final_video = final_video.subclip(
#             t_end=(final_video.duration - 1.0 / 60)
#         )
#         write_video(final_video, dir)
#         print(f"Saved .mp4 after Exception at {path}/final.mp4")
#     except Exception as e:
#         print(f"Exception {e} was raised!!")
#
#
