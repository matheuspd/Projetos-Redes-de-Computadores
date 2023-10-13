import cv2
import numpy as np
import pyaudio
import threading
import socket

# Função para capturar e enviar áudio em tempo real por uma conexão TCP
def audio_capture_and_send(audio_stream, tcp_audio_socket, connection_status):
    CHUNK = 1024
    audio_input = pyaudio.PyAudio()
    audio_stream = audio_input.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=CHUNK)
    
    while True:
        audio_data = audio_stream.read(CHUNK)
        try:
            tcp_audio_socket.sendall(audio_data)
        except (BrokenPipeError, ConnectionResetError):
            connection_status.set()  # Define a flag para encerrar o código
            break

# Função para enviar quadros de vídeo por uma conexão TCP
def send_video_frames(cap, tcp_video_socket, connection_status):
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Erro ao ler quadro.")
            break

        # Codifica o quadro como JPEG antes de enviar para reduzir o tamanho
        _, frame_encoded = cv2.imencode('.jpg', frame)
        frame_data = frame_encoded.tobytes()

        # Envie o tamanho do quadro antes de enviar o quadro real
        frame_size = len(frame_data).to_bytes(4, byteorder='big')
        try:
            tcp_video_socket.sendall(frame_size)
            tcp_video_socket.sendall(frame_data)
        except (BrokenPipeError, ConnectionResetError):
            connection_status.set()  # Define a flag para encerrar o código
            break

# Inicializa a captura de vídeo a partir da webcam (0 é o ID da webcam padrão)
cap = cv2.VideoCapture(0)

# Verifica se a captura de vídeo foi aberta com sucesso
if not cap.isOpened():
    print("Erro ao abrir a câmera.")
    exit()

# Configura o endereço e a porta para enviar o vídeo por TCP
tcp_video_target_address = ('192.168.0.126', 12345)  # Substitua pelo endereço IP do destinatário
tcp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    tcp_video_socket.connect(tcp_video_target_address)
except ConnectionRefusedError:
    print("Não foi possível conectar ao destinatário.")
    exit()

# Configura o endereço e a porta para enviar o áudio por TCP
tcp_audio_target_address = ('192.168.0.126', 12346)  # Substitua pelo endereço IP do destinatário
tcp_audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    tcp_audio_socket.connect(tcp_audio_target_address)
except ConnectionRefusedError:
    print("Não foi possível conectar ao destinatário.")
    exit()

# Inicializa a captura e o envio de áudio em segundo plano
audio_stream = None
audio_connection_status = threading.Event()
audio_thread = threading.Thread(target=audio_capture_and_send, args=(audio_stream, tcp_audio_socket, audio_connection_status))
audio_thread.daemon = True
audio_thread.start()

# Inicializa a captura e o envio de vídeo em segundo plano
video_connection_status = threading.Event()
video_thread = threading.Thread(target=send_video_frames, args=(cap, tcp_video_socket, video_connection_status))
video_thread.daemon = True
video_thread.start()

while not audio_connection_status.is_set() and not video_connection_status.is_set():
    pass

# Libera a captura de vídeo e fecha a janela
print("Conexão com o destinatário encerrada.")
cap.release()
cv2.destroyAllWindows()
