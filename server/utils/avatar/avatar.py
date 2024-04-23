import os
import replicate

REPLICATE_API_KEY = os.environ["REPLICATE_API_TOKEN"]
api = replicate.Client(api_token=REPLICATE_API_KEY)

def avatar_creation(voice_path, face_path):

    source_audio = open(
        voice_path, "rb")
    source_image = open(
        face_path, "rb")
    input = {
        "driven_audio": source_audio,
        "source_image": source_image
    }
    output = api.run(
        "lucataco/sadtalker:85c698db7c0a66d5011435d0191db323034e1da04b912a6d365833141b6a285b",
        input=input
    )
    print(output)
    return output
