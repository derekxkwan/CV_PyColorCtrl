# CV_PyColorCtrl
experiments in sending osc messages corresponding to differently colored objects


[![cv_pycolorctrl demo](cv_pycolorctrl_1-16-19.png)](https://youtu.be/Qr1cq7uNvM4 "demo")

- **Python 3** requires `opencv-python` (OpenCV 4.0), and `python-osc`

## Components
- **cvcontrol.py** - detects blue and red objects so far and sends osc messages out on port `32323`
- **osc_test.py** - test reception of osc messages with tags `/red`, `/blue`, etc.

## LICENSE
gpl v 3
