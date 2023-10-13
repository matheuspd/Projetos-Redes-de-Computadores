import cv2
import numpy as np
import pyaudio
import threading

# Função para capturar e reproduzir áudio em tempo real
def audio_capture_and_play(audio_stream):
    CHUNK = 1024
    audio_input = pyaudio.PyAudio()
    audio_stream = audio_input.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, output=True, frames_per_buffer=CHUNK)
    
    while True:
        audio_data = audio_stream.read(CHUNK)
        audio_stream.write(audio_data)

# Inicializa a captura de vídeo a partir da webcam (0 é o ID da webcam padrão)
cap = cv2.VideoCapture(0)

# Verifica se a captura de vídeo foi aberta com sucesso
if not cap.isOpened():
    print("Erro ao abrir a câmera.")
    exit()

# Inicializa a captura e a reprodução de áudio em segundo plano
audio_stream = None
audio_thread = threading.Thread(target=audio_capture_and_play, args=(audio_stream,))
audio_thread.daemon = True
audio_thread.start()

while True:
    # Lê um quadro do vídeo
    ret, frame = cap.read()

    # Verifica se a leitura foi bem-sucedida
    if not ret:
        print("Erro ao ler quadro.")
        break

    # Mostra o quadro em uma janela
    cv2.imshow('Webcam', frame)

    # Aguarda uma tecla e sai do loop se a tecla 'q' for pressionada
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Libera a captura de vídeo e fecha a janela
cap.release()
cv2.destroyAllWindows()
