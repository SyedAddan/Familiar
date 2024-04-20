import replicate


def avatar_creation(voice_path, face_path):

    source_audio = open(
        voice_path, "rb")
    source_image = open(
        face_path, "rb")
    input = {
        "driven_audio": source_audio,
        "source_image": source_image
    }

    output = replicate.run(
        "lucataco/sadtalker:85c698db7c0a66d5011435d0191db323034e1da04b912a6d365833141b6a285b",
        input=input
    )
    print(output)
    return output
