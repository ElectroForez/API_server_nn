FROM forez/realsr-ncnn-vulkan

WORKDIR /usr/src/
RUN git clone https://github.com/ElectroForez/server_nn-api.git
RUN git clone https://github.com/ElectroForez/video_nn.git
RUN apt install python3-pip -y
RUN pip install -r server_nn-api/requirments.txt -r video_nn/requirments.txt
WORKDIR /usr/src/server_nn-api
EXPOSE 5000
ENTRYPOINT ["python3", "server_nn.py", "5000"]
