import os
import base64
import time
import banana_dev as banana
from datetime import timedelta

BANANA_PRICE = 0.00051992

def tts(text, voice, output_file):
    print(f"Generating Audio for {output_file}")
    start = time.time()
    out = banana.run(
        BANANA_API_KEY,
        BANANA_MODEL_KEY,
        {
            'text': text,
            'voice': voice,
            'preset': 'fast',
        })
    end = time.time()

    # Convert response to mp3 and save audio to disk
    encoded_bytes = out['modelOutputs'][0]['audio'].split(',')[1].encode("ascii")
    decoded_bytes = base64.decodebytes(encoded_bytes)

    with open(output_file, "wb") as mp3_file:
        mp3_file.write(decoded_bytes)

    elapsed_time = end - start
    time_d = timedelta(seconds=round(end - start))
    print("Banana")
    print(f"TTS Time: {time_d} (HH:MM:SS)")
    price = str(round(elapsed_time * BANANA_PRICE, 4))
    print(f"TTS Price: ${price}\n\n")
    return end - start
    print(f"Generating Audio for {output_file}")
    start = time.time()
    out = banana.run(
        api_key,
        model_key,
        {
            'text': text,
            'voice': voice,
            'preset': 'fast',
        })
    end = time.time()

    # Convert response to mp3 and save audio to disk
    encoded_bytes = out['modelOutputs'][0]['audio'].split(',')[1].encode(
        "ascii")
    decoded_bytes = base64.decodebytes(encoded_bytes)
    with open(output_file, "wb") as mp3_file:
        mp3_file.write(decoded_bytes)

    return timedelta(seconds=round(end - start))

