import pyaudio
import wave
import sys
import struct
import math
import audioop
import time

CHUNK = 1025
FORMAT = pyaudio.paInt16
CHANNELS = 2
MONO_CHANNEL = 1
RATE = 44100
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "voice.wav"

def play():
    wf = wave.open(sys.argv[2], 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)

    wf.close()
    stream.close()
    p.terminate()

def record():
    with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        stream = p.open(format = FORMAT,
                        channels = CHANNELS,
                        rate = RATE,
                        input = True,
                        frames_per_buffer=CHUNK)
        print("recording")
        for _ in range(0, RATE//CHUNK *  RECORD_SECONDS):
            wf.writeframes(stream.read(CHUNK))

    print("done")
    stream.close()
    p.terminate()

def detect_live():
    p = pyaudio.PyAudio()
    stream = p.open(format = FORMAT,
                    channels = CHANNELS,
                    rate = RATE,
                    input = True,
                    frames_per_buffer=CHUNK)
    while True:
        data = stream.read(CHUNK)
        rms = audioop.rms(data, 2)
        db = 20 * math.log10(rms)
        print(f'rms:[{rms}], db:[{db}]')

        if db > 60:
            with wave.open(sys.argv[2] + str(round(time.time() * 1000)) , 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                for _ in range(0, RATE//CHUNK *  RECORD_SECONDS):
                    wf.writeframes(stream.read(CHUNK))


    wf.close()
    stream.close()
    p.terminate()


def rmsf( data ):
    count = len(data)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, data )
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n*n
    return math.sqrt(int(sum_squares / count ))


def detect():
    wf = wave.open(sys.argv[2], 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(CHUNK)
    rms = audioop.rms(data, 2)
    db = 20 * math.log10(rms)
    print(f'rms:[{rms}], db:[{db}]')
    while data:
        data = wf.readframes(CHUNK)
        #rms = rmsf(data)
        rms = audioop.rms(data, 2)
        if rms > 0:
            print(f'rms:[{rms}]') 
            db2 = 20 * math.log10(rms)
            print(f'rms:[{rms}], db:[{db2}]')

    wf.close()
    stream.close()
    p.terminate()


def main():
    if sys.argv[1] == "play":
        play()
    elif sys.argv[1] == "detect":
        detect()
    elif sys.argv[1] == "detect-live":
        detect_live()
    else:
        record()

if __name__ == "__main__":
    main()
