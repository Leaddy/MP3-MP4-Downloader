import tkinter as tk
from tkinter import ttk
import os
from pytube import YouTube
import re
import webbrowser
from tkinter import PhotoImage
import unicodedata


# YouTube stream_options ve video_qualities değişkenlerini burada tanımlayın
video_stream_options = []
video_qualities = []


def replace_invalid_characters_with_space(file_name):
    invalid_characters = '\\/:*?"<>|'  # Değiştirilecek karakterler listesi
    for char in invalid_characters:
        file_name = file_name.replace(char, ' ')  # Her bir karakteri boşlukla değiştir
    return file_name

def clean_video_title(title):
    # Başlıkta geçersiz karakterleri ve emojileri temizleyin
    cleaned_title = ''.join(c for c in title if c.isprintable())
    # Geçerli bir dosya adı oluşturmak için uygun karakterlere dönüştürün
    cleaned_title = unicodedata.normalize('NFKD', cleaned_title).encode('ASCII', 'ignore').decode('utf-8')
    return cleaned_title


def is_valid_youtube_link(link):
    # YouTube linkinin başlangıç kısmını kontrol et
    youtube_link_pattern = r'https?://(?:www\.)?youtube\.com/watch\?v='
    if not re.match(youtube_link_pattern, link):
        return False

    # YouTube video kimliğini çıkart
    video_id = link.split('v=')[1]

    # Video kimliğinin geçerli bir biçimde olup olmadığını kontrol et (11 karakterli)
    if not re.match(r'^[a-zA-Z0-9_-]{11}$', video_id):
        return False

    return True

download_folder = os.path.expanduser('~\\Downloads')

def update_quality_combobox(link, media_type):
    try:
        if link:
            yt = YouTube(link)
            if media_type == "MP4":
                global video_stream_options, video_qualities  # Bu değişkenleri kullanmak için global olarak tanımlayın
                video_stream_options = yt.streams.filter(file_extension="mp4", progressive=True).order_by('resolution').desc()
                video_qualities = [stream.resolution for stream in video_stream_options]
                quality_combo['values'] = video_qualities
                if video_qualities:
                    quality_combo.set(video_qualities[0])  # Varsayılan olarak ilk kaliteyi seçin
                else:
                    quality_combo.set("")  # Hiç kalite yoksa Combobox'ı boş bırakın
            else:
                quality_combo.set("")  # MP3 seçildiğinde kalite seçeneğini boş bırakın
    except Exception as e:
        result_label.config(text="Hata: " + str(e))
        quality_combo.set("")  # Hata durumunda Combobox'ı boş bırakın

def on_media_type_change(event):
    selected_media_type = media_type_combo.get()
    
    # MP3 seçildiyse kalite Combobox'ını temizle
    if selected_media_type == "MP3":
        quality_combo.set("")  # Kalite seçimini sıfırla
        quality_combo['values'] = []  # Kalite seçeneklerini temizle
    else:
        # MP4 seçildiyse kalite seçeneklerini güncelle
        quality_combo['values'] = video_qualities
    
    # Kalite Combobox'ını güncelle
    link = link_var.get()
    update_quality_combobox(link, selected_media_type)

def download_media(link, media_type, selected_quality):
    try:
        if not link:
            result_label.config(text="Lütfen bir YouTube linki girin.")
            return

        if not is_valid_youtube_link(link):
            result_label.config(text="Yanlış link girdiniz.")
            return
        result_label.config(text="İndiriliyor...")
        window.update()
        yt = YouTube(link)
        
        # Video başlığını temizle
        video_title = clean_video_title(yt.title)

        if media_type == "MP3":
            mp3_filename = video_title + ".mp3"
            mp3_filename = replace_invalid_characters_with_space(mp3_filename)
            mp3_path = os.path.join(download_folder, mp3_filename)

            if os.path.exists(mp3_path):
                result_label.config(text=f"{mp3_filename} zaten var.")
            else:
                mp3_stream = yt.streams.filter(only_audio=True).first()
                mp3_stream.download(output_path=download_folder, filename=mp3_filename)
                result_label.config(text=f"{mp3_filename} başarıyla indirildi!")

        elif media_type == "MP4":
            if not selected_quality:
                result_label.config(text="Lütfen bir kalite seçin.")
                return

            mp4_filename = video_title + f" ({selected_quality}).mp4"
            mp4_filename = replace_invalid_characters_with_space(mp4_filename)
            mp4_path = os.path.join(download_folder, mp4_filename)

            if os.path.exists(mp4_path):
                result_label.config(text=f"{mp4_filename} zaten var.")
            else:
                selected_stream = yt.streams.filter(res=selected_quality, file_extension="mp4", progressive=True).first()
                selected_stream.download(output_path=download_folder, filename=mp4_filename)
                result_label.config(text=f"{mp4_filename} başarıyla indirildi!")
        else:
            result_label.config(text="Belirtilen kalitede video bulunamadı.")

    except Exception as e:
        result_label.config(text="İndirme Hatası: " + str(e))




def validate_link_input(new_text):
    if len(new_text) > 200:
        result_label.config(text="Maksimum harf sayısını aştınız.")
        return False
    return True

def open_link(event):
    webbrowser.open("https://linktr.ee/leaddy")

# Tkinter penceresini oluştur
window = tk.Tk()

window.title("Medya İndirici    -Leaddy")
window.geometry("400x270")
window.resizable(width=False, height=False)
window.configure(bg="#339999")
download_icon = PhotoImage(file='C:/Windows/System32/@edptoastimage.png')
# Etiket ve giriş kutusu oluştur
link_label = tk.Label(window, text="İndirmek istediğiniz YouTube Linkini Girin:", bg="#339999")
link_label.pack(pady=2)
link_var = tk.StringVar()
link_entry = tk.Entry(window, width=50, textvariable=link_var)
link_entry.pack()

layout = tk.Frame(window)
layout.place(x=290, y=240)

label = tk.Label(layout, text="Coded By Leaddy", fg="red", cursor="hand2", bg="#339999")
label.grid()

# Etikete tıklanınca açılacak bağlantıyı tanımlayın
label.bind("<Button-1>", open_link)

# Kullanıcı girdilerini sınırlamak için doğrulama işlevi ekleyin
validate_link = window.register(validate_link_input)
link_entry.config(validate="key", validatecommand=(validate_link, "%P"))

# Medya türünü seçmek için Combobox oluştur
media_type_label = tk.Label(window, text="Medya Türünü Seçin:", bg="#339999")
media_type_label.pack(pady=2)
media_types = ["MP3", "MP4"]
media_type_combo = ttk.Combobox(window, values=media_types, state="readonly")
media_type_combo.set("MP3")
media_type_combo.pack()
media_type_combo.bind("<<ComboboxSelected>>", on_media_type_change)

# Kalite seçimi için Combobox oluştur
quality_label = tk.Label(window, text="Kalite Seçin:", bg="#339999")
quality_label.pack(pady=2)
quality_combo = ttk.Combobox(window, state="readonly")  # Başlangıçta boş olacak
quality_combo.pack()

# İndirme butonunu oluştur
download_button = ttk.Button(window, text="İndir", command=lambda: download_media(link_var.get(), media_type_combo.get(), quality_combo.get()))
download_button.pack(pady=31)

# Sonuç etiketi
result_label = tk.Label(window, text="", bg="#339999")
result_label.pack(pady=5)

def open_downloads_folder():
    webbrowser.open(download_folder)


open_folder_button = tk.Button(window, image=download_icon, command=open_downloads_folder, bg="#339999")
open_folder_button.config(text='',)
open_folder_button.place(x=300, y=150)

# Bağlantı güncellendiğinde kalite Combobox'ını güncelle
link_var.trace_add("write", lambda name, index, mode, sv=link_var: update_quality_combobox(sv.get(), media_type_combo.get()))

# Pencereyi görüntüle
window.mainloop()
