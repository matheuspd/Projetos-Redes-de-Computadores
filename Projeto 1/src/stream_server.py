import threading
import socket

video_connections = []
audio_connections = []

# Função para enviar quadros de vídeo para clientes conectados
def send_video_to_clients(video_data, connections):
    for connection in connections:
        try:
            connection.sendall(video_data)
        except (BrokenPipeError, ConnectionResetError):
            connections.remove(connection)

# Função para enviar áudio para clientes conectados
def send_audio_to_clients(audio_data, connections):
    for connection in connections:
        try:
            connection.sendall(audio_data)
        except (BrokenPipeError, ConnectionResetError):
            connections.remove(connection)

# Função para lidar com as conexões do servidor
def server_handling(tcp_video_server, tcp_audio_server):
    while True:
        video_conn, video_addr = tcp_video_server.accept()
        audio_conn, audio_addr = tcp_audio_server.accept()
        print(f"Nova conexão de streamer: {video_addr} e {audio_addr}")

        video_thread = threading.Thread(target=receive_video, args=(video_conn, video_connections))
        video_thread.daemon = True
        video_thread.start()

        audio_thread = threading.Thread(target=receive_audio, args=(audio_conn, audio_connections))
        audio_thread.daemon = True
        audio_thread.start()

# Função para lidar com as conexões do cliente
def client_handling(tcp_video_client, tcp_audio_client):
    while True:
        video_conn, video_addr = tcp_video_client.accept()
        audio_conn, audio_addr = tcp_audio_client.accept()
        print(f"Nova conexão de cliente: {video_addr} e {audio_addr}")
        video_connections.append(video_conn)
        audio_connections.append(audio_conn)

# Função para receber e distribuir vídeo para os clientes
def receive_video(video_conn, connections):
    while True:
        try:
            frame_size_data = video_conn.recv(4)
            if not frame_size_data:
                break
            frame_size = int.from_bytes(frame_size_data, byteorder='big')
            frame_data = video_conn.recv(frame_size)
            send_video_to_clients(frame_size_data + frame_data, connections)
        except (ConnectionResetError, BrokenPipeError):
            connections.remove(video_conn)
            print("Um cliente(vídeo) foi desconectado.")
            break

# Função para receber e distribuir áudio para os clientes
def receive_audio(audio_conn, connections):
    CHUNK = 1024
    while True:
        try:
            audio_data = audio_conn.recv(CHUNK)
            send_audio_to_clients(audio_data, connections)
        except (ConnectionResetError, BrokenPipeError):
            connections.remove(audio_conn)
            print("Um cliente(áudio) foi desconectado.")
            break        

# Configura as portas para vídeo e áudio
tcp_video_server_address = ('0.0.0.0', 54321)
tcp_audio_server_address = ('0.0.0.0', 54322)

tcp_video_client_address = ('0.0.0.0', 12345)
tcp_audio_client_address = ('0.0.0.0', 12346)

# Inicializa os sockets para vídeo e áudio
tcp_video_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_video_server.bind(tcp_video_server_address)
tcp_video_server.listen(1)

tcp_audio_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_audio_server.bind(tcp_audio_server_address)
tcp_audio_server.listen(1)

tcp_video_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_video_client.bind(tcp_video_client_address)
tcp_video_client.listen(5) # 5 clientes assistindo

tcp_audio_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_audio_client.bind(tcp_audio_client_address)
tcp_audio_client.listen(5) # 5 clientes assistindo

# Inicia a thread para lidar com as conexões do servidor
server_handling_thread = threading.Thread(target=server_handling, args=(tcp_video_server, tcp_audio_server))
server_handling_thread.daemon = True
server_handling_thread.start()

# Inicia a thread para lidar com as conexões do cliente
client_handling_thread = threading.Thread(target=client_handling, args=(tcp_video_client, tcp_audio_client))
client_handling_thread.daemon = True
client_handling_thread.start()

# Mantém o servidor em execução
while True:
    pass
