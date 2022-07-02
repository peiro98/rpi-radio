import pyaudio
import socket
import struct

HOST, PORT = "127.0.0.1", 4242

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()

    with conn:
        print(f"Received a connection from {addr}")

        # audio sink
        sink = pyaudio.PyAudio()
        
        while True:
            # read frame type 
            frame_type = conn.recv(1)
            
            frame_type = struct.unpack_from("B", frame_type, 0)[0]

            if frame_type == 0:
                # settings frame
                settings = conn.recv(11)
                settings = struct.unpack_from("!BBxLL", settings)
                n_channels, sample_width, sample_rate, num_frames = settings

                print("")
                print("Audio settings: ")
                print(f"Sample rate: {sample_rate}")
                print(f"Num channels: {n_channels}")
                print(f"Sample width: {sample_width}")
                print(f"Num frames: {num_frames}")

                # TODO: format is assumed to be int16
                sink = sink.open(format=pyaudio.paInt16, channels=n_channels, rate=sample_rate, output=True)

            elif frame_type == 1:
                frame_length = conn.recv(3)
                frame_length, = struct.unpack_from("!Hx", frame_length)

                data = conn.recv(frame_length, socket.MSG_WAITALL)
                sink.write(data)

            elif frame_type == 2:
                print("Stream finished")
                break
