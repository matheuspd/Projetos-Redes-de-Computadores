import cv2
import numpy as np
import pyaudio
import threading
import socket

# Listening to Server and Sending Nickname
def receive(client, nickname):
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            if message == 'NICK':
                client.send(nickname.encode('ascii'))
            elif message == 'EXIT':
                print("You have left the chat.")
                client.close()
                break
            else:
                print(message)
        except:
            # Close Connection When Error
            print("An error occured!")
            client.close()
            break

# Sending Messages To Server
def write(client, nickname):
    while True:
        message = input('')
        if message.lower() == "/quit" or message.lower() == "/exit":
            client.send('/quit'.encode('ascii'))  # Envia o comando para o servidor
            client.close()
            break
        else:
            message = '{}: {}'.format(nickname, message)
            client.send(message.encode('ascii'))

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
    cv2.namedWindow('Local Video', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Local Video', 800, 600)

    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Erro ao ler quadro.")
            break

        cv2.imshow('Local Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            connection_status.set()
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
    cv2.namedWindow('Stream', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Stream', 800, 600)

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

        cv2.imshow('Stream', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def stream_video():
    # Inicializa a captura de vídeo a partir da webcam (0 é o ID da webcam padrão)
    cap = cv2.VideoCapture(0)

    # Verifica se a captura de vídeo foi aberta com sucesso
    if not cap.isOpened():
        print("Erro ao abrir a câmera.")
        exit()

    # Configura o endereço e a porta para enviar o vídeo por TCP
    tcp_video_target_address = ('127.0.0.1', 54321)  # Substitua pelo endereço IP do servidor
    tcp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_video_socket.connect(tcp_video_target_address)
    except ConnectionRefusedError:
        print("Não foi possível conectar ao servidor.")
        exit()

    # Configura o endereço e a porta para enviar o áudio por TCP
    tcp_audio_target_address = ('127.0.0.1', 54322)  # Substitua pelo endereço IP do servidor
    tcp_audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_audio_socket.connect(tcp_audio_target_address)
    except ConnectionRefusedError:
        print("Não foi possível conectar ao servidor.")
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
    print("Conexão com o servidor encerrada.")
    cap.release()
    cv2.destroyAllWindows()


def watch_video():
    # Choosing Nickname
    nickname = input("Choose your nickname: ")

    # Configura o endereço e a porta para enviar o vídeo por TCP
    tcp_video_target_address = ('127.0.0.1', 12345)  # Substitua pelo endereço IP do servidor
    tcp_video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_video_socket.connect(tcp_video_target_address)
    except ConnectionRefusedError:
        print("Não foi possível conectar ao servidor.")
        exit()

    # Configura o endereço e a porta para enviar o áudio por TCP
    tcp_audio_target_address = ('127.0.0.1', 12346)  # Substitua pelo endereço IP do servidor
    tcp_audio_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        tcp_audio_socket.connect(tcp_audio_target_address)
    except ConnectionRefusedError:
        print("Não foi possível conectar ao servidor.")
        exit()

    # Connecting To Server
    client_chat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_chat.connect(('127.0.0.1', 12347))

    # Starting Threads For Listening And Writing in chat
    receive_connection_status = threading.Event()
    receive_thread = threading.Thread(target=receive, args=(client_chat, nickname))
    receive_thread.start()
    
    write_connection_status = threading.Event()
    write_thread = threading.Thread(target=write, args=(client_chat, nickname))
    write_thread.start()

    # Inicializa a reprodução de áudio e exibição de vídeo em segundo plano
    audio_stream = None
    audio_connection_status = threading.Event()
    audio_thread = threading.Thread(target=audio_receive_and_play, args=(audio_stream, tcp_audio_socket))
    audio_thread.daemon = True
    audio_thread.start()

    receive_and_display_video(tcp_video_socket)

    receive_connection_status.set()
    write_connection_status.set()
    audio_connection_status.set()

    cv2.destroyAllWindows()

    print("Conexão com o servidor encerrada.")


def main():
    choice = input("Digite 'stream' para streamar ou 'watch' para assistir: ")

    if choice == "stream":
        stream_video()
    
    elif choice == "watch":
        watch_video()
    
    else:
        print("Escolha inválida. Reinicie o programa e escolha 'stream' ou 'watch'.")


if __name__ == '__main__':
    main()