#!/usr/bin/env python3
"""Genera los SFX y la musica de Robo Caotico (WAV, sintesis propia).

Uso: python3 tools/generate_audio.py
No necesita dependencias: solo la libreria estandar.
"""
import math
import os
import random
import struct
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX_DIR = os.path.join(ROOT, "assets", "audio", "sfx")
MUSIC_DIR = os.path.join(ROOT, "assets", "audio", "music")
AMBIENCE_DIR = os.path.join(ROOT, "assets", "audio", "ambience")

TAU = math.tau
SFX_SR = 44100
MUSIC_SR = 22050


def write_wav(path, samples, sr, peak=0.9):
    top = max(1e-9, max(abs(s) for s in samples))
    gain = peak / top
    frames = bytearray()
    for s in samples:
        v = int(max(-1.0, min(1.0, s * gain)) * 32767)
        frames += struct.pack("<h", v)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sr)
        f.writeframes(bytes(frames))
    print("%-42s %5.2fs  %6.1f KB" % (os.path.relpath(path, ROOT), len(samples) / sr, len(frames) / 1024))


def fade_edges(buf, sr, fade_in=0.003, fade_out=0.012):
    a = min(len(buf), int(fade_in * sr))
    b = min(len(buf), int(fade_out * sr))
    for i in range(a):
        buf[i] *= i / a
    for i in range(b):
        buf[-1 - i] *= i / b


def add_note(buf, start, freq, dur, amp, sr, attack=0.004, decay=None,
             harmonics=((1.0, 1.0),), vibrato=0.0):
    if decay is None:
        decay = max(0.02, dur * 0.45)
    n = int(dur * sr)
    start = int(start * sr)
    for i in range(n):
        idx = start + i
        if idx < 0 or idx >= len(buf):
            break
        t = i / sr
        env = min(1.0, t / max(0.0001, attack)) * math.exp(-t / decay)
        phase = TAU * freq * t
        if vibrato:
            phase += vibrato * math.sin(TAU * 5.0 * t)
        s = 0.0
        for mult, weight in harmonics:
            s += weight * math.sin(phase * mult)
        buf[idx] += amp * env * s


def add_noise(buf, start, dur, amp, sr, decay=0.02, lowpass=0.0):
    n = int(dur * sr)
    start = int(start * sr)
    prev = 0.0
    for i in range(n):
        idx = start + i
        if idx < 0 or idx >= len(buf):
            break
        t = i / sr
        env = math.exp(-t / max(0.0001, decay))
        raw = random.uniform(-1.0, 1.0)
        if lowpass > 0.0:
            prev += (raw - prev) * lowpass
            raw = prev
        buf[idx] += amp * env * raw


def add_sweep(buf, start, f0, f1, dur, amp, sr, harmonics=((1.0, 1.0),)):
    n = int(dur * sr)
    start = int(start * sr)
    phase = 0.0
    for i in range(n):
        idx = start + i
        if idx < 0 or idx >= len(buf):
            break
        t = i / dur
        freq = f0 + (f1 - f0) * t
        phase += TAU * freq / sr
        env = math.exp(-3.2 * t)
        s = 0.0
        for mult, weight in harmonics:
            s += weight * math.sin(phase * mult)
        buf[idx] += amp * env * s


def echo(buf, taps):
    src = list(buf)
    n = len(buf)
    for delay_s, gain in taps:
        d = int(delay_s * MUSIC_SR)
        for i in range(n):
            buf[i] += src[(i - d) % n] * gain


def fold_loop(buf, loop_samples, tail_samples):
    for i in range(tail_samples):
        buf[i] += buf[loop_samples + i]
    return buf[:loop_samples]


# ---------------------------------------------------------------- SFX (44.1k)
def sfx_gem():
    sr = SFX_SR
    buf = [0.0] * int(0.38 * sr)
    add_note(buf, 0.0, 987.77, 0.20, 0.5, sr, decay=0.10,
             harmonics=((1, 1.0), (2.01, 0.35), (3.02, 0.15)))
    add_note(buf, 0.065, 1318.51, 0.26, 0.45, sr, decay=0.12,
             harmonics=((1, 1.0), (2.01, 0.3), (3.02, 0.12)))
    add_noise(buf, 0.02, 0.12, 0.05, sr, decay=0.04)
    fade_edges(buf, sr)
    return buf


def sfx_grab():
    sr = SFX_SR
    buf = [0.0] * int(0.17 * sr)
    add_sweep(buf, 0.0, 210.0, 95.0, 0.12, 0.55, sr)
    add_noise(buf, 0.0, 0.05, 0.2, sr, decay=0.012, lowpass=0.35)
    fade_edges(buf, sr)
    return buf


def sfx_drop():
    sr = SFX_SR
    buf = [0.0] * int(0.24 * sr)
    add_sweep(buf, 0.0, 150.0, 55.0, 0.18, 0.6, sr)
    add_note(buf, 0.0, 60.0, 0.20, 0.35, sr, decay=0.07)
    add_noise(buf, 0.0, 0.08, 0.18, sr, decay=0.02, lowpass=0.25)
    fade_edges(buf, sr)
    return buf


def sfx_deliver():
    sr = SFX_SR
    buf = [0.0] * int(1.05 * sr)
    notes = [523.25, 659.25, 783.99, 1046.50]
    for i, f in enumerate(notes):
        add_note(buf, i * 0.085, f, 0.75, 0.32, sr, decay=0.35,
                 harmonics=((1, 1.0), (2.76, 0.35), (5.4, 0.12)))
    echo(buf, [(0.17, 0.22), (0.34, 0.1)])
    fade_edges(buf, sr)
    return buf


def sfx_win():
    sr = SFX_SR
    buf = [0.0] * int(2.25 * sr)
    notes = [523.25, 659.25, 783.99, 1046.50]
    for i, f in enumerate(notes):
        add_note(buf, i * 0.11, f, 0.55, 0.32, sr, decay=0.28,
                 harmonics=((1, 1.0), (2, 0.35), (3, 0.15)))
    for f in [523.25, 659.25, 783.99, 1046.50, 1318.51]:
        add_note(buf, 0.52, f, 1.6, 0.18, sr, attack=0.02, decay=0.7,
                 harmonics=((1, 1.0), (2, 0.2)))
    for f in [1046.50, 1318.51, 1567.98]:
        add_note(buf, 0.8, f, 1.1, 0.10, sr, decay=0.45,
                 harmonics=((1, 1.0), (2.76, 0.3)))
    echo(buf, [(0.22, 0.2), (0.44, 0.1)])
    fade_edges(buf, sr)
    return buf


def sfx_lose():
    sr = SFX_SR
    buf = [0.0] * int(1.9 * sr)
    notes = [220.0, 196.0, 174.61, 164.81]
    for i, f in enumerate(notes):
        add_note(buf, i * 0.22, f, 0.8, 0.32, sr, decay=0.4,
                 harmonics=((1, 1.0), (2, 0.35), (3, 0.12)))
    add_note(buf, 0.0, 55.0, 1.7, 0.25, sr, attack=0.05, decay=0.9)
    add_noise(buf, 0.0, 0.5, 0.04, sr, decay=0.2, lowpass=0.1)
    fade_edges(buf, sr)
    return buf


def sfx_click():
    sr = SFX_SR
    buf = [0.0] * int(0.06 * sr)
    add_note(buf, 0.0, 1500.0, 0.035, 0.5, sr, decay=0.012)
    add_note(buf, 0.0, 900.0, 0.05, 0.25, sr, decay=0.02)
    fade_edges(buf, sr)
    return buf


def sfx_step():
    sr = SFX_SR
    buf = [0.0] * int(0.10 * sr)
    add_noise(buf, 0.0, 0.07, 0.35, sr, decay=0.018, lowpass=0.18)
    add_note(buf, 0.0, 85.0, 0.09, 0.25, sr, decay=0.03)
    fade_edges(buf, sr)
    return buf


def sfx_tick():
    sr = SFX_SR
    buf = [0.0] * int(0.05 * sr)
    add_note(buf, 0.0, 2350.0, 0.03, 0.4, sr, decay=0.008)
    add_note(buf, 0.0, 1180.0, 0.04, 0.2, sr, decay=0.012)
    fade_edges(buf, sr)
    return buf


def sfx_camera():
    sr = SFX_SR
    buf = [0.0] * int(0.22 * sr)
    add_note(buf, 0.0, 1800.0, 0.07, 0.32, sr, decay=0.03)
    add_note(buf, 0.10, 1500.0, 0.07, 0.28, sr, decay=0.03)
    fade_edges(buf, sr)
    return buf


def sfx_alarm():
    sr = SFX_SR
    dur = 2.0
    buf = [0.0] * int(dur * sr)
    phase = 0.0
    for i in range(len(buf)):
        t = i / sr
        freq = 640.0 + 150.0 * math.sin(TAU * 1.5 * t)
        phase += TAU * freq / sr
        pulse = 0.55 + 0.45 * math.sin(TAU * 2.0 * t)
        s = 0.5 * math.sin(phase) + 0.22 * math.sin(phase * 2.0)
        sub = 0.18 * math.sin(TAU * 110.0 * t) * max(0.0, math.sin(TAU * 2.0 * t))
        buf[i] = (s * pulse + sub) * 0.5
    fade_edges(buf, sr, fade_in=0.006, fade_out=0.006)
    return buf


# -------------------------------------------------------------- Music (22.05k)
def music_menu():
    sr = MUSIC_SR
    bpm = 80.0
    beat = 60.0 / bpm
    total_beats = 32
    loop_n = int(total_beats * beat * sr)
    tail_n = int(1.6 * sr)
    buf = [0.0] * (loop_n + tail_n)

    chords = [
        [110.00, 130.81, 164.81, 246.94],
        [87.31, 110.00, 130.81, 164.81],
        [130.81, 164.81, 196.00, 246.94],
        [98.00, 123.47, 146.83, 164.81],
    ]
    arp_pattern = [0, 2, 1, 3, 2, 1, 3, 0]

    for bar in range(4):
        start = bar * 8 * beat
        chord = chords[bar]
        for f in chord:
            add_note(buf, start, f, 5.9, 0.075, sr, attack=0.5, decay=3.4,
                     harmonics=((1, 1.0), (2, 0.18), (3, 0.06)))
        for b in range(8):
            add_note(buf, start + b * beat, chord[0] / 2.0, beat * 0.85, 0.16, sr,
                     attack=0.01, decay=0.45, harmonics=((1, 1.0), (2, 0.25)))
            for k in range(2):
                idx = b * 2 + k
                f = chord[arp_pattern[idx % len(arp_pattern)]] * 2.0
                add_note(buf, start + idx * beat / 2.0, f, beat * 0.7, 0.05, sr,
                         decay=0.3, harmonics=((1, 1.0), (2.76, 0.3), (5.4, 0.08)))

    random.seed(7)
    for _ in range(90):
        add_noise(buf, random.uniform(0, total_beats * beat), 0.012,
                  random.uniform(0.005, 0.018), sr, decay=0.004)
    buf = fold_loop(buf, loop_n, tail_n)
    echo(buf, [(beat, 0.22), (beat * 2, 0.12), (beat * 3, 0.06)])
    return buf


def music_heist():
    sr = MUSIC_SR
    bpm = 96.0
    beat = 60.0 / bpm
    total_beats = 32
    loop_n = int(total_beats * beat * sr)
    tail_n = int(1.6 * sr)
    buf = [0.0] * (loop_n + tail_n)

    bass_pattern = [55.00, 55.00, 65.41, 82.41, 55.00, 49.00, 65.41, 82.41]
    pluck_notes = [440.00, 523.25, 659.25, 392.00, 440.00, 659.25, 523.25, 392.00]
    pads = [
        [110.00, 130.81, 164.81],
        [87.31, 110.00, 130.81],
        [130.81, 164.81, 196.00],
        [82.41, 110.00, 164.81],
    ]

    for bar in range(4):
        start = bar * 8 * beat
        for f in pads[bar]:
            add_note(buf, start, f / 2.0, 5.2 * beat, 0.05, sr, attack=0.4, decay=2.0,
                     harmonics=((1, 1.0), (2, 0.12)))

    for b in range(total_beats):
        t0 = b * beat
        f = bass_pattern[b % 8]
        add_note(buf, t0, f, beat * 0.8, 0.24, sr, attack=0.006, decay=0.22,
                 harmonics=((1, 1.0), (2, 0.35), (3, 0.18)))
        if b % 4 in (0, 2):
            add_sweep(buf, t0, 95.0, 45.0, 0.16, 0.25, sr)
        add_noise(buf, t0 + beat * 0.5, 0.045, 0.045, sr, decay=0.01, lowpass=0.0)
        if b % 2 == 1:
            f2 = pluck_notes[(b // 2) % len(pluck_notes)]
            add_note(buf, t0, f2, beat * 1.4, 0.06, sr, decay=0.35,
                     harmonics=((1, 1.0), (2.76, 0.35), (5.4, 0.1)))

    random.seed(11)
    for _ in range(40):
        add_noise(buf, random.uniform(0, total_beats * beat), 0.02,
                  random.uniform(0.003, 0.01), sr, decay=0.006)
    buf = fold_loop(buf, loop_n, tail_n)
    echo(buf, [(beat / 2.0, 0.2), (beat, 0.12), (beat * 1.5, 0.06)])
    return buf


def ambience_lab():
    """Loop industrial de 24 s para el vertical slice.

    Solo tonos con un numero entero de ciclos en el loop, mas eventos
    cortos que se apagan antes del final: el salto de loop queda limpio.
    """
    sr = MUSIC_SR
    loop_s = 24.0
    n = int(loop_s * sr)
    buf = [0.0] * n

    # Zumbido de instalacion: frecuencias que completan ciclos exactos en 24 s.
    for i in range(n):
        t = i / sr
        slow = 0.55 + 0.45 * math.sin(TAU * 0.0416667 * t)
        drone = (
            0.030 * math.sin(TAU * 55.0 * t)
            + 0.018 * math.sin(TAU * 82.5 * t + 0.7)
            + 0.010 * math.sin(TAU * 110.0 * t + 1.9)
            + 0.006 * math.sin(TAU * 220.5 * t + 0.3)
        )
        buf[i] = drone * (0.55 + 0.45 * slow)

    # Aire metalico tenue, tambien periodico.
    for i in range(n):
        t = i / sr
        buf[i] += 0.004 * math.sin(TAU * 440.25 * t) * (0.5 + 0.5 * math.sin(TAU * 0.0833333 * t))

    # Gotas y crujidos, separados y con caida corta.
    for start, freq, amp in [
        (3.2, 1450.0, 0.06),
        (8.7, 1720.0, 0.045),
        (13.4, 1280.0, 0.05),
        (19.1, 1840.0, 0.04),
    ]:
        add_note(buf, start, freq, 0.42, amp, sr, attack=0.002, decay=0.11,
                 harmonics=((1.0, 1.0), (2.4, 0.25)))

    for start, f0, f1 in [(6.2, 92.0, 61.0), (16.8, 78.0, 54.0)]:
        add_sweep(buf, start, f0, f1, 0.85, 0.035, sr,
                  harmonics=((1.0, 1.0), (2.0, 0.2)))
    return buf


def main():
    random.seed(3)
    sfx = {
        "gem.wav": sfx_gem,
        "grab.wav": sfx_grab,
        "drop.wav": sfx_drop,
        "deliver.wav": sfx_deliver,
        "win.wav": sfx_win,
        "lose.wav": sfx_lose,
        "click.wav": sfx_click,
        "step.wav": sfx_step,
        "tick.wav": sfx_tick,
        "camera.wav": sfx_camera,
        "alarm.wav": sfx_alarm,
    }
    for name, fn in sfx.items():
        write_wav(os.path.join(SFX_DIR, name), fn(), SFX_SR, 0.85)

    music = {
        "menu.wav": music_menu,
        "heist.wav": music_heist,
    }
    for name, fn in music.items():
        write_wav(os.path.join(MUSIC_DIR, name), fn(), MUSIC_SR, 0.8)

    write_wav(os.path.join(AMBIENCE_DIR, "ambience.wav"), ambience_lab(), MUSIC_SR, 0.6)


if __name__ == "__main__":
    main()
