#!/usr/bin/env python3
"""Genera la capa de audio de terror de FRECUENCIA MUERTA (WAV, sintesis propia).

Uso: python3 tools/fm_generate_horror_audio.py

No necesita dependencias: solo la biblioteca estandar. No sobrescribe los
assets existentes de ``assets/audio``: escribe en ``assets/audio/fm``.

Contenido:
  - amb_drone_loop.wav        24 s, drone sub-grave + cluster metalico frio.
  - event_metal_hit.wav       golpe metalico lejano con cola de sala.
  - event_distant_steps.wav   pasos amortiguados, sin fuente visible.
  - event_whisper_static.wav  susurro ininteligible + estatica de radio.
  - event_radio_interference.wav interferencia de radio con portadoras.
  - event_drip.wav            goteo en una sala humeda.
  - event_creak.wav           crujido metalico bajo tension.

Todo es sintesis original creada para este proyecto (CC0 / uso libre dentro
de FRECUENCIA MUERTA). No se usa ninguna grabacion externa ni musica.
"""
import math
import os
import random
import struct
import wave

TAU = math.tau
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "audio", "fm")
LOOP_SR = 22050
EVENT_SR = 44100


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
    print("%-46s %5.2fs  %6.1f KB" % (
        os.path.relpath(path, ROOT), len(samples) / sr, len(frames) / 1024))


def fade_edges(buf, sr, fade_in=0.004, fade_out=0.02):
    a = min(len(buf), int(fade_in * sr))
    b = min(len(buf), int(fade_out * sr))
    for i in range(a):
        buf[i] *= i / max(1, a)
    for i in range(b):
        buf[-1 - i] *= i / max(1, b)
        

def lowpass(buf, cutoff, sr):
    """Filtro de un polo aplicado en sitio."""
    dt = 1.0 / sr
    rc = 1.0 / (TAU * cutoff)
    alpha = dt / (rc + dt)
    prev = buf[0] if buf else 0.0
    for i in range(len(buf)):
        prev += (buf[i] - prev) * alpha
        buf[i] = prev
    return buf


def highpass(buf, cutoff, sr):
    low = list(buf)
    lowpass(low, cutoff, sr)
    for i in range(len(buf)):
        buf[i] -= low[i]
    return buf


def bandpass_noise(n, center, q, sr, seed):
    """Ruido blanco pasado por un pasa-banda RBJ de estado estable."""
    rng = random.Random(seed)
    w0 = TAU * center / sr
    alpha = math.sin(w0) / (2.0 * q)
    b0 = alpha
    b2 = -alpha
    a0 = 1.0 + alpha
    a1 = -2.0 * math.cos(w0)
    a2 = 1.0 - alpha
    b0 /= a0
    b2 /= a0
    a1 /= a0
    a2 /= a0
    x1 = x2 = y1 = y2 = 0.0
    out = [0.0] * n
    for i in range(n):
        x = rng.uniform(-1.0, 1.0)
        y = b0 * x + b2 * x2 - a1 * y1 - a2 * y2
        x2 = x1
        x1 = x
        y2 = y1
        y1 = y
        out[i] = y
    return out


def add_reverb(buf, sr, taps, feedback=0.35, wet=0.5):
    """Colas de eco con realimentacion; suficiente para una sala industrial."""
    src = list(buf)
    n = len(src)
    tail = [0.0] * n
    for delay_s, gain in taps:
        d = max(1, int(delay_s * sr))
        for i in range(n):
            prev = tail[i - d] if i >= d else 0.0
            tail[i] += (src[i - d] * gain + prev * feedback) if i >= d else 0.0
    for i in range(n):
        buf[i] = src[i] + tail[i] * wet
    return buf


def add_impulse(buf, start_s, sr, amp, decay, low=900.0):
    n = min(len(buf) - int(start_s * sr), int(decay * 6.0 * sr))
    if n <= 0:
        return
    t0 = int(start_s * sr)
    rng = random.Random(int(start_s * 1000) + 17)
    prev = 0.0
    alpha = min(1.0, 900.0 / low)
    for i in range(n):
        t = i / sr
        env = math.exp(-t / decay)
        prev += (rng.uniform(-1.0, 1.0) - prev) * alpha
        buf[t0 + i] += prev * env * amp
        if t > decay * 5.0 and i > 8:
            break


# --------------------------------------------------------------------- loops
def amb_drone_loop():
    """24 s sin costura: todos los tonos completan ciclos enteros en el loop."""
    sr = LOOP_SR
    loop_s = 24.0
    n = int(loop_s * sr)
    buf = [0.0] * n
    # Frecuencias = k / loop_s, con k entero: el loop cierra sin salto.
    for i in range(n):
        t = i / sr
        slow = 0.5 + 0.5 * math.sin(TAU * t / loop_s)
        slow2 = 0.5 + 0.5 * math.sin(TAU * 3.0 * t / loop_s + 1.2)
        sub = (
            0.080 * math.sin(TAU * 32.0 * t)
            + 0.050 * math.sin(TAU * 32.0416667 * t + 0.8)
            + 0.034 * math.sin(TAU * 45.0 * t + 1.7)
            + 0.022 * math.sin(TAU * 58.0 * t + 2.4)
            + 0.012 * math.sin(TAU * 87.0 * t + 0.3)
        )
        hum = (
            0.006 * math.sin(TAU * 60.0 * t)
            + 0.003 * math.sin(TAU * 120.0 * t + 0.9)
        )
        buf[i] = sub * (0.55 + 0.45 * slow) + hum * (0.4 + 0.6 * slow2)

    # Cluster metalico frio: parciales inarmonicos periodicos, sin melodia.
    rng = random.Random(20261113)
    for _ in range(26):
        # Bins enteros entre 140 y 520 Hz para que el loop sea exacto.
        k = rng.randint(int(140.0 * loop_s), int(520.0 * loop_s))
        f = k / loop_s
        phase = rng.uniform(0.0, TAU)
        amp = rng.uniform(0.0012, 0.0055)
        lfo = rng.choice((1.0, 2.0, 3.0, 5.0)) / loop_s
        lfo_phase = rng.uniform(0.0, TAU)
        for i in range(n):
            t = i / sr
            buf[i] += amp * math.sin(TAU * f * t + phase) * (0.5 + 0.5 * math.sin(TAU * lfo * t + lfo_phase))

    # Presion de aire muy grave, sin ruido blanco: senos por debajo de 130 Hz.
    for i in range(n):
        t = i / sr
        air = 0.010 * math.sin(TAU * 103.125 * t + 0.4) + 0.006 * math.sin(TAU * 116.25 * t + 2.1)
        buf[i] += air * (0.5 + 0.5 * math.sin(TAU * 2.0 * t / loop_s + 0.6))

    # Sin filtro final: todos los componentes ya completan ciclos enteros en el
    # loop y un lowpass con estado inicial romperia la costura en la muestra 0.
    return buf


# -------------------------------------------------------------------- events
def event_metal_hit():
    sr = EVENT_SR
    dur = 3.2
    n = int(dur * sr)
    buf = [0.0] * n
    # Modos inarmonicos de una pieza metalica golpeada.
    modes = [
        (173.0, 0.28, 2.4, 0.2),
        (397.0, 0.22, 1.8, 1.1),
        (691.0, 0.15, 1.3, 2.0),
        (1187.0, 0.10, 0.9, 0.6),
        (1873.0, 0.06, 0.6, 2.6),
        (2939.0, 0.035, 0.4, 1.4),
    ]
    for f, amp, decay, phase in modes:
        for i in range(min(n, int(2.8 * sr))):
            t = i / sr
            bend = 1.0 - 0.018 * min(1.0, t / dur)
            env = min(1.0, t / 0.0018) * math.exp(-t / decay)
            buf[i] += amp * env * math.sin(TAU * f * bend * t + phase)
    # Transitorio seco y pequeno bombo de impacto.
    add_impulse(buf, 0.0, sr, 0.30, 0.018, low=2600.0)
    for i in range(min(n, int(0.45 * sr))):
        t = i / sr
        buf[i] += 0.22 * math.exp(-t / 0.16) * math.sin(TAU * 58.0 * t)
    add_reverb(buf, sr, [(0.047, 0.24), (0.083, 0.16), (0.131, 0.10), (0.203, 0.06)], 0.32, 0.7)
    lowpass(buf, 3200.0, sr)
    fade_edges(buf, sr, 0.002, 0.35)
    return buf


def event_distant_steps():
    sr = EVENT_SR
    dur = 4.0
    n = int(dur * sr)
    buf = [0.0] * n
    rng = random.Random(411)
    start = 0.32
    for step in range(4):
        t0 = start + step * 0.70 + rng.uniform(-0.035, 0.035)
        freq = rng.uniform(50.0, 63.0)
        idx0 = int(t0 * sr)
        length = min(n - idx0, int(0.30 * sr))
        for i in range(length):
            t = i / sr
            env = min(1.0, t / 0.006) * math.exp(-t / 0.085)
            buf[idx0 + i] += 0.38 * env * math.sin(TAU * freq * t)
        add_impulse(buf, t0, sr, 0.11, 0.035, low=620.0)
    lowpass(buf, 780.0, sr)
    add_reverb(buf, sr, [(0.13, 0.18), (0.23, 0.12), (0.37, 0.07)], 0.25, 0.55)
    fade_edges(buf, sr, 0.05, 0.5)
    return buf


def event_whisper_static():
    sr = EVENT_SR
    dur = 4.6
    n = int(dur * sr)
    buf = [0.0] * n
    # Capas de aire susurrante: ruido pasa-banda sin tono ni palabras.
    layers = [
        (520.0, 2.8, 0.030, 0.0),
        (870.0, 3.2, 0.026, 0.7),
        (1320.0, 3.6, 0.020, 1.4),
        (2050.0, 4.0, 0.012, 2.1),
    ]
    for center, q, amp, offset in layers:
        noise = bandpass_noise(n, center, q, sr, int(center) + 5)
        rng = random.Random(int(center) + 31)
        t = offset * 0.25
        while t < dur - 0.3:
            syllable = rng.uniform(0.16, 0.34)
            attack = rng.uniform(0.03, 0.09)
            idx0 = int(t * sr)
            length = min(n - idx0, int(syllable * sr))
            for i in range(length):
                tt = i / sr
                env = min(1.0, tt / attack) * math.exp(-max(0.0, tt - attack) / (syllable * 0.55))
                env *= min(1.0, (syllable - tt) / 0.035)
                buf[idx0 + i] += noise[idx0 + i] * max(0.0, env) * amp * 8.0
            t += syllable + rng.uniform(0.05, 0.22)
    # Estatica de radio y chasquidos secos.
    for start_s in (0.15, 0.9, 1.7, 2.4, 3.3, 4.0):
        add_impulse(buf, start_s, sr, 0.05, 0.006, low=5000.0)
    hiss = bandpass_noise(n, 4200.0, 1.1, sr, 99)
    for i in range(n):
        buf[i] += hiss[i] * 0.012 * (0.5 + 0.5 * math.sin(TAU * 0.35 * i / sr))
    # Tremolo suave de radio, no musical.
    for i in range(n):
        t = i / sr
        buf[i] *= 0.82 + 0.18 * math.sin(TAU * 6.7 * t)
    highpass(buf, 260.0, sr)
    lowpass(buf, 6500.0, sr)
    fade_edges(buf, sr, 0.35, 0.6)
    return buf


def event_radio_interference():
    sr = EVENT_SR
    dur = 3.4
    n = int(dur * sr)
    buf = [0.0] * n
    rng = random.Random(77)
    # Portadoras de radio con AM rapida y puertas de silencio.
    carriers = [(412.0, 7.3, 0.10), (836.0, 11.7, 0.07), (1474.0, 5.1, 0.045), (2210.0, 9.4, 0.025)]
    for f, am, amp in carriers:
        phase = rng.uniform(0.0, TAU)
        for i in range(n):
            t = i / sr
            gate_a = 0.5 + 0.5 * math.sin(TAU * am * t + phase)
            gate_b = 0.5 + 0.5 * math.sin(TAU * (am * 0.37) * t + 2.0)
            gate = (gate_a * gate_b) ** 2.5
            buf[i] += amp * gate * math.sin(TAU * f * t + phase)
    # Ruido de banda ancha en rafagas.
    noise = bandpass_noise(n, 1800.0, 0.9, sr, 123)
    t = 0.0
    while t < dur:
        length = rng.uniform(0.08, 0.38)
        idx0 = int(t * sr)
        count = min(n - idx0, int(length * sr))
        for i in range(count):
            tt = i / sr
            env = min(1.0, tt / 0.01) * math.exp(-max(0.0, tt - 0.01) / (length * 0.4))
            env *= min(1.0, (length - tt) / 0.02)
            buf[idx0 + i] += noise[idx0 + i] * max(0.0, env) * 0.16
        t += length + rng.uniform(0.03, 0.18)
    for start_s in (0.08, 0.52, 1.14, 1.9, 2.55, 3.1):
        add_impulse(buf, start_s, sr, 0.06, 0.005, low=6000.0)
    highpass(buf, 180.0, sr)
    lowpass(buf, 7200.0, sr)
    fade_edges(buf, sr, 0.12, 0.25)
    return buf


def event_drip():
    sr = EVENT_SR
    dur = 1.9
    n = int(dur * sr)
    buf = [0.0] * n
    for start_s, amp, f0, f1 in ((0.08, 0.9, 1320.0, 430.0), (0.96, 0.55, 1180.0, 390.0)):
        idx0 = int(start_s * sr)
        phase = 0.0
        count = min(n - idx0, int(0.38 * sr))
        for i in range(count):
            t = i / sr
            freq = f0 + (f1 - f0) * min(1.0, t / 0.055)
            phase += TAU * freq / sr
            env = min(1.0, t / 0.0015) * math.exp(-t / 0.075)
            buf[idx0 + i] += amp * env * math.sin(phase)
        add_impulse(buf, start_s, sr, 0.10 * amp, 0.012, low=3200.0)
    add_reverb(buf, sr, [(0.11, 0.16), (0.19, 0.10), (0.31, 0.06)], 0.28, 0.6)
    lowpass(buf, 5200.0, sr)
    fade_edges(buf, sr, 0.003, 0.3)
    return buf


def event_creak():
    sr = EVENT_SR
    dur = 3.8
    n = int(dur * sr)
    buf = [0.0] * n
    # Ruido resonante: la estructura se queja, no es una voz ni un motor.
    for center, q, amp, sway in ((186.0, 18.0, 0.30, 26.0), (312.0, 24.0, 0.20, 38.0)):
        noise = bandpass_noise(n, center, q, sr, int(center) + 7)
        for i in range(n):
            t = i / sr
            swell = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(TAU * 0.55 * t + 1.1))
            micro = 0.60 + 0.40 * math.sin(TAU * (3.1 + 0.4 * math.sin(TAU * 0.2 * t)) * t)
            drift = 0.75 + 0.25 * math.sin(TAU * (sway / 100.0) * t + 0.8)
            buf[i] += noise[i] * amp * swell * micro * drift * 3.0
    # Golpes de tension y un lamento grave.
    rng = random.Random(305)
    t = 0.35
    while t < dur - 0.4:
        add_impulse(buf, t, sr, rng.uniform(0.03, 0.07), 0.01, low=1200.0)
        t += rng.uniform(0.45, 0.95)
    for i in range(n):
        tt = i / sr
        buf[i] += 0.05 * math.sin(TAU * (66.0 - 8.0 * tt / dur) * tt) * math.exp(-tt / 2.6)
    highpass(buf, 90.0, sr)
    lowpass(buf, 2400.0, sr)
    fade_edges(buf, sr, 0.25, 0.6)
    return buf


def main():
    random.seed(20261113)
    write_wav(os.path.join(OUT_DIR, "amb_drone_loop.wav"), amb_drone_loop(), LOOP_SR, 0.62)
    write_wav(os.path.join(OUT_DIR, "event_metal_hit.wav"), event_metal_hit(), EVENT_SR, 0.82)
    write_wav(os.path.join(OUT_DIR, "event_distant_steps.wav"), event_distant_steps(), EVENT_SR, 0.58)
    write_wav(os.path.join(OUT_DIR, "event_whisper_static.wav"), event_whisper_static(), EVENT_SR, 0.52)
    write_wav(os.path.join(OUT_DIR, "event_radio_interference.wav"), event_radio_interference(), EVENT_SR, 0.48)
    write_wav(os.path.join(OUT_DIR, "event_drip.wav"), event_drip(), EVENT_SR, 0.60)
    write_wav(os.path.join(OUT_DIR, "event_creak.wav"), event_creak(), EVENT_SR, 0.54)


if __name__ == "__main__":
    main()
