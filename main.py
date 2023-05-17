from tkinter import *
import customtkinter as ct
import requests
from tkinter import messagebox
from googletrans import Translator
import json
from tkinter import filedialog
import time
import speech_recognition as sr
import moviepy.editor
import os
from pydub import AudioSegment
import pysrt
import sqlite3
import threading
from threading import Thread
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


# Get config prefences from JSON
def get_bg_theme():
    with open("theme_config.json", "r") as f:
        theme = json.load(f)
    return theme["bg_theme"]

# Set themes
ct.set_appearance_mode(get_bg_theme())

translator = Translator()

# Starting main window
one = ct.CTk()
one.title('Translator')
one.geometry(f"{700}x{450}+{570}+{270}")
one.wm_resizable(False, False)
one.iconbitmap("icon.ico")

# Appearance theme function
def changeTheme(color):
    color = color.lower()
    themes_list = ["system", "dark", "light"]
    if color in themes_list:
        ct.set_appearance_mode(color)
        to_change = "bg_theme"
    else:
        ct.set_default_color_theme(color)
        ct.CTkLabel(one, text = "(Restart to take full effect)", font = ("arial", 12)).place(x = 242 , y = 415)
        to_change = "default_color"
    with open("theme_config.json", "r", encoding="utf8") as f:
        theme = json.load(f)
    with open("theme_config.json", "w", encoding="utf8") as f:
        theme[to_change] = color
        json.dump(theme, f, sort_keys = True, indent = 4, ensure_ascii = False)
ct.CTkLabel(one, text = "Appearance Settings", font = ("arial bold", 19)).place(x=490, y=365)
themes_menu = ct.CTkOptionMenu(one, values = ["System", "Dark", "Light"], width = 130, command = changeTheme, corner_radius = 15)
themes_menu.place(x = 520 , y = 405)
themes_menu.set(get_bg_theme().title())

# Voice input to text function
def voice_to_text():
 r = sr.Recognizer()
 tr_textbox.configure(state="disabled")
 with sr.Microphone() as source:
    r.adjust_for_ambient_noise(source)
    audio_text = r.listen(source,timeout=5)
    try:
     text = r.recognize_google(audio_text)
     tr_textbox.delete("1.0", END)
     tr_textbox.insert(END, text)
     tr_textbox.configure(state="normal")
    except:
     return messagebox.showerror('Error', 'Please try again')



# Main window widgets
ct.CTkLabel(one, text= "Enter The Text:", font=(None, 29, 'bold')).place(x= 85, y= 25)
ct.CTkLabel(one, text= "The Translation:", font=(None, 29, 'bold')).place(x= 397, y= 25)
ct.CTkLabel(one, text= "From:", font=(None, 20)).place(x= 110, y= 235)
ct.CTkLabel(one, text= "To:", font=(None, 20)).place(x= 430, y= 235)
tr_textbox = ct.CTkTextbox(one, width=280, height=150, font=(None, 21), corner_radius=15)
tr_textbox.place(x= 50, y= 70)
to_tr_textbox = ct.CTkTextbox(one, width=280, height=150, font=(None, 21), corner_radius=15)
to_tr_textbox.place(x= 370, y= 70)
to_tr_textbox.configure(state="disabled")
from_lang_list = ["Auto", "Arabic", "Chinese (simplified)", "Chinese (traditional)", "English", "French", "German", "Italian", "Japanese", "Korean", "Portuguese", "Russian", "Spanish", "Turkish"]
from_lang_combo = ct.CTkComboBox(one, width= 90, values= from_lang_list, corner_radius=15)
from_lang_combo.place(x= 170, y= 237)
to_lang_list = ["Arabic", "Chinese (simplified)", "Chinese (traditional)", "English", "French", "German", "Italian", "Japanese", "Korean", "Portuguese", "Russian", "Spanish", "Turkish"]
to_lang_combo = ct.CTkComboBox(one, width= 90, values= to_lang_list, corner_radius= 15)
to_lang_combo.place(x= 465, y= 237)
ct.CTkButton(one, text="Voice", font=(None, 18), width= 70, height=30,command=voice_to_text, corner_radius= 4).place(x=250, y= 180)
one.bind('<Return>', lambda event: translate())

# On closing the app
def closing():
  one.destroy()
one.protocol("WM_DELETE_WINDOW", closing)

# On back button
def back(window):
  one.deiconify()
  window.withdraw()



# Text translate function
def translate():
  timeout = 1
  statues = ""
  word = tr_textbox.get("1.0", END)
  from_language = from_lang_combo.get()
  to_language = to_lang_combo.get()

  if word.strip() == "":
    return messagebox.showerror('Error', 'Please enter text to translate.')
  elif not from_language in from_lang_list:
    return messagebox.showerror('Error', 'Please check the language you are translating from.')
  elif not to_language in to_lang_list:
    return messagebox.showerror('Error', 'Please check the language you are translating to.')
  try:
    requests.head("http://www.google.com/", timeout=timeout)
    statues = "online"
  except requests.ConnectionError:
    statues= "offline"
  except requests.exceptions.Timeout:
    statues = "timeout"
  if statues == "online":
    try:
      if from_language == "Auto":
        tran = translator.translate(word, dest=to_language)
      else:
        tran = translator.translate(word, dest=to_language, src=from_language)
    except TypeError:
      messagebox.showerror('Error', 'Sorry, an unexpected error has occured. Please try again.')
    if tran.text == word:
        messagebox.showerror('Error', 'Please check your text or language selection.')
    else:
      to_tr_textbox.configure(state="normal")
      to_tr_textbox.delete("1.0", END)
      to_tr_textbox.insert(END, tran.text)
      to_tr_textbox.configure(state="disabled")
    current_string = datetime.now() # Current date in string/readable format
    current_timestamp = int(current_string.timestamp()) # Current date as a time stamp
    with sqlite3.connect("history.db") as db:
      cursor = db.cursor()
      cursor.execute("CREATE TABLE IF NOT EXISTS history (original TEXT, translation TEXT, time_stamp INTEGER)")
      cursor.execute("INSERT INTO history (original, translation, time_stamp) VALUES (?, ?, ?)", (word, tran.text, current_timestamp,))
      db.commit()
  elif statues == "offline":
    messagebox.showerror('Error', 'Please check your connection')
  elif statues == "timeout":
    messagebox.showerror('Error', 'Connection timeout. Please try again later.')
# Text Translate button
ct.CTkButton(one, text="Translate", corner_radius = 16 , font=(None, 20), width= 190, height=40, command=translate).place(x=255, y= 295)

# Open file translation window
def openfile_tr_win():
  one.withdraw() # Withdraw main window
  # Open new window
  file_tr_win = ct.CTkToplevel()
  file_tr_win.title("File Translator")
  file_tr_win.geometry(f"{700}x{450}+{570}+{270}")
  file_tr_win.resizable(False, False)
  file_tr_win.iconbitmap("icon.ico")
  file_tr_win.protocol("WM_DELETE_WINDOW", closing)

  def locate_txt():
    filepath = filedialog.askopenfilename(title= "Open a text/subtitles file", filetypes=(("text files", "*.txt"),("subtitles files", "*.srt") , ("all files", "*.*")))
    file_path_var.set(filepath)

  # File translation function
  def tr_file():
    timeout = 1
    from_language = from_lang_combo.get()
    to_language = to_lang_combo.get()
    filepath = file_path_var.get()
    file_name = os.path.splitext(os.path.basename(filepath))[0]
    file_type = os.path.splitext(filepath)[1]
    if filepath.strip() == '':
      return messagebox.showerror('Error', 'Error: Please type the file path')
    elif not from_language in from_lang_list:
      return messagebox.showerror('Error', 'Please check the language you are translating from.')
    elif not to_language in to_lang_list:
      return messagebox.showerror('Error', 'Please check the language you are translating to.')
    else:
      if file_type == '.srt' and radio_value.get() == 0:
         subs = pysrt.open(filepath)
         progress.configure(determinate_speed=50/len(subs))        
         for sub in subs:
            translated_text = translator.translate(sub.text, dest=to_language).text
            sub.text = translated_text
            progress.step()
            file_tr_win.update_idletasks()
            time.sleep(1)
         subs.save('translated_subtitles.srt')
         progress.set(0)
         file_tr_win.update_idletasks()
         return messagebox.showinfo('Done','The file has been translated')

      elif file_type == '.srt' and radio_value.get() != 0:
        return messagebox.showerror('Error', ' You can\'t use this option with a srt file')
      else:
       with open(filepath, "r+", encoding="utf8") as data:
         global lines
         lines = data.readlines()
         if lines == []:
           return messagebox.showerror('Error', 'Error: The file is empty')
         tredlines = []
         progress.configure(determinate_speed=50/len(lines))
         try:
           requests.head("http://www.google.com/", timeout=timeout)
           statues = "online"
         except requests.ConnectionError:
           statues= "offline"
         except requests.exceptions.Timeout:
           statues = "timeout"
         if statues == 'online':
           if from_language == "Auto":
             for line in lines:
               a = translator.translate(line, dest=to_language)
               tredlines.append(a.text)
               progress.step()
               file_tr_win.update_idletasks()
               time.sleep(0.1)
           else:
             for line in lines:
               a = translator.translate(line, dest=to_language, src= from_language)
               tredlines.append(a.text)
               progress.step()
               file_tr_win.update_idletasks()
               time.sleep(0.1)
           global string
           string = ""
           for line in tredlines:
               string += (f"{line}\n")
           progress.set(0)
           choice_value = radio_value.get()
           file_name = os.path.basename(filepath)
           file_type = file_name.split(".")[-1].strip()
           tr_textbox.configure(state="normal")
           tr_textbox.delete("1.0", END)
           tr_textbox.insert(END, string)
           tr_textbox.configure(state="disabled")
           if choice_value == 1:
             directory_path = os.path.dirname(filepath)
             with open(f"{directory_path}\{file_name}_translated{file_type}", "w", encoding="utf8") as file:
               file.write(string)
           elif choice_value == 2:
             data.write(f"\n\n{string}")
           elif choice_value == 3:
             with open(filepath, "w", encoding="utf8") as file:
               file.truncate(0)
               file.write(string)
         elif statues == "offline":
           messagebox.showerror('Error', 'Please check your connection')
         elif statues == "timeout":
           messagebox.showerror('Error', 'Connection timeout. Please try again later.')
    file_tr_win.bind('<Return>', lambda event: tr_file())

  # File translation window widgets
  ct.CTkLabel(file_tr_win, text= "Type The File Path (txt/srt):", font=(None, 25)).place(x= 30, y= 30)
  file_path_var = StringVar()
  file_path_entry = ct.CTkEntry(file_tr_win, textvariable=file_path_var, width=260, height=30, font=(None, 15), corner_radius=15)
  file_path_entry.place(x= 30 , y= 75)
  ct.CTkButton(file_tr_win, text= 'Locate', corner_radius=15, font=(None, 17), width=60, command=locate_txt).place(x=300, y=75)
  ct.CTkLabel(file_tr_win, text= "From:", font=(None, 20)).place(x= 40, y=130)
  ct.CTkLabel(file_tr_win, text= "To:", font=(None, 20)).place(x= 220 , y= 130)
  from_lang_combo = ct.CTkComboBox(file_tr_win, width= 90, corner_radius=15, values= from_lang_list)
  from_lang_combo.place(x=100, y=130)
  to_lang_combo = ct.CTkComboBox(file_tr_win, width= 90, values= to_lang_list, corner_radius=15)
  to_lang_combo.place(x=255, y=130)
  radio_value = IntVar()
  new_file_radio = ct.CTkRadioButton(file_tr_win, variable=radio_value, value=1, text ="New file with translation", font=(None, 20))
  new_file_radio.place(x=40, y=185)
  update_file_radio = ct.CTkRadioButton(file_tr_win, variable=radio_value, value=2, text ="Update file with translation", font=(None, 20))
  update_file_radio.place(x=40, y=220)
  replace_file_radio = ct.CTkRadioButton(file_tr_win, variable=radio_value, value=3, text ="Replace file with translation", font=(None, 20))
  replace_file_radio.place(x=40, y=255)
  ct.CTkButton(file_tr_win, text="Translate", font=(None, 20), width= 190, height=40, corner_radius=15, command=tr_file).place(x= 250, y= 330)
  ct.CTkButton(file_tr_win, text= 'Back', font=(None, 20), command=lambda: back(file_tr_win), corner_radius=15, width=70).place(x=20, y= 400)
  progress = ct.CTkProgressBar(file_tr_win, width=240, mode= 'determinate', height= 10, corner_radius=20)
  progress.set(0)
  progress.place(x=230, y=400)
  ct.CTkLabel(file_tr_win, text= "The Translation:", font=(None, 25,'bold')).place(x= 440, y=30 )
  tr_textbox = ct.CTkTextbox(file_tr_win, width=280, height=230, font=(None, 21), corner_radius=15)
  tr_textbox.place(x= 400, y= 75)
  tr_textbox.configure(state="disabled")

# Audio translation window
def openaudiotr():
  one.withdraw() # Main withdraw
  # Window start
  audio_tr_win = ct.CTkToplevel()
  audio_tr_win.title("Audio Translator")
  audio_tr_win.geometry(f"{700}x{450}+{570}+{270}")
  audio_tr_win.resizable(False, False)
  audio_tr_win.iconbitmap("icon.ico")
  audio_tr_win.protocol("WM_DELETE_WINDOW", closing)

  def locate():
    filepath = filedialog.askopenfilename(title= "Open a wav/mp4 file", filetypes=(("Video files", "*.mp4"), ("Audio files", "*.wav"),("Audio files", "*.mp3"), ("all files", "*.*")))
    path_var.set(filepath)

  # Audio translation function
  def audio_tr_winans():
    checkvalue = radio_value2.get()
    print(radio_value2.get())
    r = sr.Recognizer()
    timeout = 1
    try:
      requests.head("http://www.google.com/", timeout=timeout)
      statues = "online"
    except requests.ConnectionError:
      statues= "offline"
    except requests.exceptions.Timeout:
      statues = "timeout"
    from_language = from_lang_combo.get()
    to_language = to_lang_combo.get()
    data = ""
    audio_tr = ''
    filepath = path_var.get()
    if filepath.strip() == "":
      return messagebox.showerror('Error', 'Please type the file path.')
    elif not from_language in from_lang_list:
      return messagebox.showerror('Error', 'Please check the language you are translating from.')
    elif not to_language in to_lang_list:
      return messagebox.showerror('Error', 'Please check the language you are translating to.')
    if statues == 'online':
      file_name = os.path.splitext(os.path.basename(filepath))[0]
      file_type = os.path.splitext(filepath)[1]

      if file_type == "mp4":
          pass
      elif file_type == "wav":
          pass
      elif file_type == "mp3":
          pass
      else:
          return messagebox.showerror('Error', 'File format is not supported.')
      if file_type == '.wav' or file_type == '.mp3' and checkvalue ==2:
        return messagebox.showerror('Error', ' You can\'t use this option with an audio file')
      if file_type == ".mp3":
        input = filepath
        output = "audio_in_wav.wav"
        audio = AudioSegment.from_mp3(input)
        audio.export(output, format="wav")
        with sr.AudioFile(output) as source:
          audio_data = r.record(source)
          adata = r.recognize_google(audio_data)
          data = f"{adata}"
          if from_language == "Auto":
            audio_tr = translator.translate(data, dest=to_language)
          else:
            audio_tr = translator.translate(data, dest=to_language , src=from_language)
          string = ""
          string += audio_tr.text
          tr_textbox.configure(state="normal")
          tr_textbox.delete("1.0", END)
          tr_textbox.insert(END, string)
          tr_textbox.configure(state="disabled")
          if checkvalue == 1:
            save = open(f"{sfile[0]}.txt", "x")
            save.write(string)
      if file_type == ".wav":
        with sr.AudioFile(file_name) as source:
          audio_data = r.record(source)
          adata = r.recognize_google(audio_data)
          data = f"{adata}"
          if from_language == "Auto":
            audio_tr = translator.translate(data, dest=to_language)
          else:
            audio_tr = translator.translate(data, dest=to_language , src=from_language)
          string = ""
          string += audio_tr.text
          tr_textbox.configure(state="normal")
          tr_textbox.delete("1.0", END)
          tr_textbox.insert(END, string)
          tr_textbox.configure(state="disabled")
          if checkvalue == 1:
            save = open(f"{sfile[0]}.txt", "x")
            save.write(string)

      elif file_type == ".mp4":
        if checkvalue == 2:
          video = moviepy.editor.VideoFileClip(filepath)
          audio = video.audio
          audio.write_audiofile("audio.wav")
          r = sr.Recognizer()
          with sr.AudioFile("audio.wav") as source:
           audio = r.listen(source)
           try:
            text = r.recognize_google(audio)
           except:
            text = ""
          subs = pysrt.SubRipFile()
          sentences = text.split(". ")
          start = 0
          end = 0
          for i, s in enumerate(sentences):
           duration = len(s.split()) * 0.6
           end = start + duration
           item = pysrt.SubRipItem()
           item.index = i + 1
           item.start.seconds = start
           item.end.seconds = end
           translation = translator.translate(s, dest=to_language , src=from_language)
           item.text = translation.text
           subs.append(item)
           start = end
          subs.save("subtitles.srt", encoding="utf-8")
          os.remove('audio.wav')

        else:
         videof = filepath
         video = moviepy.editor.VideoFileClip(videof)
         audio = video.audio
         sfile = file_name.split(".")
         audio.write_audiofile(f"{sfile[0]}.wav")
         with sr.AudioFile(f"{sfile[0]}.wav") as source:
          audio_data = r.record(source)
          adata = r.recognize_google(audio_data)
          data = f"{adata}"
          if from_language == "Auto":
            audio_tr = translator.translate(data, dest=to_language)
          else:
            audio_tr = translator.translate(data, dest=to_language , src=from_language)
          string = ""
          string += audio_tr.text
          tr_textbox.configure(state="normal")
          tr_textbox.delete("1.0", END)
          tr_textbox.insert(END, string)
          tr_textbox.configure(state="disabled")
          directory_path = os.path.dirname(filepath)
          if checkvalue == 1:
            save = open(f"{directory_path}\{file_name}.txt", "x")
            save.write(string)
          path = os.path.join(f"{directory_path}\{file_name}.wav")
          os.remove(path)
    elif statues == 'offline':
      messagebox.showerror('Error', 'Error: Please check your connection')
    elif statues == "timeout":
      messagebox.showerror('Error', 'Connection timeout. Please try again later.')

  # Audio translation widgets
  ct.CTkLabel(audio_tr_win, text= "Type The File Path                    :", font=(None, 23)).place(x= 30, y= 30)
  ct.CTkLabel(audio_tr_win, text= "(mp4/wav/mp3)", font=(None, 17)).place(x= 235, y= 32)
  path_var = StringVar()
  entry_a = ct.CTkEntry(audio_tr_win, textvariable=path_var, width=260, height=30, font=(None, 15), corner_radius=15)
  entry_a.place(x= 30 , y= 75)
  ct.CTkButton(audio_tr_win, text= 'Locate', corner_radius=15, font=(None, 17), width=60, command=locate).place(x=300, y=75)
  ct.CTkLabel(audio_tr_win, text= "From:", font=(None, 20)).place(x= 35, y=125)
  ct.CTkLabel(audio_tr_win, text= "To:", font=(None, 20)).place(x= 215 , y= 125)
  from_lang_combo = ct.CTkComboBox(audio_tr_win, width= 90, corner_radius=15, values= from_lang_list)
  to_lang_combo= ct.CTkComboBox(audio_tr_win, width= 90, values= to_lang_list, corner_radius=15)
  from_lang_combo.place(x=97, y=125)
  to_lang_combo.place(x=252, y=125)
  radio_value2 = IntVar()
  radio_a2 = ct.CTkRadioButton(audio_tr_win, variable=radio_value2, value=1, text ="Save the translation in a txt file",corner_radius=15, font=(None, 20))
  radio_a2.place(x=35, y=180)
  radio_a3 = ct.CTkRadioButton(audio_tr_win, variable=radio_value2, value=2,text ="Save the translation in a srt file", corner_radius=15, font=(None, 20))
  radio_a3.place(x=35, y=215)
  ct.CTkButton(audio_tr_win, text="Translate", font=(None, 20), width= 190, height=40, corner_radius=15, command=audio_tr_winans).place(x= 270, y= 350)
  ct.CTkButton(audio_tr_win, text= 'Back', font=(None, 20), command=lambda: back(audio_tr_win), corner_radius=15, width=70).place(x=20, y= 400)
  ct.CTkLabel(audio_tr_win, text= "The Translation:", font=(None, 25,'bold')).place(x= 440, y=30 )
  tr_textbox = ct.CTkTextbox(audio_tr_win, width=280, height=230, font=(None, 21), corner_radius=15)
  tr_textbox.place(x= 400, y= 80)
  tr_textbox.configure(state="disabled")

# Image translation window
def openimagetr():
  one.withdraw() # Main withdraw
  # Window start
  image_tr_win = ct.CTkToplevel()
  image_tr_win.title("Image Translator")
  image_tr_win.geometry(f"{700}x{450}+{570}+{270}")
  image_tr_win.resizable(False, False)
  image_tr_win.iconbitmap("icon.ico")
  image_tr_win.protocol("WM_DELETE_WINDOW", closing)

  # Locate
  def locate():
    filepath = filedialog.askopenfilename(title= "Open a jpg/png file", filetypes=(("Image files", "*.jpg"), ("Image files", "*.png"), ("all files", "*.*")))
    path_var.set(filepath)

  def img_thread():
    threading.Thread(target = img_tr).start()
  # Image translation
  def img_tr():
    timeout = 1
    from_language = from_lang_combo.get()
    to_language = to_lang_combo.get()
    filepath = path_var.get()
    file_name = os.path.splitext(os.path.basename(filepath))[0]
    file_type = os.path.splitext(filepath)[1]
    if filepath.strip() == '':
      return messagebox.showerror('Error', 'Error: Please type the file path')
    elif not from_language in from_lang_list:
      return messagebox.showerror('Error', 'Please check the language you are translating from.')
    elif not to_language in to_lang_list:
      return messagebox.showerror('Error', 'Please check the language you are translating to.')
    else:
      if file_type != ".png" and file_type != ".jpg" and file_type != ".jpeg":
        messagebox.showerror("Error", "This format is not supported.")
      else:
        entry_a.configure(state="disabled")
        locate_btn.configure(state="disabled")
        from_lang_combo.configure(state="disabled")
        to_lang_combo.configure(state="disabled")
        radio_a2.configure(state="disabled")
        radio_a3.configure(state="disabled")
        tr_btn.configure(state="disabled")
        wait_lbl = ct.CTkLabel(image_tr_win, text= "Wait a moment...", font=(None, 15))
        wait_lbl.place(x= 313, y= 400)
        # Getting the text from the image
        def get_text(api_key):
          api_url = 'https://api.api-ninjas.com/v1/imagetotext'
          image_file_descriptor = open(filepath, 'rb')
          headers = {"X-Api-Key": api_key}
          files = {'image': image_file_descriptor}
          response = requests.post(api_url, files=files, headers=headers)
          text = response.json()
          string = ""
          print(text)
          for word in text:
              string += word['text'] + " "
          return string
      try: text = get_text(os.getenv("K+vwIRZM3NgfQP2nOBmZqg==0c3QxNHh4dbT9Hwr"))
      except TypeError: text = get_text(os.getenv("API_KEY2"))
      except: return messagebox.showerror("Sorry, an unexpected error has occured.")

      # Translating
      try: requests.head("http://www.google.com/", timeout=timeout)
      except requests.ConnectionError: return messagebox.showerror('Error', 'Please check your connection')
      except requests.exceptions.Timeout: return messagebox.showerror('Error', 'Connection timeout. Please try again later.')
      if from_language == "Auto": translation = translator.translate(text, dest=to_language).text
      else: translation = translator.translate(text, dest=to_language, src=from_language).text

      # Saving the translation
      tr_textbox.configure(state="normal")
      tr_textbox.delete("1.0", END)
      tr_textbox.insert(END, translation)
      tr_textbox.configure(state="disabled")
      directory_path = os.path.dirname(filepath)
      if radio_value2.get() == 1:
        with open(f"{directory_path}\{file_name}_translated.txt", "w", encoding="utf8") as file:
          file.write(translation)
      elif radio_value2.get() == 2:
        with open(f"{directory_path}\{file_name}_translated.txt", "w", encoding="utf8") as file:
          file.write(f"{text}\n\n{translation}")
      entry_a.configure(state="normal")
      locate_btn.configure(state="normal")
      from_lang_combo.configure(state="normal")
      to_lang_combo.configure(state="normal")
      radio_a2.configure(state="normal")
      radio_a3.configure(state="normal")
      tr_btn.configure(state="normal")
      wait_lbl.configure(text="")
    image_tr_win.bind('<Return>', lambda event: img_tr())

  # Image translation widgets
  ct.CTkLabel(image_tr_win, text= "Type The File Path (jpg/png):", font=(None, 25)).place(x= 30, y= 30)
  path_var = StringVar()
  entry_a = ct.CTkEntry(image_tr_win, textvariable=path_var, width=260, height=30, font=(None, 15), corner_radius=15)
  entry_a.place(x= 30 , y= 75)
  locate_btn = ct.CTkButton(image_tr_win, text= 'Locate', corner_radius=15, font=(None, 17), width=60, command=locate)
  locate_btn.place(x=300, y=75)
  ct.CTkLabel(image_tr_win, text= "From:", font=(None, 20)).place(x= 35, y=125)
  ct.CTkLabel(image_tr_win, text= "To:", font=(None, 20)).place(x= 215 , y= 125)
  from_lang_combo = ct.CTkComboBox(image_tr_win, width= 90, corner_radius=15, values= from_lang_list)
  to_lang_combo= ct.CTkComboBox(image_tr_win, width= 90, values= to_lang_list, corner_radius=15)
  from_lang_combo.place(x=97, y=125)
  to_lang_combo.place(x=252, y=125)
  radio_value2 = IntVar()
  radio_a2 = ct.CTkRadioButton(image_tr_win, variable=radio_value2, value=1, text ="Save the translation in a txt file",corner_radius=15, font=(None, 20))
  radio_a2.place(x=35, y=180)
  radio_a3 = ct.CTkRadioButton(image_tr_win, variable=radio_value2, value=2, text ="Save the original text and the\ntranslation in a txt file",corner_radius=15, font=(None, 20))
  radio_a3.place(x=35, y=215)
  tr_btn = ct.CTkButton(image_tr_win, text="Translate", font=(None, 20), width= 190, height=40, corner_radius=15, command=img_thread)
  tr_btn.place(x= 270, y= 350)
  ct.CTkButton(image_tr_win, text= 'Back', font=(None, 20), command=lambda: back(image_tr_win), corner_radius=15, width=70).place(x=20, y= 400)
  ct.CTkLabel(image_tr_win, text= "The Translation:", font=(None, 25,'bold')).place(x= 440, y=30 )
  tr_textbox = ct.CTkTextbox(image_tr_win, width=280, height=230, font=(None, 21), corner_radius=15)
  tr_textbox.place(x= 400, y= 80)
  tr_textbox.configure(state="disabled")

# History window
def openhistory():
  one.withdraw() # Main withdraw
  # Window start
  history_win = ct.CTkToplevel()
  history_win.title("Translation History")
  history_win.geometry(f"{700}x{450}+{570}+{270}")
  history_win.resizable(False, False)
  history_win.iconbitmap("icon.ico")
  history_win.protocol("WM_DELETE_WINDOW", closing)

  def delete_history():
    if os.path.isfile("history.db") == False:  messagebox.showerror("Error", "You didn't translate anything yet.")
    ask = messagebox.askokcancel("Are you sure?", "Your whole history will be deleted, you wanna continue?")
    if ask == True:
      try:
        with sqlite3.connect("history.db") as db:
          cursor = db.cursor()
          cursor.execute("DROP TABLE history")
          db.commit()
        history_textbox.configure(state="normal")
        history_textbox.delete("1.0", END)
        history_textbox.configure(state="disabled")
      except sqlite3.OperationalError:  messagebox.showerror("Error", "Your history is already cleared.")

  # History widgets
  history_textbox = ct.CTkTextbox(history_win, width=679, height=370, font=(None, 20), corner_radius=15)
  history_textbox.place(x= 10, y= 10)
  history_textbox.configure(state="disabled")
  ct.CTkButton(history_win, text= 'Back', font=(None, 20), command=lambda: back(history_win), corner_radius=15, width=70).place(x=20, y= 400)
  ct.CTkButton(history_win, text= 'Delete History', font=(None, 20), command=delete_history, corner_radius=15, width=70, fg_color="red").place(x=525, y= 400)

  # Show history
  if os.path.isfile("history.db") == False: return
  try:
    with sqlite3.connect("history.db") as db:
      cursor = db.cursor()
      cursor.execute("SELECT original, translation, time_stamp FROM history")
      data = cursor.fetchall()
    data = sorted(data, key=lambda x: x[2], reverse=True)
    for row in data:
      row = list(row)
      original = str(row[0]).replace("\n", "")
      translation = str(row[1])
      time_stamp = int(row[2])
      date = datetime.fromtimestamp(time_stamp).strftime("%B %d, %Y %I:%M %p")
      history_textbox.configure(state="normal")
      history_textbox.insert(END, f"{date} --- {original} = {translation}\n")
      history_textbox.configure(state="disabled")
    history_textbox.configure(state="disabled")
  except sqlite3.OperationalError: pass

# Other windows open buttons
ct.CTkButton(one, text="Translate File", font=(None, 18), width= 130, height=30, command=openfile_tr_win, corner_radius= 15).place(x=20, y= 310)
ct.CTkButton(one, text="Translate Image", font=(None, 18), width= 130, height=30, command=openimagetr, corner_radius= 15).place(x=20, y= 355)
ct.CTkButton(one, text="Translate Audio/Video", font=(None, 18), width= 130, height=30, command=openaudiotr , corner_radius= 15).place(x=20, y= 400)
ct.CTkButton(one, text="Translation History", font=(None, 18), width= 130, height=30, command=openhistory, corner_radius= 15).place(x=270, y= 400)

one.mainloop()
