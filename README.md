# server_nn-api
REST API server for image processing by neural networks. Use with [realsr-ncnn-vulkan](https://github.com/nihui/realsr-ncnn-vulkan)

[API DOC](https://documenter.getpostman.com/view/17469696/UyrEfuP6)

[Docker](https://hub.docker.com/repository/docker/forez/server_nn-api)
# requirments
flask-restful==0.3.9

opencv-python==4.5.5.62

moviepy==1.0.3
# install
with already installed realsr-ncnn-vulkan
```
git clone https://github.com/ElectroForez/server_nn-api.git
git clone https://github.com/ElectroForez/video_nn.git
pip install -r server_nn-api/requirments.txt -r video_nn/requirments.txt
```
# usage
```
export PASS_NN=YOUR_PASSWORD
export REALSR_PATH=YOUR_PATH_TO_REASLR
$ python3 server_nn.py --help
usage: server_nn [-h] [-p PORT]

REST API server. Gets a picture and processes it using a neural network

options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  The port on which the server will be opened (default=500)
```
# example
Run
```
export PASS_NN=password
export REALSR_PATH="/home/vladt/realsr-ncnn-vulkan/realsr-ncnn-vulkan"
$ python3 server_nn.py -p 5000
```

Requests to server
```
# check status
curl -H 'X-PASSWORD: pass' http://localhost:5000/info/all_updated

# set task
curl -X POST 'http://localhost:5000/content/dir001?realsr=-x%20-s%204&output_name=out001.png' -H 'X-PASSWORD: pass' -F 'picture=@"/tmp/testdir/in001.png"'
{"status": "Picture was uploaded", "output_filename": "Updated_dir001/in001.png"}

# get list pictures
curl -H 'X-PASSWORD: pass' http://localhost:5000/content/Updated_dir001

# download result
curl -H 'X-PASSWORD: pass' http://localhost:5000/content/Updated_dir001/in001.png -o /tmp/testdir/out001.png

# cleanup result
curl -X DELETE -H 'X-PASSWORD: pass' http://localhost:5000/content/Updated_dir001/in001.png
```

