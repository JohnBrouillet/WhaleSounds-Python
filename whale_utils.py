import os
import numpy as np
import soundfile as sf

def load_audio(path):
    samples, rate = sf.read(path)
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    duration = len(samples) / rate
    time = np.arange(len(samples)) / rate
    return samples, rate, duration, time

def compute_spectrogram(samples, nfft=1024, noverlap=512):
    hop = nfft - noverlap
    frames = np.lib.stride_tricks.sliding_window_view(samples, nfft)[::hop]
    window = np.hanning(nfft)
    spec = np.fft.rfft(frames * window, axis=1)
    S = np.abs(spec.T)
    S = S / np.max(S)
    S_db = 20 * np.log10(S + 1e-8)
    S_db = S_db + 100
    shapes = S_db.shape
    S_db = S_db.T
    return S_db, shapes
