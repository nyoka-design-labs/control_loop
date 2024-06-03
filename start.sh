#!/bin/bash

cd /home/sam/Desktop/control_loop

gnome-terminal --tab --title="server" --command="bash -c 'source /home/sam/Desktop/control_loop/env/bin/activate; python /home/sam/Desktop/control_loop/webapp/backend/api_server.py'"
gnome-terminal --tab --title="client" --command="bash -c 'cd /home/sam/Desktop/control_loop/webapp/frontend; npm start'"