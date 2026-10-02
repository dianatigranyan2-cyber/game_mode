import tkinter as tk
from tkinter import ttk, scrolledtext
import datetime
import threading
from pynput import keyboard

from miner_engine import MiningEngine

class AutoMinerGUI:
    """Modern Dark-Mode GUI for Minecraft 1.21 Auto-Miner"""

    BG_COLOR = "#181825"
    CARD_BG = "#1e1e2e"
    FRAME_BORDER = "#313244"
    TEXT_COLOR = "#cdd6f4"
    SUBTEXT_COLOR = "#a6adc8"
    ACCENT_COLOR = "#cba6f7"
    GREEN_COLOR = "#a6e3a1"
    RED_COLOR = "#f38ba8"
    YELLOW_COLOR = "#f9e2af"

    PRESETS = {
        "Нетерит/Алмаз (Эфф V) - 0.35с": 0.35,
        "Алмазная кирка - 0.45с": 0.45,
        "Железная кирка - 0.60с": 0.60,
        "Каменная кирка - 0.90с": 0.90,
        "Деревянная кирка - 1.20с": 1.20,
    }

    def __init__(self, root):
        self.root = root
        self.root.title("⛏ Minecraft 1.21 Auto-Miner v1.0")
        self.root.geometry("640x720")
        self.root.configure(bg=self.BG_COLOR)
        self.root.resizable(False, False)

        # Initialize Mining Engine
        self.engine = MiningEngine(
            status_callback=self._async_log,
            count_callback=self._async_update_count
        )

        self._setup_styles()
        self._build_ui()

        # Start Global Hotkey Listener
        self.hotkey_listener = keyboard.Listener(on_press=self._on_global_key_press)
        self.hotkey_listener.daemon = True
        self.hotkey_listener.start()

        self.log("🚀 Приложение запущено. Нажмите F6 для старта/паузы, F7 для стопа.")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure(".", background=self.BG_COLOR, foreground=self.TEXT_COLOR, font=("Segoe UI", 10))
        style.configure("TLabel", background=self.CARD_BG, foreground=self.TEXT_COLOR)
        style.configure("Header.TLabel", background=self.BG_COLOR, foreground=self.ACCENT_COLOR, font=("Segoe UI Bold", 16))
        style.configure("SubHeader.TLabel", background=self.BG_COLOR, foreground=self.SUBTEXT_COLOR, font=("Segoe UI", 9))
        
        style.configure("TLabelframe", background=self.CARD_BG, foreground=self.ACCENT_COLOR, bordercolor=self.FRAME_BORDER, relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=self.CARD_BG, foreground=self.ACCENT_COLOR, font=("Segoe UI Bold", 11))
        
        style.configure("TCheckbutton", background=self.CARD_BG, foreground=self.TEXT_COLOR)
        style.map("TCheckbutton", background=[('active', self.CARD_BG)])

    def _build_ui(self):
        # 1. Header Frame
        header_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        header_frame.pack(fill="x", padx=20, pady=15)

        title_label = ttk.Label(header_frame, text="⛏ MINECRAFT 1.21 AUTO-MINER", style="Header.TLabel")
        title_label.pack(anchor="w")

        sub_label = ttk.Label(header_frame, text="Автоматическая копка туннелей, факелы, еда и DirectInput для 1.21", style="SubHeader.TLabel")
        sub_label.pack(anchor="w")

        # 2. Status & Statistics Bar
        status_bar = tk.Frame(self.root, bg=self.CARD_BG, highlightbackground=self.FRAME_BORDER, highlightthickness=1)
        status_bar.pack(fill="x", padx=20, pady=5)

        self.lbl_status = tk.Label(status_bar, text="СТАТУС: ГОТОВ", bg=self.CARD_BG, fg=self.GREEN_COLOR, font=("Segoe UI Bold", 11))
        self.lbl_status.pack(side="left", padx=15, pady=10)

        self.lbl_count = tk.Label(status_bar, text="Добыто блоков: 0", bg=self.CARD_BG, fg=self.ACCENT_COLOR, font=("Segoe UI Bold", 11))
        self.lbl_count.pack(side="right", padx=15, pady=10)

        # 3. Settings Container
        settings_frame = ttk.LabelFrame(self.root, text=" ⚙️ Настройки Копания ")
        settings_frame.pack(fill="x", padx=20, pady=10)

        # Row 1: Mode & Preset Pickaxe
        r1 = tk.Frame(settings_frame, bg=self.CARD_BG)
        r1.pack(fill="x", padx=10, pady=5)

        tk.Label(r1, text="Режим работы:", bg=self.CARD_BG, fg=self.TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=2)
        self.combo_mode = ttk.Combobox(r1, values=["Туннель 2x1 (Прямой)", "АФК Автокликер"], state="readonly", width=24)
        self.combo_mode.current(0)
        self.combo_mode.grid(row=0, column=1, padx=10, pady=2)

        tk.Label(r1, text="Тип Кирки:", bg=self.CARD_BG, fg=self.TEXT_COLOR).grid(row=0, column=2, sticky="w", pady=2)
        self.combo_preset = ttk.Combobox(r1, values=list(self.PRESETS.keys()), state="readonly", width=26)
        self.combo_preset.current(1)
        self.combo_preset.grid(row=0, column=3, padx=10, pady=2)
        self.combo_preset.bind("<<ComboboxSelected>>", self._on_preset_change)

        # Row 2: Custom Dig Delay & Start Countdown
        r2 = tk.Frame(settings_frame, bg=self.CARD_BG)
        r2.pack(fill="x", padx=10, pady=5)

        tk.Label(r2, text="Задержка копания (сек):", bg=self.CARD_BG, fg=self.TEXT_COLOR).grid(row=0, column=0, sticky="w", pady=2)
        self.ent_dig_delay = ttk.Entry(r2, width=10)
        self.ent_dig_delay.insert(0, "0.45")
        self.ent_dig_delay.grid(row=0, column=1, padx=10, pady=2, sticky="w")

        tk.Label(r2, text="Отсчет перед стартом (сек):", bg=self.CARD_BG, fg=self.TEXT_COLOR).grid(row=0, column=2, sticky="w", pady=2)
        self.ent_start_delay = ttk.Entry(r2, width=10)
        self.ent_start_delay.insert(0, "5")
        self.ent_start_delay.grid(row=0, column=3, padx=10, pady=2, sticky="w")

        # Row 3: Torches Settings
        r3 = tk.Frame(settings_frame, bg=self.CARD_BG)
        r3.pack(fill="x", padx=10, pady=5)

        self.var_torches = tk.BooleanVar(value=True)
        chk_torches = ttk.Checkbutton(r3, text="Ставить факелы каждые", variable=self.var_torches)
        chk_torches.grid(row=0, column=0, sticky="w")

        self.ent_torch_int = ttk.Entry(r3, width=6)
        self.ent_torch_int.insert(0, "10")
        self.ent_torch_int.grid(row=0, column=1, padx=5)

        tk.Label(r3, text="блоков. Слот:", bg=self.CARD_BG, fg=self.TEXT_COLOR).grid(row=0, column=2, sticky="w")
        self.combo_torch_slot = ttk.Combobox(r3, values=["Вторая рука (F)", "Слот 9", "Слот 8", "Слот 7"], state="readonly", width=16)
        self.combo_torch_slot.current(0)
        self.combo_torch_slot.grid(row=0, column=3, padx=5)

        # Row 4: Food Settings
        r4 = tk.Frame(settings_frame, bg=self.CARD_BG)
        r4.pack(fill="x", padx=10, pady=5)

        self.var_food = tk.BooleanVar(value=True)
        chk_food = ttk.Checkbutton(r4, text="Авто-еда каждые", variable=self.var_food)
        chk_food.grid(row=0, column=0, sticky="w")

        self.ent_food_int = ttk.Entry(r4, width=6)
        self.ent_food_int.insert(0, "180")
        self.ent_food_int.grid(row=0, column=1, padx=5)

        tk.Label(r4, text="секунд. Слот еды:", bg=self.CARD_BG, fg=self.TEXT_COLOR).grid(row=0, column=2, sticky="w")
        self.combo_food_slot = ttk.Combobox(r4, values=["Слот 8", "Слот 7", "Слот 9"], state="readonly", width=16)
        self.combo_food_slot.current(0)
        self.combo_food_slot.grid(row=0, column=3, padx=5)

        # 4. Action Control Buttons Frame
        btn_frame = tk.Frame(self.root, bg=self.BG_COLOR)
        btn_frame.pack(fill="x", padx=20, pady=10)

        self.btn_start = tk.Button(btn_frame, text="▶ СТАРТ (F6)", bg="#27a745", fg="white", font=("Segoe UI Bold", 11), activebackground="#218838", relief="flat", command=self.action_start)
        self.btn_start.pack(side="left", expand=True, fill="x", padx=5)

        self.btn_pause = tk.Button(btn_frame, text="⏸ ПАУЗА (F6)", bg="#ffc107", fg="black", font=("Segoe UI Bold", 11), activebackground="#e0a800", relief="flat", command=self.action_pause)
        self.btn_pause.pack(side="left", expand=True, fill="x", padx=5)

        self.btn_stop = tk.Button(btn_frame, text="⏹ СТОП (F7)", bg="#dc3545", fg="white", font=("Segoe UI Bold", 11), activebackground="#c82333", relief="flat", command=self.action_stop)
        self.btn_stop.pack(side="left", expand=True, fill="x", padx=5)

        # 5. Real-time Console Log Frame
        log_frame = ttk.LabelFrame(self.root, text=" 📜 Лог Работы ")
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.txt_log = scrolledtext.ScrolledText(log_frame, bg="#11111b", fg=self.TEXT_COLOR, font=("Consolas", 9), insertbackground="white", relief="flat")
        self.txt_log.pack(fill="both", expand=True, padx=5, pady=5)

    def _on_preset_change(self, event):
        val = self.combo_preset.get()
        if val in self.PRESETS:
            self.ent_dig_delay.delete(0, tk.END)
            self.ent_dig_delay.insert(0, str(self.PRESETS[val]))

    def _apply_engine_config(self):
        try:
            self.engine.dig_delay = float(self.ent_dig_delay.get())
            self.engine.start_delay = int(self.ent_start_delay.get())
            
            mode_str = self.combo_mode.get()
            if "Туннель" in mode_str:
                self.engine.mode = MiningEngine.MODE_TUNNEL_2X1
            else:
                self.engine.mode = MiningEngine.MODE_AUTOCLICKER

            self.engine.enable_torches = self.var_torches.get()
            self.engine.torch_interval = int(self.ent_torch_int.get())
            torch_val = self.combo_torch_slot.get()
            if "F" in torch_val:
                self.engine.torch_slot = 'f'
            else:
                self.engine.torch_slot = torch_val.split()[-1]

            self.engine.enable_food = self.var_food.get()
            self.engine.food_interval = int(self.ent_food_int.get())
            self.engine.food_slot = self.combo_food_slot.get().split()[-1]

        except ValueError as e:
            self.log(f"⚠️ Ошибка параметров настройки: {e}")

    def action_start(self):
        if self.engine.is_running():
            if self.engine.is_paused():
                self.engine.pause()
                self.lbl_status.config(text="СТАТУС: КОПАЕМ", fg=self.GREEN_COLOR)
            return
        
        self._apply_engine_config()
        self.lbl_status.config(text="СТАТУС: ОТСЧЕТ...", fg=self.YELLOW_COLOR)
        self.engine.start()

    def action_pause(self):
        if self.engine.is_running():
            self.engine.pause()
            if self.engine.is_paused():
                self.lbl_status.config(text="СТАТУС: ПАУЗА", fg=self.YELLOW_COLOR)
            else:
                self.lbl_status.config(text="СТАТУС: КОПАЕМ", fg=self.GREEN_COLOR)

    def action_stop(self):
        self.engine.stop()
        self.lbl_status.config(text="СТАТУС: ОСТАНОВЛЕН", fg=self.RED_COLOR)

    def _on_global_key_press(self, key):
        try:
            if key == keyboard.Key.f6:
                if not self.engine.is_running():
                    self.root.after(0, self.action_start)
                else:
                    self.root.after(0, self.action_pause)
            elif key in (keyboard.Key.f7, keyboard.Key.esc):
                self.root.after(0, self.action_stop)
        except Exception:
            pass

    def _async_log(self, msg: str):
        self.root.after(0, self.log, msg)

    def _async_update_count(self, count: int):
        self.root.after(0, lambda: self.lbl_count.config(text=f"Добыто блоков: {count}"))

    def log(self, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.txt_log.insert(tk.END, f"[{now}] {msg}\n")
        self.txt_log.see(tk.END)
