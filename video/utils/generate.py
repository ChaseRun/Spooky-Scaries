import os

import toml
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.VideoClip import ImageClip
from PIL import Image
from playwright.sync_api import sync_playwright


def create_screenshots(
    story: dict[str, str], segments: list[str], path: str
) -> None:
    """Generates a png file that will be the background for a video segment
    Post data is used to create an HTML file based on a template. This HTML
    is used to create a screenshot.

    Args:
        story: Data containing a story's tile, flair, created time,
               author, author flair, awards, and a text segment
        segments: The text to put in the screenshots
        path: The directory to create the images
    """

    config = toml.load("config/config.toml")["ASSETS"]
    screenshot_template = config["SCREENSHOT_TEMPLATE"]

    # add empty string for title
    for idx, current_html in enumerate(segments):
        story["text"] = current_html
        html_file = f"{path}/{idx}.html"
        jpeg_file = f"{path}/{idx}.jpeg"
        with open(screenshot_template, "r", encoding="utf8") as file:
            template = file.read()
            for k, v in story.items():
                template_key = f"{{{{ {k} }}}}"
                template = template.replace(template_key, v)
            with open(html_file, "w", encoding="utf8") as output:
                output.write(template)

        # generate screenshot
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context(device_scale_factor=6)
            page = context.new_page()
            page.goto(f"file://{os.path.abspath(html_file)}")
            page.query_selector(".screenshot-div").screenshot(
                path=jpeg_file, quality=100, type="jpeg"
            )

        # resize image
        resize_image(jpeg_file)

        # delete generated html
        os.remove(html_file)


def resize_image(image_file):
    final_width = 3840
    final_height = 2160

    image = Image.open(image_file)
    ratio = (final_width * SCREENSHOT_WIDTH_RATIO) / image.width
    new_width, new_height = int(image.width * ratio), int(image.height * ratio)
    resized_image = image.resize((new_width, new_height))

    background = Image.new(mode="RGB", size=(3840, 2160), color=(38, 38, 38))

    top_corner_width = int((final_width - new_width) / 2)
    top_corner_height = int((final_height - new_height) / 2)

    background.paste(resized_image, box=(top_corner_width, top_corner_height))
    background.save(image_file)


def create_video(path: str, num_clips: int):
    """

    Args:
        num_clips ():
        directory ():
    """
    # combine audio and background
    final_video = []

    intro_video = VideoFileClip(f"{path}/Intro.mp4")
    final_video.append(intro_video)

    # add audio to screenshots
    for idx in range(num_clips):
        image_file, audio_file = f"{path}/{idx}.jpeg", f"{path}/{idx}.mp3"

        video = ImageClip(image_file)
        audio = AudioFileClip(audio_file)
        video.duration = audio.duration
        video.audio = audio

        final_video.append(video)

    final_video = concatenate_videoclips(final_video)

    try:
        final_video.write_videofile(
            f"{path}/final_video.mp4",
            fps=60,
            audio_codec="aac",
            audio_bitrate="3000k",
            verbose=True,
            threads=multiprocessing.cpu_count(),
        )
        print(f"Saved .mp4 without Exception at {path}/final_video.mp4")
    except IndexError:
        # Short by one frame, so get rid on the last frame:
        final_video = final_video.subclip(
            t_end=(final_video.duration - 1.0 / 60)
        )
        final_video.write_videofile(
            f"{path}/final_video.mp4",
            fps=60,
            audio_codec="aac",
            audio_bitrate="3000k",
            verbose=True,
            threads=multiprocessing.cpu_count(),
        )
        print(f"Saved .mp4 after Exception at {path}/final_video.mp4")
    except Exception as e:
        print(f"Exception {e} was raised!!")

    for idx in range(num_clips):
        image_file, audio_file = f"{path}/{idx}.jpeg", f"{path}/{idx}.mp3"
        os.remove(image_file)
        # os.remove(audio_file)

    return f"{path}/final_video.mp4"
