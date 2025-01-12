#reconocimiento de voz con google recognition

import speech_recognition as sr
speech = sr.Recognizer()
with sr.Microphone() as source:
    print("Hable algo: ")
    audio = speech.listen(source)
    try:
        text = speech.recognize_google(audio)
        print("Tu dijiste: {}".format(text))
    except:
        print("No se pudo reconocer el audio")
        