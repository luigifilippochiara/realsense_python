# RealSense Python
Some Python scripts to get started with the Intel RealSense depth cameras

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](/LICENSE)

## Scripts description

1. `01_text_stream` prints to the standard output a snapshot of the depth camera in ASCII code.
2. `02_detect_point_depth` allow the user to detect the distance of a given point in the RGB view of the camera.
3. `03_measure_object_distance` run a mask-RCNN instance segmentator on the RGB view and compute the distance of the objects from the camera.
4. `04_object_tracking` is an example of a simple object tracking algorithm.
5. `05_save_with_python` contains a script to directly save the RGB and depth recordings in .mp4 or .avi formats, without using the default .bag format (which is very heavy).
6. `06_rosbag2video` allows to convert from .bag to .mp4 (does not work yet!).
