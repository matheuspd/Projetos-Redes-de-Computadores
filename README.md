# Projetos-Redes-de-Computadores
Repositório para projetos da disciplina Redes de Computadores

### Autores:
- [Matheus Pereira Dias](https://github.com/matheuspd) - NUSP: 11207752
- [Gabriel Franceschi Libardi](https://github.com/gabriel-libardi) - NUSP: 11760739
- [Guilherme Castanon Silva Pereira](https://github.com/GuilhermeCastanon) - NUSP: 11801140
- [Mateus Santos Messias](https://github.com/butterbr4) - NUSP: 12548000

## Projeto 1

No primeiro projeto da disciplina, foi feito um serviço de streaming simplificado: um aplicativo de transmissão de vídeo com conexão através de um servidor central, utilizando sockets com o protocolo TCP. As dependências do projeto são:

- numpy: `pip install numpy`
- OpenCV: `pip install opencv-python`
- PyAudio: `pip install pyaudio`
- Pillow: `pip install pillow`

A instalação do módulo PyAudio é meio problemática. Primeiro, instale os seguintes pacotes (ou equivalentes para outras distribuições Linux):
```
sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
sudo apt-get install ffmpeg libav-tools
sudo pip install pyaudio
```
Para instalar as outras dependências, simplesmente rode:
```
pip install -r requirements.txt
```

O projeto foi testado em Python 3.10.11 e nas distribuições Fedora 38 e Ubuntu 22.02. Para rodar o servidor, rode o comando:
```
python3 src/stream_server.py
```
Para começar a transmitir o seu vídeo (microfone + webcam), rode o comando:
```
python3 src/stream_client.py
```
e selecione a opção "stream". Finalmente, conecte um usuário com o servidor para assistir à transmissão executando o mesmo comando, mas selecionando a opção "watch". A aplicação foi "hardcoded" para se conectar no Localhost, mas essa poderia ter sido facilmente adaptada para suportar qualquer IP ou URL passado pelo usuário. A adaptação não foi feita para facilitar a demonstração do funcionamento da aplicação num único PC.