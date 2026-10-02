"""Microphone capture with voice-activity detection.

Continuously reads the mic and yields one float32 audio array per spoken
utterance (a question), using a trailing-silence heuristic to know when the
speaker has finished.
"""
import queue

import numpy as np
import sounddevice as sd
import webrtcvad

from config import (
    FRAME_MS,
    INPUT_DEVICE,
    MIN_SPEECH_MS,
    SAMPLE_RATE,
    SILENCE_MS,
    VAD_AGGRESSIVENESS,
)


def list_input_devices() -> str:
    """Return a printable list of available input (microphone) devices."""
    lines = ["Available input devices:"]
    for idx, dev in enumerate(sd.query_devices()):
        if dev["max_input_channels"] > 0:
            lines.append(f"  [{idx}] {dev['name']}")
    return "\n".join(lines)

FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)  # 480 samples @ 16kHz/30ms
FRAME_BYTES = FRAME_SAMPLES * 2                      # int16 = 2 bytes/sample


class AudioCapture:
    def __init__(self):
        self.vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
        self._q: "queue.Queue[bytes]" = queue.Queue()
        self._stream = None

    def _callback(self, indata, frames, time_info, status):
        # RawInputStream delivers a bytes-like buffer of int16 samples.
        self._q.put(bytes(indata))

    def start(self):
        self._stream = sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=FRAME_SAMPLES,
            dtype="int16",
            channels=1,
            device=INPUT_DEVICE,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self):
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    def segments(self):
        """Generator yielding a float32 numpy array per detected utterance."""
        silence_frames_needed = max(1, SILENCE_MS // FRAME_MS)
        min_speech_frames = max(1, MIN_SPEECH_MS // FRAME_MS)

        buf = b""
        triggered = False
        voiced: list[bytes] = []
        num_silent = 0

        while True:
            try:
                buf += self._q.get(timeout=0.5)
            except queue.Empty:
                continue  # keeps the loop responsive to Ctrl+C

            while len(buf) >= FRAME_BYTES:
                frame = buf[:FRAME_BYTES]
                buf = buf[FRAME_BYTES:]
                is_speech = self.vad.is_speech(frame, SAMPLE_RATE)

                if not triggered:
                    if is_speech:
                        triggered = True
                        voiced = [frame]
                        num_silent = 0
                else:
                    voiced.append(frame)
                    if is_speech:
                        num_silent = 0
                    else:
                        num_silent += 1
                        if num_silent >= silence_frames_needed:
                            speech_frames = len(voiced) - num_silent
                            if speech_frames >= min_speech_frames:
                                yield self._to_float32(b"".join(voiced))
                            triggered = False
                            voiced = []
                            num_silent = 0

    @staticmethod
    def _to_float32(raw: bytes) -> np.ndarray:
        return np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
