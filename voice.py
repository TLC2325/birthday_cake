from sys import byteorder
from array import array
from struct import pack

import pyaudio
import wave

THRESHOLD = 500
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 44100

def is_silent(sound_data):
    MAXIMUM = 16384
    time = float(MAXIMUM)/max(abs(i) for i in sound_data)

    r = array('h')
    for i in sound_data:
        r.append(int(i*time))
    return r

def trim(sound_data):
    def _trim(sound_data):
        sound_started = False
        r = array('h')

        for i in sound_data:
            if not sound_started and abs(i) > THRESHOLD:
                sound_started = True
                r.append(i)

            elif sound_started:
                r.append(i)
        return r

    # Trim to the left
    sound_data = _trim(sound_data)

    # Trim to the right
    sound_data.reverse()
    sound_data = _trim(sound_data)
    sound_data.reverse()
    return sound_data
    
def add_silence(sound_data, seconds):
    silence = [0] * int(seconds * RATE)
    r = array('h', silence)
    r.extend(sound_data)
    r.extend(silence)
    return r

# record sound
def record():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
                    input=True, output=True,
                    frames_per_buffer=CHUNK_SIZE)
    num_silent = 0
    sound_started = False

    r = array('h')

    while 1:
        sound_data = array('h', stream.read(CHUNK_SIZE))
        if byteorder == 'big':
            sound_data.byteswap()
        r.extend(sound_data)

        silent = is_silent(sound_data)

        if silent and sound_started:
            num_silent += 1
        elif not silent and not sound_started:
            sound_started = True

        if sound_started and num_silent > 30:
            break

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    r = normalize(r)
    r = trim(r)
    r = add_silence(r, 0.5)
    return sample_width, r


def record_to_file(path):
    sample_width, data = record()
    data = pack('<' + ('h'*len(data)), *data)

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(data)
    wf.close()


if __name__ == '__main__':
    print('please speak a word into the microphone')
    record_to_file('demo.wav')
    print('done - result is written without the silence')