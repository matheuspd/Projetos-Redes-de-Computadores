# Projetos-Redes-de-Computadores
Repositório para projetos da disciplina Redes de Computadores

### Autores:
- [Matheus Pereira Dias](https://github.com/matheuspd)
- [Gabriel Franceschi Libardi](https://github.com/gabriel-libardi) - NUSP: 11760739

## Projeto 1

No primeiro projeto da disciplina, foi feito um "skype" simplificado: um aplicativo de chamadas de vídeo com conexão peer-to-peer (P2P). As dependências do projeto são:

- numpy: `pip install numpy`
- OpenCV: `pip install opencv-python`
- PyAudio: `pip install python-pyaudio`

Para instalar as dependências, simplesmente rode:
```
pip install -r requirements.txt
```

A instalação do módulo PyAudio é meio problemática. Primeiro, instale os seguintes pacotes:
```
sudo apt-get install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0
sudo apt-get install ffmpeg libav-tools
sudo pip install pyaudio
```