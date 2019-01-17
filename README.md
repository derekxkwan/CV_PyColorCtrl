# CV_PyColorCtrl
experiments in sending osc messages corresponding to differently colored objects

- **Python 3** requires `opencv-python` (OpenCV 4.0), and `python-osc`

[![cv_pycolorctrl demo](cv_pycolorctrl_1-16-19.png)](https://youtu.be/Qr1cq7uNvM4 "demo")



## Components
- **cvcontrol.py** - detects blue and red objects so far and sends osc messages out on port `32323`
  - format: "o,x,y" string where o is flag for object detected (0/1), and x and y are x- and y- coords ([0,0] top-left, [1,1] bottom-right)
- **osc_test.py** - test reception of osc messages with tags `/red`, `/blue`, etc.

## LICENSE
gpl v 3
