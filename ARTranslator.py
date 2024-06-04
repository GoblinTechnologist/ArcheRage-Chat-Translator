import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import json
import requests
import re
import configparser

# Initialize Google Translate translator
translator_url = "https://translate.googleapis.com/translate_a/single"
# Define color mappings based on message_info patterns
color_mappings = {
    r'Nation': "#8FB232",
    r'Trade': "#36F1CC",
    r'Raid': "#EB8B2D",
    r'Guild': "#659FFF",
    r'Party': "#6BEF80",
    r'Team': "#DEA8F4",
    r'Family': "#1FD857",
    r'Shout': "#F86C96",
    r'Trial': "#EFAA25",
    r'Commander': "#FF7D1D",
    r'Global': "#36F1CC",
    r'\b(\w+ to you|To \w+)$': "#EA6DDA",
}
# Define patterns for replacement
patterns = [
    (r'\|n(.+?)\|r', '{NAME}'),
    (r'\|A(.+?)\;', '{INSTANCE}'),
    (r'\|i(.+?)\;', '{LINK}')
]

# Dictionary to map language codes to full language names
language_code_to_name = {
    "af": "Afrikaans",
    "sq": "Albanian",
    "am": "Amharic",
    "ar": "Arabic",
    "hy": "Armenian",
    "az": "Azerbaijani",
    "eu": "Basque",
    "be": "Belarusian",
    "bn": "Bengali",
    "bs": "Bosnian",
    "bg": "Bulgarian",
    "ca": "Catalan",
    "ceb": "Cebuano",
    "ny": "Chichewa",
    "zh-CN": "Chinese (Simplified)",
    "zh-TW": "Chinese (Traditional)",
    "co": "Corsican",
    "hr": "Croatian",
    "cs": "Czech",
    "da": "Danish",
    "nl": "Dutch",
    "en": "English",
    "eo": "Esperanto",
    "et": "Estonian",
    "tl": "Filipino",
    "fi": "Finnish",
    "fr": "French",
    "fy": "Frisian",
    "gl": "Galician",
    "ka": "Georgian",
    "de": "German",
    "el": "Greek",
    "gu": "Gujarati",
    "ht": "Haitian Creole",
    "ha": "Hausa",
    "haw": "Hawaiian",
    "he": "Hebrew",
    "hi": "Hindi",
    "hmn": "Hmong",
    "hu": "Hungarian",
    "is": "Icelandic",
    "ig": "Igbo",
    "id": "Indonesian",
    "ga": "Irish",
    "it": "Italian",
    "ja": "Japanese",
    "jw": "Javanese",
    "kn": "Kannada",
    "kk": "Kazakh",
    "km": "Khmer",
    "rw": "Kinyarwanda",
    "ko": "Korean",
    "ku": "Kurdish (Kurmanji)",
    "ky": "Kyrgyz",
    "lo": "Lao",
    "la": "Latin",
    "lv": "Latvian",
    "lt": "Lithuanian",
    "lb": "Luxembourgish",
    "mk": "Macedonian",
    "mg": "Malagasy",
    "ms": "Malay",
    "ml": "Malayalam",
    "mt": "Maltese",
    "mi": "Maori",
    "mr": "Marathi",
    "mn": "Mongolian",
    "my": "Myanmar (Burmese)",
    "ne": "Nepali",
    "no": "Norwegian",
    "or": "Odia (Oriya)",
    "ps": "Pashto",
    "fa": "Persian",
    "pl": "Polish",
    "pt": "Portuguese",
    "pa": "Punjabi",
    "ro": "Romanian",
    "ru": "Russian",
    "sm": "Samoan",
    "gd": "Scots Gaelic",
    "sr": "Serbian",
    "st": "Sesotho",
    "sn": "Shona",
    "sd": "Sindhi",
    "si": "Sinhala",
    "sk": "Slovak",
    "sl": "Slovenian",
    "so": "Somali",
    "es": "Spanish",
    "su": "Sundanese",
    "sw": "Swahili",
    "sv": "Swedish",
    "tg": "Tajik",
    "ta": "Tamil",
    "tt": "Tatar",
    "te": "Telugu",
    "th": "Thai",
    "tr": "Turkish",
    "tk": "Turkmen",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "ug": "Uyghur",
    "uz": "Uzbek",
    "vi": "Vietnamese",
    "cy": "Welsh",
    "xh": "Xhosa",
    "yi": "Yiddish",
    "yo": "Yoruba",
    "zu": "Zulu"
}

# Create a reverse dictionary
language_codes = {name: code for code, name in language_code_to_name.items()}


# Function to get full language name from code
def get_language_name(code):
    return language_code_to_name.get(code, "Unknown Language")

chat_log_path = None
translated_lines = []
displayed_line = 0
def chat_line(channel, message_info, message_body, original_body, language="English"):
    return {
        "channel": channel,
        "message_info": message_info,
        "message_body": message_body,
        "original_body": original_body,
        "language": language
    }

# Function to get the path of the configuration file
def get_config_file_path():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(application_path, "config.txt")

# Function to load the configuration
def load_config():
    global chat_log_path  # Declare chat_log_path as global
    config_file_path = get_config_file_path()
    default_chat_log_path = os.path.join(os.path.expanduser('~'), 'Documents', 'ArcheRage', 'Chat.log')

    if os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r') as file:
                config = json.load(file)
                font_size_combobox.set(config.get('font_size', 12))
                change_font_size(None)
                selected_language.set(config.get('selected_language', "English"))
                opacity_slider.set(config.get('opacity', 1.0))
                chat_log_path = config.get('chat_log_path')
                previous_lines_var.set(config.get('previous_lines'))
                always_on_top_var.set(config.get('always_on_top', False))
                timestamp_var.set(config.get('timestamp'))
                original_var.set(config.get('show_original'))
                max_lines_var.set(config.get('max_lines'))
                window_width = config.get('window_width', 1024)
                window_height = config.get('window_height', 768)
                root.geometry(f'{window_width}x{window_height}')
                root.attributes("-topmost", always_on_top_var.get())
                root.attributes("-alpha", opacity_slider.get())
                if not chat_log_path or not os.path.exists(chat_log_path):
                    chat_log_path = default_chat_log_path if os.path.exists(default_chat_log_path) else None
                if chat_log_path:
                    load_chat_log(chat_log_path)
                for label, var in zip(checkbox_labels, checkbox_vars):
                    var.set(config.get(label, True))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
    else:
        chat_log_path = default_chat_log_path if os.path.exists(default_chat_log_path) else None
        for var in checkbox_vars:
            var.set(True)
        always_on_top_var.set(False)

    if chat_log_path:
        load_chat_log(chat_log_path)



# Function to save the configuration
def save_config():
    window_width = root.winfo_width()
    window_height = root.winfo_height()

    config = {
        'selected_language': selected_language.get(),
        'opacity': opacity_slider.get(),
        'chat_log_path': chat_log_path,
        'previous_lines': previous_lines_var.get(),
        'always_on_top': always_on_top_var.get(),
        'timestamp': timestamp_var.get(),
        'show_original': original_var.get(),
        'font_size': int(font_size_combobox.get()),
        'max_lines': max_lines_var.get(),
        'window_width': window_width,
        'window_height': window_height
    }
    for label, var in zip(checkbox_labels, checkbox_vars):
        config[label] = var.get()

    config_file_path = get_config_file_path()
    try:
        with open(config_file_path, 'w') as file:
            json.dump(config, file)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")


def load_chat_log(file_path):
    global chat_log_path, last_position, displayed_line, translated_lines
    
    target_size = previous_lines_var.get()
    CHUNK_SIZE = 1024*target_size  # Size of the chunk to read from the end of the file

    try:
        with open(file_path, 'rb') as file:
            file.seek(0, os.SEEK_END)
            end_position = file.tell()
            move_position = max(end_position - CHUNK_SIZE, 0)
            file.seek(move_position)
            
            buffer = file.read(CHUNK_SIZE)
            
            # Find the first newline from the beginning of the buffer
            if b'\n' in buffer:
                newline_pos = buffer.find(b'\n')
                last_position = move_position + newline_pos + 1
            else:
                # If no newline found, set to end of file
                last_position = end_position

        # Clear the text area before loading new lines
        displayed_line = 0
        translated_lines = []
        text_area.delete(1.0, tk.END)

        # Set background color of the text box to black
        text_area.config(bg="black")

    except Exception as e:
        messagebox.showerror("Error", "Failed to load chat log: " + str(e))
        last_position = 0  # Reset last_position in case of error

def remove_timestamp(line):
    # Find the position of the '[' character
    bracket_index = line.find('[')
    
    # Check if '[' was found
    if bracket_index != -1:
        # Slice the string from the '[' character to the end
        return line[bracket_index:]
    else:
        # If '[' is not found, return an appropriate message or handle as needed
        return line
        
# Function to check for new lines in the chat log
def check_new_lines():
    global last_position, displayed_line
    if chat_log_path:
        try:
            with open(chat_log_path, 'r', encoding='utf-8-sig', errors='replace') as file:
                file.seek(0, os.SEEK_END)
                end_position = file.tell()
                if end_position < last_position:
                    last_position = end_position
                file.seek(last_position)
                new_lines = file.readlines()
                for line in new_lines:
                    line_language = selected_language.get()
                    line = line.rstrip('\n')
                    separator_index = line.find(']:')
                    if separator_index != -1:
                        message_info = line[:separator_index + 2]
                        message_body = line[separator_index + 2:].strip()
                        for pattern, replacement in patterns:
                            message_body = re.sub(pattern, replacement, message_body)
                        original_message_info = message_info
                        match = re.search(r'\[([^:\]]+)(?=:|\])', message_info)
                        if match:
                            message_info = match.group(1)
                        translation_params = {
                            "client": "gtx",
                            "sl": "auto",
                            "tl": language_codes[selected_language.get()],
                            "dt": "t",
                            "q": message_body
                        }
                        try:
                            response = requests.get(translator_url, params=translation_params)
                            if response.status_code == 200:
                                translations = response.json()[0]
                                translated_body = ''.join(segment[0] for segment in translations if segment[0])
                                detected_language = response.json()[2]
                                translated_lines.append(chat_line(message_info, original_message_info, translated_body, message_body, language_code_to_name[detected_language]))
                        except Exception as e:
                            translated_lines.append(chat_line(message_info, original_message_info, message_body, message_body, selected_language.get()))
                            #translated_lines.append(chat_line(message_info, "", "Translation API request failed.", "", selected_language.get()))
                    elif not line.startswith("BackupNameAttachment"):
                        translated_lines.append(chat_line("Unknown", "", line, line, selected_language.get()))
                last_position = file.tell()
        except Exception as e:
            print("Error", f"Failed to check new lines: {e}")
    
    max_lines = max_lines_var.get()
    if max_lines > 0:
        while int(text_area.index('end-1c').split('.')[0]) > max_lines:
            text_area.delete("1.0", "2.0")
        while len(translated_lines) > max_lines:
            translated_lines.pop(0)
            displayed_line = max(displayed_line-1, 0)
    
    for newtext in translated_lines[displayed_line:]:
        line_visibility, text_color = determine_display_line(newtext["channel"])
        if line_visibility == True:
            body_tag = newtext["channel"]
            if newtext["language"] != selected_language.get():
                if original_var.get() == True:
                    insert_text(newtext["message_info"], newtext["original_body"], body_tag, text_color, body_tag, text_color)
                    insert_text(f'({newtext["language"]})', newtext["message_body"], "translated", "red", "translated", "red")
                else:
                    insert_text(f'{newtext["message_info"]} ({newtext["language"]})', newtext["message_body"], newtext["channel"], text_color, "translated", "red")
            else:
                insert_text(newtext["message_info"], newtext["message_body"], newtext["channel"], text_color, body_tag, text_color)

    displayed_line = len(translated_lines)
    root.after(100, check_new_lines)


# Function to insert text into the text area
def insert_text(info, body, info_tag, info_color, body_tag, body_color):
    if timestamp_var.get() == False:
        info = remove_timestamp(info)
    text_area.insert(tk.END, info + " ", (info_tag, 'line'))
    text_area.tag_config(info_tag, foreground=info_color)
    text_area.insert(tk.END, body + '\n', (body_tag, 'line'))
    text_area.tag_config(body_tag, foreground=body_color)
    text_area.see(tk.END)

# Function to insert error messages
def insert_error(error_message):
    text_area.insert(tk.END, error_message + '\n', ('error', 'line'))
    text_area.tag_config('error', foreground='red')
    text_area.see(tk.END)

# Funtion to determine line display and color
def determine_display_line(message_info):
    display_line = checkbox_vars[0].get()
    text_color = "#FFFFFF"  #

    if re.match(r'Raid', message_info):
        display_line = checkbox_vars[1].get()
        text_color = color_mappings.get(r'Raid', text_color)
    elif re.match(r'Commander', message_info):
        display_line = checkbox_vars[1].get()
        text_color = color_mappings.get(r'Commander', text_color)
    elif re.match(r'Party', message_info):
        display_line = checkbox_vars[2].get()
        text_color = color_mappings.get(r'Party', text_color)
    elif re.match(r'\b(\w+ to you|To \w+)$', message_info):
        display_line = checkbox_vars[3].get()
        text_color = color_mappings.get(r'\b(\w+ to you|To \w+)$', text_color)
    elif re.match(r'Guild', message_info):
        display_line = checkbox_vars[4].get()
        text_color = color_mappings.get(r'Guild', text_color)
    elif re.match(r'Nation', message_info):
        display_line = checkbox_vars[5].get()
        text_color = color_mappings.get(r'Nation', text_color)
    elif re.match(r'Shout', message_info):
        display_line = checkbox_vars[6].get()
        text_color = color_mappings.get(r'Shout', text_color)
    elif re.match(r'Trade', message_info):
        display_line = checkbox_vars[7].get()
        text_color = color_mappings.get(r'Trade', text_color)
    elif re.match(r'Team', message_info):
        display_line = checkbox_vars[8].get()
        text_color = color_mappings.get(r'Team', text_color)
    elif re.match(r'Family', message_info):
        display_line = checkbox_vars[9].get()
        text_color = color_mappings.get(r'Family', text_color)
    elif re.match(r'Trial', message_info):
        display_line = checkbox_vars[10].get()
        text_color = color_mappings.get(r'Trial', text_color)
    elif re.match(r'Global', message_info):
        display_line = checkbox_vars[11].get()
        text_color = color_mappings.get(r'Global', text_color)

    return display_line, text_color

# Function to handle opacity changes
def update_opacity(*args):
    root.attributes("-alpha", opacity_slider.get())

# Function to handle always on top checkbox
def update_always_on_top():
    root.attributes("-topmost", always_on_top_var.get())
    
# Function to handle font size changes
def change_font_size(event):
    new_font_size = int(font_size_combobox.get())
    text_area.config(font=("Helvetica", new_font_size))
    save_config()

# Function to handle window closing
def on_closing():
    save_config()
    root.destroy()

def on_resize(event):
    save_config()

def on_checkbox_change():
    global displayed_line
    displayed_line = 0
    text_area.delete(1.0, tk.END)
            
# Main GUI setup
# Apply dark mode colors
dark_bg = "#2e2e2e"
dark_fg = "#ffffff"
checkbox_bg = "#3c3c3c"
text_bg = "#1e1e1e"

# Create main window
root = tk.Tk()
root.title("ArcheRage Chat Translator (Goblin-tech)")

icon_image = tk.PhotoImage(data='''
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
''')
root.iconphoto(False, icon_image)

# Set default window size
root.geometry('1200x720')

# Apply dark mode to the main window
root.configure(bg=dark_bg)

# Configure ttk styles
style = ttk.Style()
style.theme_use('clam')
style.configure("TCombobox", fieldbackground=dark_bg, background=dark_bg, foreground=dark_fg, bordercolor="#333333", highlightbackground="#333333")
style.map('TCombobox', fieldbackground=[('readonly', dark_bg)], selectbackground=[('readonly', dark_bg)], selectforeground=[('readonly', dark_fg)])

# Function to toggle the options_frame
options_visible = True

def toggle_options():
    global options_visible
    if options_visible:
        options_frame.pack_forget()
        toggle_button.config(text="Show Options")
        options_visible = False
    else:
        text_frame.pack_forget()
        options_frame.pack(side=tk.TOP, fill=tk.X)
        text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        toggle_button.config(text="Hide Options")
        options_visible = True
        
        
toggle_frame = tk.Frame(root, bg=dark_bg)
toggle_frame.pack(side=tk.TOP, fill=tk.X)

# Frame to hold menu and checkboxes
options_frame = tk.Frame(root, bg=dark_bg)
options_frame.pack(side=tk.TOP, fill=tk.X)

toggle_button = tk.Button(toggle_frame, text="Hide Options", command=toggle_options, bg=dark_bg, fg=dark_fg)
toggle_button.pack(side=tk.LEFT)

# Create a frame for the top menu bar
menu_frame = tk.Frame(options_frame, bg=dark_bg)
menu_frame.pack(side=tk.TOP, fill=tk.X)

# Drop-down menu for language selection
languages = [name for code, name in language_code_to_name.items()]
selected_language = tk.StringVar()
selected_language.set("English")  # Set default value
def change_language(*args):
    # Clear the chatbox
    global displayed_line
    displayed_line = 0
    text_area.delete(1.0, tk.END)
    # Reload the chat log
    if chat_log_path and os.path.exists(chat_log_path):
        load_chat_log(chat_log_path)

# Bind the change_language function to the language selection event
selected_language.trace_add('write', change_language)


language_menu = ttk.Combobox(menu_frame, textvariable=selected_language, values=languages)
language_menu.pack(side=tk.LEFT)

# Opacity slider
opacity_label = tk.Label(menu_frame, text="Opacity:", bg=dark_bg, fg=dark_fg)
opacity_label.pack(side=tk.LEFT)

opacity_slider = tk.Scale(menu_frame, from_=0.5, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, bg=dark_bg, fg=dark_fg, troughcolor="#333333", highlightbackground="#333333", highlightcolor="#333333")
opacity_slider.set(1.0)  # Default opacity
opacity_slider.pack(side=tk.LEFT)

# Bind the update_opacity function to the slider's command option
opacity_slider.config(command=lambda val: update_opacity(opacity_slider.get()))

# Timestamp checkbox
timestamp_var = tk.BooleanVar()
timestamp_checkbox = tk.Checkbutton(menu_frame, variable=timestamp_var, bg=checkbox_bg, command=on_checkbox_change)
timestamp_checkbox.pack(side=tk.LEFT)
timestamp_label = tk.Label(menu_frame, text="Timestamps", bg=checkbox_bg, fg=dark_fg)
timestamp_label.pack(side=tk.LEFT)

# Original checkbox
original_var = tk.BooleanVar()
original_checkbox = tk.Checkbutton(menu_frame, variable=original_var, bg=checkbox_bg, command=on_checkbox_change)
original_checkbox.pack(side=tk.LEFT)
original_label = tk.Label(menu_frame, text="Show\nOriginal", bg=checkbox_bg, fg=dark_fg)
original_label.pack(side=tk.LEFT)

# Always on top checkbox
always_on_top_var = tk.BooleanVar()
always_on_top_checkbox = tk.Checkbutton(menu_frame, variable=always_on_top_var, bg=checkbox_bg)
always_on_top_checkbox.pack(side=tk.LEFT)
always_on_top_label = tk.Label(menu_frame, text="On Top", bg=checkbox_bg, fg=dark_fg)
always_on_top_label.pack(side=tk.LEFT)

# Bind the update_always_on_top function to the checkbox's command option
always_on_top_checkbox.config(command=update_always_on_top)

# File selector button
def select_chat_log():
    global chat_log_path  # Declare chat_log_path as global
    initial_dir = os.path.join(os.path.expanduser('~'), 'Documents', 'ArcheRage')
    file_path = filedialog.askopenfilename(initialdir=initial_dir, title="Set Chat.log",
                                            filetypes=(("Log files", "*.log"), ("All files", "*.*")))
    if file_path:
        chat_log_path = file_path  # Set chat_log_path globally
        load_chat_log(chat_log_path)
        save_config()

file_button = tk.Button(menu_frame, text="Select Chat.log", command=select_chat_log, bg=dark_bg, fg=dark_fg)
file_button.pack(side=tk.LEFT)

# Numeric input for previous lines using Spinbox
previous_lines_var = tk.IntVar()
previous_lines_label = tk.Label(menu_frame, text="Preload (kb):", bg=dark_bg, fg=dark_fg)
previous_lines_label.pack(side=tk.LEFT)

previous_lines_spinbox = tk.Spinbox(menu_frame, textvariable=previous_lines_var, from_=0, to=5, width=3)
previous_lines_spinbox.pack(side=tk.LEFT)
previous_lines_spinbox.config(bg=dark_bg, fg=dark_fg, insertbackground=dark_fg, buttonbackground=dark_bg)

# Bind the change_previous_lines function to the Spinbox value change event
previous_lines_spinbox.bind("<KeyRelease>", lambda e: validate_previous_lines())

def validate_previous_lines():
    # Get the current value
    try:
        value = previous_lines_var.get()
    except:
        # If the value is not an integer, set it to 0
        previous_lines_var.set(0)
        value = 0
    # Validate the value
    if value < 0:
        previous_lines_var.set(0)
    elif value > 5:
        previous_lines_var.set(5)
    save_config()

# Create a frame for additional checkboxes
checkbox_frame = tk.Frame(options_frame, bg=dark_bg)
checkbox_frame.pack(side=tk.TOP, fill=tk.X)

# List of checkbox labels
checkbox_labels = ["/s", "/r", "/p", "/w", "/g", "/n", "/sh", "/tr", "Team", "/fam", "Trial", "/u"]

# Map checkbox labels to color mappings
label_to_color = {
    "/s": "#FFFFFF",
    "/r": color_mappings[r'Raid'],
    "/p": color_mappings[r'Party'],
    "/w": color_mappings[r'\b(\w+ to you|To \w+)$'],
    "/g": color_mappings[r'Guild'],
    "/n": color_mappings[r'Nation'],
    "/sh": color_mappings[r'Shout'],
    "/tr": color_mappings[r'Trade'],
    "Team": color_mappings[r'Team'],
    "/fam": color_mappings[r'Family'],
    "Trial": color_mappings[r'Trial'],
    "/u": color_mappings[r'Global']
}

# Create and pack checkboxes with matching colors
checkbox_vars = []
for label in checkbox_labels:
    var = tk.BooleanVar()
    var.trace_add("write", lambda name, index, mode, var=var: on_checkbox_change())
    checkbox = tk.Checkbutton(checkbox_frame, variable=var, bg=checkbox_bg)
    checkbox.pack(side=tk.LEFT)
    lbl = tk.Label(checkbox_frame, text=label, bg=checkbox_bg, fg=label_to_color[label])
    lbl.pack(side=tk.LEFT)
    checkbox_vars.append(var)

# Text window for displaying text
text_frame = tk.Frame(root, bg=dark_bg)
text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

text_scroll = tk.Scrollbar(text_frame)
text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

text_area = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=text_scroll.set, bg=text_bg, fg=dark_fg)
text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

text_scroll.config(command=text_area.yview)

def change_font_size(event):
    new_font_size = int(font_size_combobox.get())
    text_area.config(font=("Helvetica", new_font_size))
    save_config()

# Font size selection
font_size_label = tk.Label(menu_frame, text="Font Size:", bg=dark_bg, fg=dark_fg)
font_size_label.pack(side=tk.LEFT)

# Options for font size
font_sizes = [8, 10, 12, 14, 16, 18, 20]  # You can adjust this list as needed

# Combobox for selecting font size
font_size_combobox = ttk.Combobox(menu_frame, values=font_sizes, width=3, state="readonly")
font_size_combobox.pack(side=tk.LEFT)
font_size_combobox.set(12)  # Set default font size

# Apply ttk style to the combobox
font_size_combobox.configure(style="TCombobox")

# Bind the change_font_size function to the combobox selection event
font_size_combobox.bind("<<ComboboxSelected>>", change_font_size)

max_lines_var = tk.IntVar()
max_lines_label = tk.Label(menu_frame, text="Max lines:\n(0 unlimited)", bg=dark_bg, fg=dark_fg)
max_lines_label.pack(side=tk.LEFT)

max_lines_spinbox = tk.Spinbox(menu_frame, textvariable=max_lines_var, increment=10, from_=0, to=200, width=3)
max_lines_spinbox.pack(side=tk.LEFT)
max_lines_spinbox.config(bg=dark_bg, fg=dark_fg, insertbackground=dark_fg, buttonbackground=dark_bg)

# Bind the change_previous_lines function to the Spinbox value change event
max_lines_spinbox.bind("<KeyRelease>", lambda e: validate_max_lines())

def validate_max_lines():
    # Get the current value
    try:
        value = max_lines_var.get()
    except:
        # If the value is not an integer, set it to 0
        max_lines_var.set(0)
        value = 0
    # Validate the value
    if value < 0:
        max_lines_var.set(0)
        
# Disable text editing but allow copying
text_area.bind("<KeyPress>", lambda e: "break")
text_area.bind("<Key>", lambda e: "break")

def on_resize(event):
    save_config()

root.bind('<Configure>', on_resize)

# Load configuration from file
load_config()

# Save configuration when closing the window
root.protocol("WM_DELETE_WINDOW", on_closing)

# Apply always on top setting
root.attributes("-topmost", always_on_top_var.get())

# Apply opacity setting
root.attributes("-alpha", opacity_slider.get())

# Bind resizing event
root.bind('<Configure>', on_resize)

# Run the application
root.after(400, check_new_lines)  # Start checking for new lines every second
root.mainloop()
