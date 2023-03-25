import os

def file_exists(audio, s3_files):
    # clip segment
    if ".wav" in audio:
        print(f"{audio} exists locally")
        if os.path.isfile(audio):
            return True
        print(f"{audio} exists on s3")
        if audio in s3_files:
            s3.download(audio)
            return True

    # full_clip
    else:
        # create local output dir if path
        if not os.path.exists(audio):
            os.makedirs(audio)
        # if clip file has been generated continue
        if f"{audio}.wav" in s3_files:
            print(f"{audio}.wav exists on s3")
            return True
    return False