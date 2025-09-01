import tkinter as tk
from tkinter import scrolledtext, messagebox
from ytmusicapi import YTMusic
import speech_recognition as sr
import keyboard, os, sys, datetime, webbrowser, threading, wikipedia
import pyttsx3, re
from pyowm import OWM


owm = OWM('716762da637237d9c7631b0c80be4ed7')
mgr = owm.weather_manager()
recognizer = sr.Recognizer()
ytmusic = YTMusic()
engine = pyttsx3.init()
voices = engine.getProperty('voices')

listening = False
text_area = None
start_btn = None  # Declare globally
def output(msg,c):
    if c == "red":
        text_area.tag_configure("normal1", foreground="red")
        if text_area:
            text_area.insert(tk.END, msg + '\n',"normal1")
            text_area.see(tk.END)
            text_area.update_idletasks()
    elif c == "blue":
        text_area.tag_configure("normal2", foreground="blue")
        if text_area:
            text_area.insert(tk.END, msg + '\n',"normal2")
            text_area.see(tk.END)
            text_area.update_idletasks()
    else:
        text_area.tag_configure("normal3", foreground="black")
        if text_area:
            text_area.insert(tk.END, msg + '\n',"normal3")
            text_area.see(tk.END)
            text_area.update_idletasks()




def Assistant_output(msg):
    if text_area:
        text_area.tag_configure("boldncolor", font=("TkDefaultFont", 10, "bold"), foreground="green")
        text_area.tag_configure("color", foreground="green")
        text_area.insert(tk.END, '\n' + "Assistant: ", "boldncolor")
        text_area.insert(tk.END, msg + '\n' + '\n', "color") 
        text_area.see(tk.END)
        text_area.update_idletasks()

def speak(msg):
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 150)
    engine.say(msg)
    engine.runAndWait()


#---------- Functions ----------#
def play_music(s):
    if not s:
        Assistant_output("No song specified.")
        return
    results = ytmusic.search(s, filter="songs")
    if results:
        videoId = results[0]['videoId']
        url = f"https://music.youtube.com/watch?v={videoId}"
        webbrowser.open(url)
        speak(f"Playing {s}")
        Assistant_output(f"Playing {s}")
    else:
        Assistant_output(f"No results found for {s}")

def current_time():
    time_str = datetime.datetime.now().strftime("%I:%M %p")
    Assistant_output(f"Current time: {time_str}")

def date_today():
    date_str = datetime.datetime.now().strftime("%B %d, %Y")
    Assistant_output(f"Today's date: {date_str}")

def wikipedia_search(command):

    try:

        query_match = re.search(
            r"^(?:search|find|what is|who is|what are|who are|tell me about)\s+(.*)",command,re.IGNORECASE)
        
        if query_match:
            query = query_match.group(1).strip()
            
            summary = wikipedia.summary(query, sentences=3)
            
            if summary:
                Assistant_output(summary)
                speak(summary)
                return True
            else:
                return False
                
    except wikipedia.exceptions.PageError:
        Assistant_output("No results found on Wikipedia")
        speak("No results found on Wikipedia")
        return False
        
    return False

def get_weather(city):
    try:
        observation = mgr.weather_at_place(city)
        weather_now = observation.weather
        Assistant_output(f"Weather in {city}: {weather_now.detailed_status}, Temperature: {weather_now.temperature('celsius')['temp']}°C")

    except:
        Assistant_output(f"Could not get weather for {city}")



#---------- Speech Recognition and fuction call for voice commands ----------#
# Get voice command
def get_command():
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)
            output("Listening...","black")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            command = recognizer.recognize_google(audio)
            return command.lower()
    except sr.WaitTimeoutError:
        output("No command detected (timeout).","red")
        return None
    except sr.UnknownValueError:
        output("Could not understand the audio.","red")
        return None
    except sr.RequestError as e:
        output(f"Speech recognition error: {e}","red")
        return None
    
#main loop
def main():
    global listening
    while listening:
        command = get_command()
        if command is None:
            continue
        output(f"You: {command}","blue")
        if command.startswith("play"):
            play_music(command[4:].strip())
            stop_listening()
        elif "time" in command and "now" in command:
            current_time()
            stop_listening()
        elif "date" in command and "today" in command:
            date_today()
            stop_listening()
        elif "who" in command or "what" in command:
            wikipedia_search(command)
            stop_listening()
        elif "weather" in command:
            weather_match = re.search(r"weather in (.+)", command, re.IGNORECASE)
            if weather_match:
                city = weather_match.group(1).strip()
                get_weather(city)
                stop_listening()
        else:
            output("Sorry, I can't understand that. Please try again.","red")


# Start and Stop Listening Functions and shortcut key to start listening
def start_listening():
    global listening, start_btn
    if not listening:
        listening = True
        start_btn.config(state=tk.DISABLED)
        #output("Started listening...")
        output("-----------------------------------","black")
        # Run main in a separate thread to avoid freezing the GUI
        threading.Thread(target=main, daemon=True).start()
def stop_listening():
    global listening, start_btn
    listening = False
    start_btn.config(state=tk.NORMAL)
    output("Stopped listening.","black")

#shortcut key to start listening
keyboard.add_hotkey('space+l', start_listening)

#---------- GUI Setup using Tkinter ----------#
root = tk.Tk()
root.title("Kai 1.0")
root.geometry("600x500")
root.resizable(False, False) # making the window non-resizable
menubar = tk.Menu(root)

# About Dialog Window
def about_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("About")
    dialog.geometry("300x125")
    dialog.resizable(False, False)
    dialog.grab_set()
    url = "https://github.com/MevinuAbey/Assistant"

    tk.Label(dialog, text="KAI 1.0\nCS50 Introduction to Programming with Python\nFinal Project By Mevinu Abeysinghe",
             justify="left", font=("sans", 10)).pack(pady=10)

    link_label = tk.Label(dialog, text="GitHub Repository", fg="blue", cursor="hand2", font=("Arial", 10, "underline"))
    link_label.pack()
    link_label.bind("<Button-1>", lambda e: webbrowser.open_new(url))

# Top bar
spacer_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label=" " * 166, menu=spacer_menu)
menubar.add_cascade(label="About", command=about_dialog)
menubar.add_cascade(label="Exit", command=root.destroy)
root.config(menu=menubar)

# Title
title_label = tk.Label(root, text="Kai", font=("sans", 30))
title_label.pack(side=tk.TOP, pady=10)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(side=tk.TOP, pady=10)

start_btn = tk.Button(
    button_frame,
    text="Start Listening",
    font=("sans", 13),
    command=start_listening,
    bg='green',
    fg='black',
    width=15,
    height=2
)
start_btn.pack(side=tk.LEFT, padx=10)

# output text area
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=15)
text_area.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)
root.mainloop()
