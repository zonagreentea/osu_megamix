import time, random, numpy as np, librosa
import sounddevice as sd
from pydub import AudioSegment
from collections import deque
from ..engine import register_mode

class PrototypeMode:
    name = "playable_prototype_audio"
    duration = 2.0

    def __init__(self, engine, audio_file="assets/audio.mp3"):
        self.engine = engine
        self.score = 0
        self.circles = []
        self.last_spawn = time.time()
        self.audio_file = audio_file

        # load audio with pydub for playback
        self.audio = AudioSegment.from_file(audio_file)
        self.samples = np.array(self.audio.get_array_of_samples()).astype(np.float32)
        self.rate = self.audio.frame_rate
        self.pos = 0
        self.stream = sd.OutputStream(samplerate=self.rate, channels=self.audio.channels)
        self.stream.start()

        # setup real-time BPM detection buffer
        self.chunk_size = 4096
        self.audio_buffer = deque(maxlen=44100*10)  # 10s buffer
        self.spawn_interval = 0.5  # default

    def update_bpm(self, new_samples):
        self.audio_buffer.extend(new_samples)
        y = np.array(self.audio_buffer)
        if len(y) > self.rate * 2:  # at least 2 seconds of audio
            tempo, _ = librosa.beat.beat_track(y=y, sr=self.rate)
            self.spawn_interval = max(0.05, 60 / tempo)

    def spawn_circle(self):
        sh, sw = self.engine.screen_height, self.engine.screen_width
        self.circles.append({'y': random.randint(1, sh-2),
                             'x': random.randint(1, sw-2),
                             'spawn': time.time()})

    def update(self):
        now = time.time()
        if now - self.last_spawn > self.spawn_interval:
            self.spawn_circle()
            self.last_spawn = now

        for c in self.circles[:]:
            if now - c['spawn'] > self.duration:
                self.circles.remove(c)

        # audio playback + real-time BPM
        if self.pos < len(self.samples):
            end = min(self.pos+self.chunk_size, len(self.samples))
            chunk = self.samples[self.pos:end]
            self.stream.write(chunk)
            self.update_bpm(chunk)
            self.pos = end

    def handle_input(self, key):
        if key == 'q':
            self.engine.quit()
        elif key == 'o':
            self.score += len(self.circles)
            self.circles.clear()

    def render(self):
        self.engine.clear()
        for c in self.circles:
            self.engine.draw_circle(c['y'], c['x'])
        self.engine.draw_text(0, 0, f"Score: {self.score} | Spawn interval: {self.spawn_interval:.2f}s")

def setup(engine):
    engine.register_mode(PrototypeMode(engine))
