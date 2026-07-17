from pydub import AudioSegment

sound = AudioSegment.from_mp3("sounds/scan.mp3")
trimmed = sound[:3000]
trimmed.export("sounds/scan.mp3", format="mp3")
print("Done! Scan sound trimmed to 3 seconds!")
