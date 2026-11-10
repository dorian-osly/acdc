import os
import pygame

class AudioPlayer:
    def __init__(self):
        self.initialized = False
        self.current_track = None
        self.is_paused = False
        self.volume = 0.75
        self._init_mixer()

    def _init_mixer(self):
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            self.initialized = True
            pygame.mixer.music.set_volume(self.volume)
        except Exception as e:
            print(f"Warning: Failed to initialize audio mixer: {e}")
            self.initialized = False

    def play_track(self, filepath: str, loop: bool = True, fade_ms: int = 800) -> bool:
        if not self.initialized:
            self._init_mixer()
            if not self.initialized:
                return False

        if not filepath or not os.path.exists(filepath):
            return False

        if self.current_track == filepath and pygame.mixer.music.get_busy() and not self.is_paused:
            return True

        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(fade_ms)
                pygame.time.wait(fade_ms // 2)

            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(loops=-1 if loop else 0)
            self.current_track = filepath
            self.is_paused = False
            return True
        except Exception as e:
            print(f"Error playing track '{filepath}': {e}")
            return False

    def pause(self):
        if self.initialized and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.is_paused = True

    def unpause(self):
        if self.initialized and self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def toggle_pause(self):
        if self.is_paused:
            self.unpause()
        else:
            self.pause()
        return self.is_paused

    def stop(self, fade_ms: int = 500):
        if self.initialized:
            try:
                pygame.mixer.music.fadeout(fade_ms)
            except Exception:
                pass
            self.current_track = None
            self.is_paused = False

    def set_volume(self, volume_percent: int):
        self.volume = max(0.0, min(1.0, volume_percent / 100.0))
        if self.initialized:
            try:
                pygame.mixer.music.set_volume(self.volume)
            except Exception:
                pass

    def is_playing(self) -> bool:
        if not self.initialized:
            return False
        return pygame.mixer.music.get_busy() and not self.is_paused
