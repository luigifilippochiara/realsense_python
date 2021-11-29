"""
Load a recorded .bag streams, and save 
the depth stream as a video file.
"""


import pyrealsense2 as rs
import numpy as np
import cv2
import os
import json
import argparse


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input', '-i', type=str, help="Path to the bag file")
    parser.add_argument(
        '--json', '-j', default='config.json', type=str, help="Path to the json config file")
    parser.add_argument(
        '--name', '-n', default='record', type=str)
    parser.add_argument(
        '--format', '-f', default='mp4', type=str, choices=['mp4', 'avi'])
    parser.add_argument(
        '--width', default=1280, type=int, choices=[1280, 848, 640])
    parser.add_argument(
        '--height', default=720, type=int, choices=[720, 480, 360])
    parser.add_argument(
        '--FPS', '-fps', default=30, type=int, choices=[15, 25, 30, 60, 90])
    return parser


def get_args(parser):
    # Parse the command line arguments to an object
    args = parser.parse_args()
    # Safety if no parameter have been given
    if not args.input:
        print("No input paramater have been given.")
        print("For help type --help")
        exit()
    # Check if the given file have bag extension
    if os.path.splitext(args.input)[1] != ".bag":
        print("The given file is not of correct file format.")
        print("Only .bag files are accepted")
        exit()
    return args


def main(args):
    # set output video encoding
    if args.format == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    elif args.format == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # set output video names
    depth_path = args.name + '_depth.' + args.format
    # set output video writers
    depthwriter = cv2.VideoWriter(depth_path, fourcc, args.FPS, (args.width, args.height), 1)

    # Create pipeline
    pipeline = rs.pipeline()
    # Create a config object
    config = rs.config()
    # Tell config that we will use a recorded device from file to be used by the pipeline through playback.
    config.enable_device_from_file(args.input, repeat_playback=False)
    # Configure the pipeline to stream the depth stream
    # REMEMBER that width, height and FPS should be the same of the recorded stream
    config.enable_stream(rs.stream.depth, args.width, args.height, rs.format.z16, args.FPS)

    # Start streaming from file
    profile = pipeline.start(config)
    device = profile.get_device()

    # Playback is used to find duration of recorded video
    playback = device.as_playback()
    playback.set_real_time(False)
    # duration in nano seconds
    duration = playback.get_duration().total_seconds() * 1e9

    try:
        # Create colorizer object
        colorizer = rs.colorizer()

        # Streaming loop
        while True:
            # Get frameset
            frames = pipeline.wait_for_frames()
            curr_pos = playback.get_position()
            
            # DEPTH
            depth_frame = frames.get_depth_frame()
            if not depth_frame:
                print("No depth_frame")
                continue
            # Colorize depth frame to jet colormap
            depth_color_frame = colorizer.colorize(depth_frame)
            # Convert depth_frame to numpy array to render image in opencv
            depth_color_image = np.asanyarray(depth_color_frame.get_data())
            # Save to disk
            depthwriter.write(depth_color_image)
            # Render image in opencv window
            cv2.imshow('Depth', depth_color_image)

            print("Progress:", f"{curr_pos}/{duration}")
            if curr_pos >= duration:
                print("End of recording reached")
                break

            # if pressed escape exit program
            if cv2.waitKey(1) in [27, ord("q")]:
                break
    finally:
        cv2.destroyAllWindows()
        depthwriter.release()
        pipeline.stop()
        print("Done.")


if __name__ == '__main__':
    parser = get_parser()
    args = get_args(parser)
    print(args)
    main(args)

