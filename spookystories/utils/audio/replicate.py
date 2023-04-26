import os
import time
import replicate
import requests
from datetime import timedelta

REPLICATE_PRICE = 0.00055


def replicate_tts(text, voice, output_file):
    print(f"Generating Audio for {output_file}")

    output = None
    start = time.time()
    while output is None:
        try:
            output = replicate.run(
                "afiaka87/tortoise-audio:e9658de4b325863c4fcdc12d94bb7c9b54cbfe351b7ca1b36860008172b91c71",
                input={
                    "text": text,
                    "voice_a": voice,
                    "preset": "fast",
                }
            )
        except replicate.exceptions.ModelError as e:
            print(e)
            pass
    end = time.time()

    # Convert response to mp3 and save audio to disk
    rsp = requests.get(output)
    with open(output_file, 'wb') as f:
        f.write(rsp.read())

    return timedelta(seconds=round(end - start))

