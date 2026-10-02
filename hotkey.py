"""Global F9 hotkey listener (clears the document)."""
from pynput import keyboard


class HotkeyListener:
    def __init__(self, on_clear):
        self.on_clear = on_clear
        self._listener = None

    def start(self):
        self._listener = keyboard.Listener(on_press=self._on_press)
        self._listener.start()

    def _on_press(self, key):
        if key == keyboard.Key.f9:
            try:
                self.on_clear()
            except Exception as exc:  # never let a hotkey error kill the listener
                print(f"[F9] clear failed: {exc}")

    def stop(self):
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
