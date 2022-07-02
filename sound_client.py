import struct
import wave
import socket

HOST, PORT = "127.0.0.1", 4242

wav_file = wave.open("lofi.wav", "r")

print(f"Sample rate: {wav_file.getframerate()}")
print(f"Channels: {wav_file.getnchannels()}")
print(f"Sample width: {wav_file.getsampwidth()}")
print(f"Num of frames: {wav_file.getnframes()}")


#####################
#  Settings frames  #
#####################

#  - type: unsigned char
#  - channels: unsigned char
#  - sample width: unsigned char
#  - one byte of padding
#  - sample rate: unsigned 32-bits integer
#  - num of frames: unsigned 32-bits integer

#    0                8               16               24               32
#  0 |----------------|----------------|----------------|----------------|
#    | frame type (0) | n. of channels | sample width   | *unused*       |
#  4 |----------------|----------------|----------------|----------------|
#    |                            sample rate                            |
#  8 |----------------|----------------|----------------|----------------|
#    |                         number of frames                          |
# 12 |----------------|----------------|----------------|----------------|


#################
#  Data frames  #
#################

#  - type: unsigned char
#  - frame length: unsigned 16-bits integer

#    0                8               16               24               32
#  0 |----------------|----------------|----------------|----------------|
#    | frame type (1) |          frame length           | *unused*       |
#  4 |----------------|----------------|----------------|----------------|
#    |                                                                   |
#    |                               data                                |
#    |                                                                   |
# xx |----------------|----------------|----------------|----------------|


################
#  End frames  #
################

#  - type: unsigned char

#    0                8               16               24               32
#  0 |----------------|----------------|----------------|----------------|
#    | frame type (2) |                     *unused*                     |
#  4 |----------------|----------------|----------------|----------------|


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    # settings frame has size 12 bytes
    settings_frame = struct.pack(
        "!BBBxLL", # format
        0, # settings frame
        wav_file.getnchannels(),
        wav_file.getsampwidth(),
        wav_file.getframerate(),
        wav_file.getnframes()
    )

    # get type
    frame_type = struct.unpack_from("B", settings_frame, 0)

    s.sendall(settings_frame)

    data = wav_file.readframes(1024)
    # data has size nframes * n_channels * sample width

    while len(data) > 0:
        data_frame = struct.pack(
            "!BHx", # format
            1, # data frame
            len(data) # frame length
        )

        s.sendall(data_frame + data)
        data = wav_file.readframes(1024)

    end_frame = struct.pack(
        "!Bxxx", # format
        2, # end frame
    )
    s.sendall(end_frame)
