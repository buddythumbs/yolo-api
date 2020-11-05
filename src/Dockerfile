FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY . /src

RUN apt-get update ##[edited]
RUN apt-get install 'ffmpeg'\
    'libsm6'\ 
    'libxext6'  -y

WORKDIR /src/

CMD [ "python", "object_detection.py" ]
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt