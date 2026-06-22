import os
import tkinter as tk
from tkinter import filedialog, ttk
import vlc  # Professional pleyer drayveri


class CyberpunkCapCutPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("KIBER_PLEYER // CAPCUT_STYLE v12.0")
        self.root.geometry("1200x790")
        self.root.configure(bg="#0b0c10")  # Chuqur kiber qora fon

        # Dastur o'zgaruvchilari
        self.video_path = ""
        self.is_paused = True
        self.history_list = []
        self.current_speed = 1.0

        # VLC sozlamalari
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

        # Voqealarni kuzatish (Video aniq yonganda ma'lumotlarni yangilash uchun)
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerPlaying, self.on_video_playing)

        self.create_widgets()
        self.check_video_end()

    def create_widgets(self):
        # ------------------ ASOSIY BAAZA (CapCut split style) ------------------
        self.main_split = tk.Frame(self.root, bg="#0b0c10")
        self.main_split.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # CHAP TOMON: Video hududi
        self.video_container = tk.Frame(self.main_split, bg="#1f2833", bd=1, relief=tk.SOLID)
        self.video_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.video_container.pack_propagate(False)

        self.video_frame = tk.Frame(self.video_container, bg="black")
        self.video_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # O'NG TOMON: Tarix va Tezlik paneli
        self.right_panel = tk.Frame(self.main_split, bg="#1f2833", width=280, bd=1, relief=tk.SOLID)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.right_panel.pack_propagate(False)

        # Tarix sarlavhasi
        lbl_hist_title = tk.Label(self.right_panel, text="📁 KIBER_KLIPLAR", bg="#1f2833", fg="#45f3ff",
                                  font=("Impact", 13), pady=12)
        lbl_hist_title.pack(fill=tk.X)

        # Kliplar ro'yxati
        self.history_box = tk.Listbox(self.right_panel, bg="#0b0c10", fg="#c5a1ff", bd=0,
                                      selectbackground="#45f3ff", selectforeground="#0b0c10",
                                      highlightthickness=1, highlightbackground="#333", font=("Consolas", 10))
        self.history_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.history_box.bind("<Double-Button-1>", self.play_from_history)

        # TEZLIK BLOKI (Speed Boost)
        speed_box_frame = tk.Frame(self.right_panel, bg="#0b0c10", bd=1, relief=tk.SOLID, highlightbackground="#45f3ff")
        speed_box_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=15, ipady=8)

        speed_title = tk.Label(speed_box_frame, text="⚡ SPEED_BOOST", bg="#0b0c10", fg="#ff455b", font=("Impact", 10))
        speed_title.pack(pady=(5, 8))

        btn_grid_frame = tk.Frame(speed_box_frame, bg="#0b0c10")
        btn_grid_frame.pack()

        speeds = [0.5, 1.0, 1.5, 2.0]
        self.speed_buttons = {}
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]

        for idx, sp in enumerate(speeds):
            r, c = positions[idx]
            btn = tk.Button(btn_grid_frame, text=f"{sp}x", bg="#1f2833", fg="#45f3ff", bd=0,
                            width=10, pady=6, font=("Consolas", 9, "bold"),
                            activebackground="#45f3ff", activeforeground="#0b0c10",
                            cursor="hand2", command=lambda s=sp: self.change_speed(s))
            btn.grid(row=r, column=c, padx=5, pady=5)
            self.speed_buttons[sp] = btn

        self.speed_buttons[1.0].config(bg="#45f3ff", fg="#0b0c10")

        # ------------------ PASTKI MONITORING PANELI ------------------
        self.control_panel = tk.Frame(self.root, bg="#1f2833", bd=1, relief=tk.SOLID)
        self.control_panel.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))

        # O'RTADAGI ASOSIY TUGMALAR
        main_btn_frame = tk.Frame(self.control_panel, bg="#1f2833")
        main_btn_frame.pack(pady=12)

        # CHOOSE button
        self.btn_open = tk.Button(main_btn_frame, text="📁 CHOOSE", bg="#0b0c10", fg="#45f3ff", bd=1,
                                  relief=tk.SOLID, highlightbackground="#45f3ff", padx=15, pady=6,
                                  font=("Consolas", 9, "bold"), activebackground="#45f3ff", command=self.open_file)
        self.btn_open.pack(side=tk.LEFT, padx=15)

        # -10s BACK
        self.btn_back = tk.Button(main_btn_frame, text="⏪ -10s", bg="#0b0c10", fg="#ffffff", bd=0,
                                  padx=15, pady=6, font=("Consolas", 10, "bold"), activebackground="#ff455b",
                                  command=lambda: self.seek_video(-10000))
        self.btn_back.pack(side=tk.LEFT, padx=10)

        # ▶ PLAY / PAUSE
        self.btn_play = tk.Button(main_btn_frame, text="▶ PLAY", bg="#ff455b", fg="white", bd=0,
                                  padx=30, pady=8, font=("Impact", 11), activebackground="#45f3ff",
                                  activeforeground="black", command=self.toggle_play)
        self.btn_play.pack(side=tk.LEFT, padx=15)

        # +10s NEXT
        self.btn_forward = tk.Button(main_btn_frame, text="⏩ +10s", bg="#0b0c10", fg="#ffffff", bd=0,
                                     padx=15, pady=6, font=("Consolas", 10, "bold"), activebackground="#ff455b",
                                     command=lambda: self.seek_video(10000))
        self.btn_forward.pack(side=tk.LEFT, padx=10)

        # ENG PASTKI HOLAT VA VIDEO TEXNIK PARAMETRLARI SATRI
        secondary_frame = tk.Frame(self.control_panel, bg="#0b0c10", height=30)
        secondary_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Chap tomonda status
        self.lbl_status = tk.Label(secondary_frame, text="STATUS: READY // SPEED: 1.0X", bg="#0b0c10", fg="#45f3ff",
                                   font=("Consolas", 9, "bold"))
        self.lbl_status.pack(side=tk.LEFT, padx=15, pady=4)

        # O'ng tomonda Video Info (MB, FPS, FORMAT) uchun maxsus neon kiber widget
        self.lbl_video_info = tk.Label(secondary_frame, text="SIZE: -- MB | FPS: -- | TYPE: --", bg="#0b0c10",
                                       fg="#ff455b", font=("Consolas", 9, "bold"))
        self.lbl_video_info.pack(side=tk.RIGHT, padx=15, pady=4)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video fayllar", "*.mp4 *.mkv *.avi *.mov")])
        if file_path:
            self.play_video(file_path)

    def play_video(self, file_path):
        self.video_path = os.path.normpath(file_path)
        filename = os.path.basename(self.video_path)

        if self.video_path not in self.history_list:
            self.history_list.append(self.video_path)
            self.history_box.insert(tk.END, f" > {filename}")

        self.lbl_status.config(text=f"PLAYING: {filename[:25].upper()} // SPEED: 1.0X")

        media = self.vlc_instance.media_new(self.video_path)
        self.player.set_media(media)
        self.player.set_hwnd(self.video_frame.winfo_id())

        self.player.play()
        self.is_paused = False
        self.btn_play.config(text="⏸ PAUSE", bg="#45f3ff", fg="#0b0c10")
        self.change_speed(1.0)

    def on_video_playing(self, event):
        # Video oqimi boshlanishi bilan tezlikni o'rnatish va ma'lumotlarni yangilash
        self.root.after(50, lambda: self.player.set_rate(self.current_speed))
        self.root.after(200, self.update_video_details)

    def update_video_details(self):
        if not self.video_path:
            return
        try:
            # 1. Hajmini aniqlash (Megabaytda)
            file_size_bytes = os.path.getsize(self.video_path)
            file_size_mb = round(file_size_bytes / (1024 * 1024), 1)

            # 2. Formatini (kengaytmasini) aniqlash
            _, file_extension = os.path.splitext(self.video_path)
            file_format = file_extension.replace(".", "").upper()

            # 3. FPS ni aniqlash
            fps = self.player.get_fps()
            if fps <= 0:
                # Agar VLC videodan FPS ololmasa, metadata sinxronizatsiyasi uchun biroz kutib qayta urinamiz
                self.root.after(300, lambda: self.final_display(file_size_mb, file_format))
            else:
                self.lbl_video_info.config(text=f"SIZE: {file_size_mb} MB | FPS: {round(fps)} | TYPE: {file_format}")
        except Exception:
            self.lbl_video_info.config(text="INFO: METADATA ERROR")

    def final_display(self, size_mb, file_format):
        fps = self.player.get_fps()
        # Agar baribir 0 bo'lsa, xatolik ko'rsatmasdan eng ko'p tarqalgan 24 yoki 30 kadrni beramiz
        fps_display = round(fps) if fps > 0 else "24/30"
        self.lbl_video_info.config(text=f"SIZE: {size_mb} MB | FPS: {fps_display} | TYPE: {file_format}")

    def toggle_play(self):
        if not self.video_path:
            return
        if self.is_paused:
            self.player.play()
            self.is_paused = False
            self.btn_play.config(text="⏸ PAUSE", bg="#45f3ff", fg="#0b0c10")
        else:
            self.player.pause()
            self.is_paused = True
            self.btn_play.config(text="▶ PLAY", bg="#ff455b", fg="white")

    def seek_video(self, milliseconds):
        if self.video_path:
            current_time = self.player.get_time()
            self.player.set_time(current_time + milliseconds)

    def change_speed(self, speed):
        self.current_speed = speed
        self.player.set_rate(speed)

        if self.video_path:
            filename = os.path.basename(self.video_path)
            self.lbl_status.config(text=f"PLAYING: {filename[:20].upper()} // SPEED: {speed}X")
        else:
            self.lbl_status.config(text=f"STATUS: READY // SPEED: {speed}X")

        for sp, btn in self.speed_buttons.items():
            if sp == speed:
                btn.config(bg="#45f3ff", fg="#0b0c10")
            else:
                btn.config(bg="#1f2833", fg="#45f3ff")

    def play_from_history(self, event):
        try:
            index = self.history_box.curselection()[0]
            selected_video = self.history_list[index]
            self.play_video(selected_video)
        except IndexError:
            pass

    def check_video_end(self):
        if self.video_path and self.player.get_state() == vlc.State.Ended:
            self.player.stop()
            self.is_paused = True
            self.btn_play.config(text="▶ PLAY", bg="#ff455b", fg="white")
        self.root.after(1000, self.check_video_end)


if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('clam')
    app = CyberpunkCapCutPlayer(root)
    root.mainloop()