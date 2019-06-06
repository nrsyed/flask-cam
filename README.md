# Flask internet streaming webcam server

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


