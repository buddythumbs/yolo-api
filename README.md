# Overview

This is an object detection project which uses the YOLO object detection algorithm.
The object detection algorithm is exposed via FastAPI

# Running

Make sure you have Docker installed.

In order to run this project you will need to download 3 missing files:
1.  `coco.names` - https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names - the names of the classes for the model
2.  `yolov3.cfg` - https://github.com/pjreddie/darknet/blob/master/cfg/yolov3.cfg - config file for the model - can get this here .
3.  `yolov3.weights` - https://pjreddie.com/media/files/yolov3.weights - weights for the model.

Once these are downloaded, place them in an `artifacts` folder - ypu should have a foolder structure like the following:


```
├── README.md
├── artifacts
│   ├── coco.names
│   ├── yolov3.cfg
│   └── yolov3.weights
├── docker-compose.yml
└── src
    ├── Dockerfile
    ├── __init__.py
    ├── main.py
    ├── obj_detection
    │   ├── __init__.py
    │   ├── object_detection.py
    │   └── routes.py
    └── requirements.txt
```

To run the project type the following to build the image:

```bash
docker-compoose build
```

Once the image is built, run the following to run the project:

```bash
docker-compose up
```
The `artifacts` folder is mounted in the container and this is where files processed will be saved.

Also, all code in the `src` folder is mounted to the container so any changes will be seen in realtime.

Once running, head to http://0.0.0.0:80/docs to test out the API

This is all setup to be run in local development mode, if you want to build for production, remoove the following line from the `docker-compose.yml` file:

```yaml
command: /start-reload.sh
```

# Other

The following lines are included in the Dockerfile as the `openCV` library was unable to load in the inage.

```yaml
RUN apt-get update ##[edited]
RUN apt-get install 'ffmpeg'\
    'libsm6'\ 
    'libxext6'  -y
```

The foloowng volumes are mounted in `docker-compose.yml`:

```yaml
volumes: 
    - "/Users/martin/projects/object_detection/artifacts/config/:${CONFIG_DIR}"
    - "/Users/martin/projects/object_detection/artifacts/outputs/:${ARTIFACT_DIR}"
    - /Users/martin/projects/object_detection/src:/src/
```

 The first 2 mounts are for the config files (for the yolov3 model) and an output directory for processed images/videos. These are setup on my local machine and need to be managed by me - in order to industrialize this type of system it would be better to use a `bind mount` instead with some 3rd party provider (AWS/Azure/Google cloud). See https://docs.docker.com/storage/volumes/ for more info.

 is for development purposes only, this should be replaced with a proper `bind` mount in production.

