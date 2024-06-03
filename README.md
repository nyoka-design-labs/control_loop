# control_loop

Code for the repo is split into the `src` and `webapp` folder. The src folder contains the main control logic as well as the files to read from the various devices and sensors. The webapp folder contains the React client side and the Python websocket server.

### Start application

To start the server run the following commands from the control_loop directory:
```bash
# activate virtual environment
source env/bin/activate
# run websocket server
python webapp/backend/api_server.py
```

To start the the client run `npm start` in the `control_loop/webapp/frontend` directory.

Alternatively you can run the quick start bash script by running `bash start.sh`.