# Financial assessment tool for PV Plant + green H2 generation

This is a tool developed to model and financially assess energy projects involving a solar photovoltaic power plant that supplies with energy a electrolyzer plant to produce green hydrogen.

## Setup 

Python is assumend to be already installed. Python 3.11 was used.

Within the project's directory, open a terminal instance and type the following commands.

To ensure that Python package manager is installed:

```sh
python -m ensurepip --upgrade
```

To install the tool's requirements:

```sh
pip install -r requirements.txt
```

To initialize the tool:

```sh
python app.py
```

Upon correct initialization the following message should display in the terminal:


```sh
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with watchdog (inotify)
 * Debugger is active!
 * Debugger PIN: 122-289-601
```
## Use the tool

Inside a web browser navigate to http://127.0.0.1:5000. The default values will load up first, every parameter can be adjusted as required.

## Contact

Feel free to collaborate. If you have any questions you can contact me via email: maxescovi@gmail.com

## TODO...

- cache for same location 
- save results to database


#### Build for different architectures:

To build docker image for raspberry Pi (I am using version 3 B):

```sh
docker buildx build --platform linux/arm/v7 -t <docker repo>/npv_calculator:<tag> --push .
```

### Useful commands:

#### test endpoints within the container
```sh
docker exec -it nginx curl -v http://npv_calculator:5000/plot-data
```