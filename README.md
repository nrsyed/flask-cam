# Raspberry Pi internet-streaming interactive Flask webcam server

## Overview
&#35; TODO

## Installation

Simply clone this repository and run `setup.sh` in the top-level directory,
specifying the port you'd like the server to listen on (i.e., the port that
will be opened up to the world) with the `-p`/`--port` flag:

```
git clone https://github.com/nrsyed/flask-cam.git
cd flask-cam
./setup.sh --port 9001
```

Replace `9001` with the port you wish to use. Note that the standard HTTP port
is 80, but it may be prudent to choose a different port for obscurity. After
the necessary packages have been installed and configuration files have been
created, the script will allow you to choose whether to set up an authorized
username/password. This username and password will be required by the web
interface to view the livestream webpage. For more information on user
authentication, see the [User Authentication](#user-authentication) section
below.

As part of the installation process, the `opencv-python` Python package is
installed. However, some users may wish to build/install OpenCV manually (for
example, using the instructions at
<a href="https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/">
pyimagesearch</a>). For this reason, `opencv-python` is not included in
`requirements.txt` (but is installed by `setup.sh`). If you wish to skip
installation of `opencv-python`, pass the `--skip-opencv` flag to `setup.sh`:

```
./setup.sh --port 9001 --skip-opencv
```

**NOTE**: This project relies on `uvcdynctrl` because it assumes that a webcam
supported by `uvcdynctrl` is being used. If this is not the case, `camera.py`
must be modified based on the specifics of your particular webcam(s).

**IMPORTANT**: If you wish to run the program in a Python virtual environment
(which is recommended), ensure that the virtual is activated before running
`setup.sh`.

The final step is modifying your router's port forwarding settings (assuming
you're accessing the internet from behind a router) to forward the port
previously selected (9001 in the example above) to your Raspberry Pi's local
IP address, which can be obtained via `ifconfig`.

To access the app, use your public IP address and the port you chose above.
You can obtain your public IP address using the `dig` tool, which is part of
the `dnsutils` package and is installed by `setup.sh`.

```
dig +short myip.opendns.com @resolver1.opendns.com
999.9.999.999
```

Then, to access the index page of the app, simply navigate to
`123.4.567.890:9001` in a web browser, replacing `123.4.567.890` with the IP
address returned by `dig` and `9001` with the port you chose previously.

### Uninstallation

To uninstall all components and configuration files, simply run `setup.sh` with
the `uninstall` option:

```
./setup.sh uninstall
```


## User authentication

The Flask application requires username/password authentication to access the
index page. Passwords are encrypted and authenticated via `bcrypt`. To add a
user, run `password.py` with the `-a`/`--add-user` flag, specifying the
username with the `-u`/`--user` option and the password with the
`-p`/`--password` option. Replace `dexter` with your desired username and
`omelet` with your desired password.

```
python password.py --add-user --user dexter --password omelet
```

By default, this creates a file named `users` in the application directory,
which contains the username and the base-64 encoded hash of the password.
Additional users can be added by the same process. For more information on
working with the list of allowed users, refer to the section on
<a href="#user-authentication">user authentication</a> below.

To modify an existing user's password or to delete a user from the list, use
the `-m`/`--modify-user` and `-d`/`--delete-user` flags, respectively.

```
# Modify a user's password.
python password.py --modify-user --user dexter --password hunter2

# Delete a user.
python password.py --delete-user dexter
```

To check a user's password, use the `-c`/`--check-password` flag, which prints
`True` if the password given is correct and `False` otherwise.

## Email alerts

There are a number of ways to send email alerts initiated by events on the
Raspberry Pi. Because it's relatively easy and doesn't require storing or
using the credentials for my primary Gmail account, I've opted to use Amazon
AWS SES (**S**imple **E**mail **S**ervice).

&#35; TODO

<img src="doc/img/aws_ses.png">
