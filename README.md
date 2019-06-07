# Raspberry Pi internet streaming webcam server

## Installation and setup

Install the necessary system packages. Note that this repository relies on
`uvcdynctrl` because it assumes that a webcam supported by `uvcdynctrl` is
being used. If this is not the case, installation of `uvcdynctrl` may be
omitted and `camera.py` must be modified based on the specifics of your
particular webcam(s).

```
sudo apt -y install libffi-dev nginx uvcdynctrl
```

Clone this repository, then install the necessary Python packages, preferably
in a virtual environment. Note that OpenCV is also required but is not listed
in `requirements.txt`. It may be built/installed manually (for example, using
the instructions at
<a href="https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/">
pyimagesearch</a>) or via the prebuilt `opencv-python` package on PyPI.


```
git clone https://github.com/nrsyed/flask-cam.git
cd flask-cam
pip install -r requirements.txt
```

Ensure your Python virtual environment is activated (if using one), *then* run
`make_systemd_file.sh` to create a systemd unit file that will allow Gunicorn
to serve the application as a service, which will be named `flaskcam`. Next,
start and enable said service.

```
./make_systemd_file.sh
sudo systemctl start flaskcam
sudo systemctl enable flaskcam
```

To configure Nginx to properly route requests to gunicorn, create the file
`/etc/nginx/sites-available/flaskcam` and fill it out as follows, replacing the
port `9001` with the port you'd like your server to use, the sample IP address
`192.168.1.101` with the IP address of your Raspberry Pi on your local network
(which can be found with the `ifconfig` command), and the path to the flask-cam
repository directory (`/home/pi/flask-cam/`) with your own, if you've placed it
in a different directory. Note that standard HTTP port is 80, but it may be
prudent to choose a different port for obscurity.

```
server {
    listen 9001;
    server_name 192.168.1.101

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/pi/flask-cam/flaskcam.sock;
    }
}
```

Enable this configuration by symlinking it in the Nginx `sites-enabled` directory.

```
sudo ln -s /etc/nginx/sites-available/flaskcam /etc/nginx/sites-enabled
```

Test the configuration file you just created by running `nginx` with the `-t`
flag. If this indicates no errors, restart the Nginx service to effect the
changes.

```
sudo nginx -t
sudo systemctl restart nginx
```

Assuming you're running
<a href="https://wiki.archlinux.org/index.php/Uncomplicated_Firewall">ufw</a>,
allow connections on the port you chose above.

```
sudo ufw allow 9001
```
