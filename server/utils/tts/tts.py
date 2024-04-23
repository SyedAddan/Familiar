import os
import replicate

REPLICATE_API_KEY = os.environ["REPLICATE_API_TOKEN"]
api = replicate.Client(api_token=REPLICATE_API_KEY)

def voice_cloning(audio_path, text):
    source_audio = open(
        audio_path, "rb")

    input = {
        "speaker": source_audio,
        "text": text
    }

    output = api.run(
        "lucataco/xtts-v2:684bc3855b37866c0c65add2ff39c78f3dea3f4ff103a436465326e0f438d55e",
        input=input
    )
    print(output)
    return output
