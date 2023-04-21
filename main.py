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
from_lang_list = ["Auto", "Arabic", "German", "English", "French"]
from_lang_combo = ct.CTkComboBox(one, width= 90, values= from_lang_list, corner_radius=15)
from_lang_combo.place(x= 170, y= 237)
to_lang_list = ["Arabic", "German", "English", "French"]
to_lang_combo = ct.CTkComboBox(one, width= 90, values= to_lang_list, corner_radius= 15)
to_lang_combo.place(x= 465, y= 237)
one.bind('<Return>', lambda event: translate())

# On closing the app
def closing():
  if messagebox.askokcancel("Exit", "Are you sure you want to exit?"):
    one.destroy()
one.protocol("WM_DELETE_WINDOW", closing)



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

  if statues == "online":
    if from_language == "Auto":
      tran = translator.translate(word, dest=to_language)
    else:
      tran = translator.translate(word, dest=to_language, src=from_language)
    if tran.text == word:
        messagebox.showerror('Error', 'Please check your text or language selection.')
    else:
      to_tr_textbox.configure(state="normal")
      to_tr_textbox.delete("1.0", END)
      to_tr_textbox.insert(END, tran.text)
      to_tr_textbox.configure(state="disabled")
  elif statues == "offline":
    messagebox.showerror('Error', 'Error: Please check your connection')
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

  # On back button
  def back():
    one.deiconify()
    file_tr_win.withdraw()

  def locate_txt():
    filepath = filedialog.askopenfilename(title= "Open a text file", filetypes=(("text files", "*.txt") , ("all files", "*.*")))
    file_path_var.set(filepath)

  # File translation function
  def tr_file():
    print(radio_value.get())
    timeout = 1
    from_language = from_lang_combo.get()
    to_language = to_lang_combo.get()
    filepath = file_path_var.get()
    if filepath.strip() == '':
      return messagebox.showerror('Error', 'Error: Please type the file path')
    elif not from_language in from_lang_list:
      return messagebox.showerror('Error', 'Please check the language you are translating from.')
    elif not to_language in to_lang_list:
      return messagebox.showerror('Error', 'Please check the language you are translating to.')
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
          if choice_value == 0:
            tr_textbox.configure(state="normal")
            tr_textbox.delete("1.0", END)
            tr_textbox.insert(END, string)
            tr_textbox.configure(state="disabled")
          elif choice_value == 1:
            with open(f"{file_name}_translated.{file_type}", "w", encoding="utf8") as file:
              file.write(string)
          elif choice_value == 2:
            data.write(f"\n\n{string}")
          elif choice_value == 3:
            with open(filepath, "w", encoding="utf8") as file:
              file.truncate(0)
              file.write(string)
        elif statues == "offline":
          return messagebox.showerror('Error', 'Error: Please check your connection')
      messagebox.showinfo('Done', 'File is translated.')
  file_tr_win.bind('<Return>', lambda event: tr_file())

  # File translation window widgets
  ct.CTkLabel(file_tr_win, text= "Type The File Path (txt):", font=(None, 25)).place(x= 30, y= 30)
  file_path_var = StringVar()
  file_path_entry = ct.CTkEntry(file_tr_win, textvariable=file_path_var, width=260, height=30, font=(None, 15), corner_radius=15)
  file_path_entry.place(x= 30 , y= 75)
  ct.CTkButton(file_tr_win, text= 'Locate', corner_radius=15, font=(None, 17), width=60, command=locate_txt).place(x=300, y=75)
  ct.CTkLabel(file_tr_win, text= "From:", font=(None, 20)).place(x= 40, y=130)
  ct.CTkLabel(file_tr_win, text= "To:", font=(None, 20)).place(x= 220 , y= 130)
  from_lang_list = ["Auto" ,"Arabic", "German", "English", "French"]
  from_lang_combo = ct.CTkComboBox(file_tr_win, width= 90, corner_radius=15, values= from_lang_list)
  from_lang_combo.place(x=100, y=130)
  to_lang_list = ["Arabic", "German", "English", "French"]
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
  ct.CTkButton(file_tr_win, text= 'Back', font=(None, 20), command=back, corner_radius=15, width=70).place(x=20, y= 400)
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

  # On back button
  def back():
    one.deiconify()
    audio_tr_win.withdraw()

  def locate():
    filepath = filedialog.askopenfilename(title= "Open a wav/mp4 file", filetypes=(("Video files", "*.mp4"), ("Audio files", "*.wav"),("Audio files", "*.mp3"), ("all files", "*.*")))
    path_var.set(filepath)

  # Audio translation function
  def audio_tr_winans():
    r = sr.Recognizer()
    timeout = 1
    try:
      requests.head("http://www.google.com/", timeout=timeout)
      statues = "online"
    except requests.ConnectionError:
      statues= "offline"
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
      file_name = os.path.basename(filepath)
      file_type = file_name.split(".")[-1].strip()
      if file_type == "mp4":
          pass
      elif file_type == "wav":
          pass
      elif file_type == "mp3":
          pass
      else:
          return messagebox.showerror('Error', 'File format is not supported.')
      if file_type == "mp3":
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
          audio_tr_win.withdraw()
          show_tr(string)
          if checkbox_a2.get() == 1:
            save = open(f"{sfile[0]}.txt", "x")
            save.write(string)
      if file_type == "wav":
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
          audio_tr_win.withdraw()
          show_tr(string)
          if checkbox_a2.get() == 1:
            save = open(f"{sfile[0]}.txt", "x")
            save.write(string)

      elif file_type == "mp4":
        videof = file_name
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
          audio_tr_win.withdraw()
          show_tr(string)
          if checkbox_a2.get() == 1:
            save = open(f"{sfile[0]}.txt", "x")
            save.write(string)
        path = os.path.join(f"{sfile[0]}.wav")
        os.remove(path)
    elif statues == 'offline':
      messagebox.showerror('Error', 'Error: Please check your connection')

  # Audio translation widgets
  ct.CTkLabel(audio_tr_win, text= "Type The File Path                    :", font=(None, 25)).place(x= 30, y= 30)
  ct.CTkLabel(audio_tr_win, text= "(mp4/wav/mp3)", font=(None, 18)).place(x= 250, y= 32)
  path_var = StringVar()
  entry_a = ct.CTkEntry(audio_tr_win, textvariable=path_var, width=430, height=30, font=(None, 21), corner_radius=15)
  entry_a.place(x= 30 , y= 75)
  ct.CTkButton(audio_tr_win, text= 'Locate', corner_radius=15, font=(None, 17), width=60, command=locate).place(x=470, y=75)
  ct.CTkLabel(audio_tr_win, text= "From:", font=(None, 20)).place(x= 30, y=120)
  ct.CTkLabel(audio_tr_win, text= "To:", font=(None, 20)).place(x= 210 , y= 120)
  from_lang_list = ["Auto", "Arabic", "German", "English", "French"]
  from_lang_combo = ct.CTkComboBox(audio_tr_win, width= 90, corner_radius=15, values= from_lang_list)
  to_lang_list = ["Arabic", "German", "English", "French"]
  to_lang_combo= ct.CTkComboBox(audio_tr_win, width= 90, values= to_lang_list, corner_radius=15)
  from_lang_combo.place(x=95, y=120)
  to_lang_combo.place(x=250, y=120)
  checkbox_a2 = ct.CTkCheckBox(audio_tr_win, text ="Save the audio translation", corner_radius=15, font=(None, 16))
  checkbox_a2.place(x=380, y=120)
  ct.CTkButton(audio_tr_win, text="Translate", font=(None, 20), width= 190, height=40, corner_radius=15, command=audio_tr_winans).place(x= 270, y= 350)
  ct.CTkButton(audio_tr_win, text= 'Back', font=(None, 20), command=back, corner_radius=15, width=70).place(x=20, y= 400)

# Other windows open buttons
ct.CTkButton(one, text="Translate File", font=(None, 18), width= 130, height=30, command=openfile_tr_win, corner_radius= 15).place(x=20, y= 357)
ct.CTkButton(one, text="Translate Audio/Video", font=(None, 18), width= 130, height=30, command=openaudiotr , corner_radius= 15).place(x=20, y= 400)

# Show translation window
def show_tr(translation):
  # Window start
  show_tr_win = ct.CTkToplevel()
  show_tr_win.title("Translator show")
  show_tr_win.geometry(f"{700}x{450}+{570}+{270}")
  show_tr_win.resizable(True, False)

  # On back button
  def back():
    one.deiconify()
    show_tr_win.withdraw()

  # Show translation widgets
  label_show1 = ct.CTkLabel(show_tr_win, text= "", font=(None, 21))
  label_show2 = ct.CTkLabel(show_tr_win, text= "Translation :", font=(None, 23))
  label_show2.place(x= 30, y= 60)
  button_show = ct.CTkButton(show_tr_win, text= 'Back', font=(None, 20), command=back, width=70)
  button_show.place(x= 20, y=155)
  scroll_v = Scrollbar(show_tr_win)
  scroll_v.pack(side= RIGHT, fill="y")
  scroll_h = Scrollbar(show_tr_win, orient= HORIZONTAL)
  scroll_h.pack(side= BOTTOM, fill= "x")
  text = Text(show_tr_win, height= 500, width= 350, yscrollcommand= scroll_v.set, 
  xscrollcommand = scroll_h.set, wrap= NONE, font= ('Helvetica 15'))
  text.pack(fill = BOTH, expand=0)
  text.insert(END, translation)
  scroll_h.config(command = text.xview)
  scroll_v.config(command = text.yview)


one.mainloop()
