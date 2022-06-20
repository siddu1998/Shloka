from shloka import speechToEnglish,speechToHindi,record_player_audio

audio_file=record_player_audio()
user_hindi=speechToHindi(audio_file)
user_english=speechToEnglish(audio_file)
print(user_hindi)
print(user_english)

