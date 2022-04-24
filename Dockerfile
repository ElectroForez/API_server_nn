FROM forez/realsr-ncnn-vulkan

WORKDIR /usr/src/
RUN git clone https://github.com/ElectroForez/API_server_nn.git
RUN git clone https://github.com/ElectroForez/video_nn.git
RUN apt install python3-pip -y
RUN pip install -r API_server_nn/requirments.txt -r video_nn/requirments.txt
WORKDIR /usr/src/API_server_nn
EXPOSE 5000
ENTRYPOINT ["python3", "server_nn.py", "5000"]
