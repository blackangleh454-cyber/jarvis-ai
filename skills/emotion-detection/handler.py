#!/usr/bin/env python3
"""emotion-detection - Jarvis reads mood from voice tone."""
import sys
import os
import subprocess
import json

RECORDING_DIR = os.path.expanduser("~/Documents/jarvis_recordings")


def run(cmd, timeout=30):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout.strip() if r.returncode == 0 else r.stderr.strip()


def detect_emotion_audio(audio_path=None):
    """Detect emotion from audio file or mic."""
    if not audio_path:
        return record_and_detect()

    try:
        import torch
        from speechbrain.inference.classifiers import EncoderClassifier
    except ImportError:
        return "speechbrain not installed. Run: pip install speechbrain"

    try:
        classifier = EncoderClassifier.from_hparams(
            source="speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
            savedir="tmp_emotion"
        )
        out_prob, score, label = classifier.classify_file(audio_path)
        return f"Detected emotion: {label} (confidence: {score:.2f})"
    except Exception as e:
        return f"Detection error: {e}"


def record_and_detect(seconds=5):
    """Record from microphone and detect emotion."""
    os.makedirs(RECORDING_DIR, exist_ok=True)
    output = os.path.join(RECORDING_DIR, f"emotion_{int(os.times().elapsed * 1000)}.wav")

    try:
        subprocess.run([
            "arecord", "-f", "cd", "-t", "wav", "-d", str(seconds), output
        ], timeout=seconds+5)
    except:
        return "Could not record audio"

    if not os.path.exists(output):
        return "Recording failed"

    return detect_emotion_audio(output)


def text_sentiment(text):
    """Analyze text sentiment."""
    if not text:
        return "No text provided"

    text_lower = text.lower()

    positive_words = ["happy", "great", "love", "good", "excellent", "wonderful", "amazing", "best", "awesome", "joy", "excited"]
    negative_words = ["sad", "bad", "hate", "terrible", "awful", "worst", "angry", "frustrated", "upset", "angry", "annoyed"]
    neutral_words = ["okay", "fine", "neutral", "whatever"]

    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)

    if pos_count > neg_count:
        sentiment = "Positive 😊"
        confidence = min(pos_count / (pos_count + neg_count + 1) * 100, 99)
    elif neg_count > pos_count:
        sentiment = "Negative 😞"
        confidence = min(neg_count / (pos_count + neg_count + 1) * 100, 99)
    else:
        sentiment = "Neutral 😐"
        confidence = 50

    return f"Sentiment: {sentiment} (confidence: {confidence:.0f}%)\nText: {text[:100]}"


def current_mood_estimate():
    """Estimate current mood based on recent interactions."""
    return "Mood estimation requires voice analysis. Use 'detect' or 'record' to analyze."


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    a = sys.argv[2:]

    if cmd == "detect":
        print(detect_emotion_audio(a[0] if a else None))
    elif cmd == "analyze_tone":
        print(record_and_detect())
    elif cmd == "record":
        print(record_and_detect(int(a[0]) if a and a[0].isdigit() else 5))
    elif cmd == "sentiment":
        print(text_sentiment(" ".join(a)) if a else "Usage: sentiment <text>")
    elif cmd == "current_mood":
        print(current_mood_estimate())
    else:
        print("Commands: detect, analyze_tone, record, sentiment, current_mood")
