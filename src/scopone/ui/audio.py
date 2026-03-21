"""Low-latency sound effect loading with procedural fallbacks."""

from __future__ import annotations

import math
import struct
from pathlib import Path

import pygame


class AudioManager:
    """Loads optional WAV assets and falls back to generated PCM effects."""

    def __init__(self) -> None:
        self.available = pygame.mixer.get_init() is not None
        self.audio_root = Path(__file__).resolve().parents[3] / "assets" / "audio"
        self.sounds = {}
        self.default_volumes = {}
        self.is_muted = False

        if not self.available:
            return

        self._register_sound("deal", self._load_sound(
            ["deal.wav", "shuffle.wav", "smazzata.wav"],
            self._build_deal_sound,
        ))
        self._register_sound("play", self._load_sound(
            ["play.wav", "card_play.wav", "giocata.wav"],
            self._build_play_sound,
        ))
        self._register_sound("capture", self._load_sound(
            ["capture.wav", "pickup.wav", "presa.wav"],
            self._build_capture_sound,
        ))

    def play(self, event_name: str) -> None:
        if not self.available:
            return

        sound = self.sounds.get(event_name)
        if sound is None:
            return

        try:
            sound.play()
        except pygame.error:
            return

    def set_muted(self, muted: bool) -> None:
        self.is_muted = bool(muted)
        if not self.available:
            return

        for name, sound in self.sounds.items():
            if sound is None:
                continue
            try:
                sound.set_volume(0.0 if self.is_muted else self.default_volumes.get(name, 0.4))
            except pygame.error:
                continue

    def _register_sound(self, name: str, sound) -> None:
        self.sounds[name] = sound
        if sound is None:
            return
        try:
            self.default_volumes[name] = sound.get_volume()
            sound.set_volume(0.0 if self.is_muted else self.default_volumes[name])
        except pygame.error:
            return

    def _load_sound(self, candidates, fallback_builder):
        for candidate in candidates:
            path = self.audio_root / candidate
            if not path.exists():
                continue
            try:
                sound = pygame.mixer.Sound(str(path))
                sound.set_volume(0.45)
                return sound
            except pygame.error:
                continue

        sound = fallback_builder()
        if sound is not None:
            sound.set_volume(0.4)
        return sound

    def _build_deal_sound(self):
        return self._build_pcm_sound(
            [
                (620.0, 0.03, 0.18),
                (430.0, 0.03, 0.14),
            ]
        )

    def _build_play_sound(self):
        return self._build_pcm_sound(
            [
                (220.0, 0.045, 0.26),
                (150.0, 0.02, 0.08),
            ]
        )

    def _build_capture_sound(self):
        return self._build_pcm_sound(
            [
                (340.0, 0.05, 0.18),
                (510.0, 0.07, 0.12),
                (680.0, 0.03, 0.08),
            ]
        )

    def _build_pcm_sound(self, tone_segments):
        if not self.available:
            return None

        mixer_settings = pygame.mixer.get_init()
        if mixer_settings is None:
            return None

        sample_rate = mixer_settings[0]
        samples = []
        for frequency, duration, amplitude in tone_segments:
            segment_samples = int(sample_rate * duration)
            for index in range(segment_samples):
                progress = float(index) / max(segment_samples - 1, 1)
                envelope = (1.0 - progress) ** 2
                waveform = math.sin(2.0 * math.pi * frequency * (float(index) / sample_rate))
                value = int(32767 * amplitude * envelope * waveform)
                samples.append(struct.pack("<h", value))

        if not samples:
            return None

        try:
            return pygame.mixer.Sound(buffer=b"".join(samples))
        except pygame.error:
            return None
