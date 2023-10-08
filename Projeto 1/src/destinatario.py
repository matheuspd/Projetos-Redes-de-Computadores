import cv2
import numpy as np
import pyaudio
import threading
import socket

# Função para reproduzir áudio em tempo real recebido por uma conexão TCP
def audio_receive_and_play(audio_stream, tcp_audio_socket):
    CHUNK = 1024
    audio_output = pyaudio.PyAudio()
    audio_stream = audio_output.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=CHUNK)

    while True:
        audio_data = tcp_audio_socket.recv(CHUNK)
        audio_stream.write(audio_data)

# Função para receber e exibir quadros de vídeo por uma conexão TCP
def receive_and_display_video(tcp_video_socket):
    cv2.namedWindow('Recebendo Vídeo', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Recebendo Vídeo', 800, 600)

    while True:
        # Receba o tamanho do quadro
        frame_size_data = tcp_video_socket.recv(4)
        frame_size = int.from_bytes(frame_size_data, byteorder='big')

        # Receba o quadro real
        frame_data = b""
        bytes_received = 0

        while bytes_received < frame_size:
            chunk = tcp_video_socket.recv(frame_size - bytes_received)
            if not chunk:
                break
            frame_data += chunk
            bytes_received += len(chunk)

        # Decodifique o quadro e exiba-o
        frame_encoded = np.frombuffer(frame_data, dtype=np.uint8)
        frame = cv2.imdecode(frame_encoded, cv2.IMREAD_COLOR)

        cv2.imshow('Recebendo Vídeo', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Configura o endereço e a porta para receber o vídeo por TCP
tcp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_video_socket.bind(('0.0.0.0', 12345))  # Escuta em todas as interfaces
tcp_video_socket.listen(1)

# Configura o endereço e a porta para receber o áudio por TCP
tcp_audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_audio_socket.bind(('0.0.0.0', 12346))  # Escuta em todas as interfaces
tcp_audio_socket.listen(1)

# Aceita a conexão para receber vídeo
tcp_video_connection, _ = tcp_video_socket.accept()

# Aceita a conexão para receber áudio
tcp_audio_connection, _ = tcp_audio_socket.accept()

# Inicializa a reprodução de áudio e exibição de vídeo em segundo plano
audio_stream = None
audio_thread = threading.Thread(target=audio_receive_and_play, args=(audio_stream, tcp_audio_connection))
audio_thread.daemon = True
audio_thread.start()

receive_and_display_video(tcp_video_connection)

cv2.destroyAllWindows()
