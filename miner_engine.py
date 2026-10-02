import threading
import time
from inputs import DirectInputController

class MiningEngine:
    """Threaded Mining Logic Engine for Minecraft 1.21 Auto-Miner"""

    MODE_TUNNEL_2X1 = "TUNNEL_2X1"
    MODE_AUTOCLICKER = "AUTOCLICKER"

    def __init__(self, status_callback=None, count_callback=None):
        self.status_callback = status_callback
        self.count_callback = count_callback
        
        self._thread = None
        self._running = False
        self._paused = False
        self._stop_event = threading.Event()

        # Configuration settings
        self.mode = self.MODE_TUNNEL_2X1
        self.dig_delay = 0.45       # Time in seconds to mine one block
        self.walk_delay = 0.28      # Time in seconds to step forward
        self.start_delay = 5        # Countdown seconds before start

        # Torch settings
        self.enable_torches = True
        self.torch_interval = 10    # Place torch every N blocks (default 10)
        self.torch_slot = 'f'       # 'f' for offhand, or '1'-'9'
        self.pickaxe_slot = '1'     # Default pickaxe slot

        # Food settings
        self.enable_food = True
        self.food_interval = 180    # Eat food every N seconds
        self.food_slot = '8'        # Hotbar slot for food

        # State tracking
        self.blocks_mined = 0
        self.last_eat_time = 0

    def log(self, message: str):
        if self.status_callback:
            self.status_callback(message)

    def update_count(self, count: int):
        if self.count_callback:
            self.count_callback(count)

    def is_running(self):
        return self._running

    def is_paused(self):
        return self._paused

    def start(self):
        if self._running:
            return
        self._running = True
        self._paused = False
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_wrapper, daemon=True)
        self._thread.start()

    def pause(self):
        if self._running:
            self._paused = not self._paused
            status = "ПАУЗА" if self._paused else "ВОЗОБНОВЛЕНО"
            self.log(f"⏸ Состояние: {status}")
            if self._paused:
                DirectInputController.release_all()

    def stop(self):
        if not self._running:
            return
        self.log("🛑 Остановка процесса копания...")
        self._stop_event.set()
        self._running = False
        self._paused = False
        DirectInputController.release_all()

    def _sleep_check(self, seconds: float) -> bool:
        """Sleep in small increments to allow rapid cancellation and pause handling."""
        end_time = time.time() + seconds
        while time.time() < end_time:
            if self._stop_event.is_set():
                return False
            while self._paused:
                if self._stop_event.is_set():
                    return False
                time.sleep(0.1)
            time.sleep(0.02)
        return True

    def _run_wrapper(self):
        try:
            self.log(f"⏳ Отсчет запуск {self.start_delay} сек... Переключитесь на Minecraft!")
            for i in range(self.start_delay, 0, -1):
                if self._stop_event.is_set():
                    self.log("🛑 Запуск отменен.")
                    return
                self.log(f"⏱ До старта: {i} сек...")
                time.sleep(1)

            if self._stop_event.is_set():
                return

            self.log("⛏ СТАРТ! Начинаем копать...")
            self.last_eat_time = time.time()

            if self.mode == self.MODE_TUNNEL_2X1:
                self._tunnel_2x1_loop()
            elif self.mode == self.MODE_AUTOCLICKER:
                self._autoclicker_loop()
        except Exception as e:
            self.log(f"⚠️ Ошибка выполнения: {e}")
        finally:
            self._running = False
            DirectInputController.release_all()
            self.log("✅ Процесс завершен/остановлен.")

    def _tunnel_2x1_loop(self):
        while not self._stop_event.is_set():
            # Check Auto-Eat
            if self.enable_food and (time.time() - self.last_eat_time > self.food_interval):
                self._eat_food()
                if self._stop_event.is_set():
                    break

            # 1. Mine Head Block (Upper)
            self.log(f"⛏ Копаем верхний блок... ({self.blocks_mined + 1})")
            DirectInputController.mouse_left_down()
            if not self._sleep_check(self.dig_delay):
                break
            DirectInputController.mouse_left_up()

            # 2. Mine Feet Block (Lower)
            self.log("⛏ Копаем нижний блок...")
            DirectInputController.mouse_left_down()
            if not self._sleep_check(self.dig_delay):
                break
            DirectInputController.mouse_left_up()

            # 3. Move Forward
            self.log("🚶 Шаг вперед...")
            DirectInputController.press_key('w')
            if not self._sleep_check(self.walk_delay):
                DirectInputController.release_key('w')
                break
            DirectInputController.release_key('w')

            self.blocks_mined += 1
            self.update_count(self.blocks_mined)

            # 4. Torch Placement
            if self.enable_torches and (self.blocks_mined % self.torch_interval == 0):
                self._place_torch()

    def _place_torch(self):
        self.log(f"💡 Установка факела (блок {self.blocks_mined}): Поворот влево...")
        # 1. Turn left ~90°
        DirectInputController.turn_left(amount=600, steps=15)
        if not self._sleep_check(0.50):
            return

        # 2. Place torch
        if self.torch_slot.lower() == 'f':
            DirectInputController.click_right(hold_time=0.15)
        else:
            DirectInputController.tap_key(self.torch_slot)
            if not self._sleep_check(0.1):
                return
            DirectInputController.click_right(hold_time=0.15)
            if not self._sleep_check(0.1):
                return
            DirectInputController.tap_key(self.pickaxe_slot)

        if not self._sleep_check(0.15):
            return

        # 3. Turn back right ~90°
        self.log("💡 Возврат прицела прямо...")
        DirectInputController.turn_right(amount=600, steps=15)
        self._sleep_check(0.1)

    def _eat_food(self):
        self.log("🍖 Авто-Еда: Едим еду...")
        DirectInputController.tap_key(self.food_slot)
        if not self._sleep_check(0.15):
            return
        DirectInputController.mouse_right_down()
        if not self._sleep_check(2.3): # Eating animation in Minecraft ~1.6s
            DirectInputController.mouse_right_up()
            return
        DirectInputController.mouse_right_up()
        DirectInputController.tap_key(self.pickaxe_slot)
        self.last_eat_time = time.time()
        self.log("🍖 Закончили есть!")

    def _autoclicker_loop(self):
        self.log("⚡ Режим Автокликера активен...")
        while not self._stop_event.is_set():
            DirectInputController.mouse_left_down()
            if not self._sleep_check(self.dig_delay):
                break
            DirectInputController.mouse_left_up()
            if not self._sleep_check(0.05):
                break
