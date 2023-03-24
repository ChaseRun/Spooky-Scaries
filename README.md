# Spooky Scaries

This repository automates the creation of youtube videos for the spooky scaries
channel

## Description

## Project Iterations

### Version 1:

- Call Reddit API and store ID's in Excel table
- Then Begin Video Generation
    - Re-call Reddit API based on ID in table
    - Extract Text/Story
    - Sanitize story text and save as Plain Text.
    - Create Audio from plain text using AWS Polly
    - Manually find an image online to user as a background
    - Manually edit this image, unique for each story
    - Create video by adding audio to background
    - Manually upload to YouTube
        - Uploaded plain text file to YouTube for subtitles
    - Manually mark video as saved in Excel sheet

### Version 2

- One difference from First Iteration
- Formatted Story text into Plain Text and SSML text
    - SSML text improved audio Quality

### Version 3

- Process 1: Save Data
    - Call Reddit API and story ID's along with story text in a SQL DB
    - This removes a redundant call to the reddit API later on in the video
      genetation process

- Process 2: Generate Video
    - Get Story Text from DB
    - Format Story Text into a list of HTML / Sanitized Text Pair. Each item
      in the list will be referred to as a "segment".
        - HTML Text
            - Each HTML segment is used to create a custom jpeg background
              image.
            - Each images contain story text at different intervals of the
              story. This lets the viewer "read along" throughout the video.
                - This eliminates the need to generate YouTube subtitles.
            - An HTML file is rendered using a predefined template and the
              HTML segment.
            - A screenshot of this HTML file is saved/formatted as a 4k jpeg
              image.
        - Sanitized Text.
            - Each segment represents an audio file that will be used for the
              corresponding background image.
            - Each segment contains a list of
              strings (sub-segments).
            - A new custom TTS engine is used.
            - The length of each sub-segment is less than the TTS Engine's char
              limit
            - An Audio file for each sub-segment is generated. Sub-segments
              are combined to from one audio file. This audio files maps to
              a single screenshot
        - Create Video
            - Combine each screenshot and it's corresponding audio.
            - Combine a YoutubeIntro
        - Automatically upload to YouTube using YouTube API.
            - Designate a specific date for it to be released
        - Mark as Uploaded in the DB

## Main Drawback:

- The TTS engine is EXTREMELY GPU INTENSIVE!
- Generating the Audio for a single sentence takes 1hr on my personal
  computer!
- This is not sustainable.

### Solution 1:

- Try using free Jupyter notebook platforms that provide GPUs
- I experimented with Google Colab, Kaggle, and Paperspace Gradient
- Problems:
    - Platforms offer limited GPU compute hours per week/month.
    - Generation for a Video still takes ~10-15 hours depending on the length
      of the story.
    - Idle times (Maximum time your can leave your notebook idling before it
      shuts down) interrupt TTS process.
    - Only a few platforms offer the option to automatically query a notebook.
        - I would have log into a platform using my browser, load/attach the
          audio dataset, and then manually run the program.
        - This is not feasible for my goal of having a fully automated
          YouTube.

### Solution 2:

- Experiment with Dedicated / Spot GPU instances
- Will potentially cost significantly more than I expected for this project.

### New design changes

- Database will be an AWS Aurora DB
- Reddit.py will store test segments in a db table
    - Generate Audio can query this directly

### Next Steps

- Benchmark Each notebook platform that allows automatic queries
- Benchmark GPU Instances on multiple platforms.
    - Maybe utilize free cloud credits for platform's I haven't signed up for
      before. Benchmark "Spot Instances".
- Using this determines a "reasonable" number of stories I can upload a wee
  based on which server option is the most cost/time efficient.
    - I can maybe ask family and friends to create notebook platform accounts
      for me :).
- Create individual services for Reddit scraping, background image
  generation, audio generation, final video generation, and YouTube uploading.
    - Will probably need to migrate to a Cloud Architecture

## Benchmarking

- inf1: Did not work
- G3
- P3
- P3dn
- P4d
- G5
- G4dn

[inf Instances Docs](https://docs.aws.amazon.com/dlami/latest/devguide/tutorial-inferentia.html)
[Helpful Setup](https://awsdocs-neuron.readthedocs-hosted.com/en/latest/general/quick-start/torch-neuron.html#torch-quick-start)

| Cloud Provider | Instance     | Benchmark (sec) | Price/hr | Cost Ratio       |
|----------------|--------------|-----------------|----------|------------------|
| Google Colab   | NA           | 0s              | $0.00    | 0.00 dollars/sec |
| Kaggle         | NA           | 0s              | $0.00    | 0.00 dollars/sec |
| Gradient       | NA           | 0s              | $0.00    | 0.00 dollars/sec |
| AWS            | g4ad.2xlarge | 0s              | $0.00    | 0.00 dollars/sec |
| AWS            | g4dn.2xlarge | 0s              | $0.00    | 0.00 dollars/sec |
