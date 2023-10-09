import socket
import threading

# Connection Data
host = '127.0.0.1'
port = 12345

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []

# Sending Messages To All Connected Clients
def broadcast(message):
    for client in clients:
        client.send(message)

def remove_client(client, nickname):    
    clients.remove(client)
    client.close()
    nicknames.remove(nickname)
    broadcast('{} left!'.format(nickname).encode('ascii'))
    print('{} left!'.format(nickname))

# Handling Messages From Clients
def handle(client):
    index = clients.index(client)
    nickname = nicknames[index]
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024)
            if message.decode('ascii').strip() == '/quit':  # Check if the message is "/quit"
                client.send('EXIT'.encode('ascii'))
                remove_client(client, nickname)
                break
            broadcast(message)
        except:
            # Removing And Closing Clients
            remove_client(client, nickname)
            break

# Receiving / Listening Function
def receive():
    try:
        while True:
        
            # Accept Connection
            client, address = server.accept()
            print("Connected with {}".format(str(address)))

            # Request And Store Nickname
            client.send('NICK'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')
            nicknames.append(nickname)
            clients.append(client)

            # Print And Broadcast Nickname
            print("Nickname is {}".format(nickname))
            broadcast("{} joined!".format(nickname).encode('ascii'))
            client.send('Connected to server!'.encode('ascii'))

            # Start Handling Thread For Client
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()
    except KeyboardInterrupt:
        print("\nServer has been interrupted.")
        server.close()

def main():
    receive()

if __name__ == "__main__":
    main()
