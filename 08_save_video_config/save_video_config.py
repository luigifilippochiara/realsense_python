import pyrealsense2 as rs
import numpy as np
import cv2
import argparse
import json


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--name', '-n', default='record', type=str)
    parser.add_argument(
        '--format', '-f', default='mp4', type=str, choices=['mp4', 'avi'])
    parser.add_argument(
        '--json', '-j', default='config.json', type=str, help="Path to the json config file")

    return parser


def main(args):
    # json config
    json_path = args.json
    jason_obj = json.load(open(json_path))
    json_string= str(jason_obj).replace("'", '\"')
    width = int(jsonObj['viewer']['stream-width'])
    height = int(jsonObj['viewer']['stream-height'])
    FPS = int(jsonObj['viewer']['stream-fps'])

    # set output video encoding
    if args.format == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    elif args.format == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # set output video names
    color_path = args.name + '_rgb.' + args.format
    depth_path = args.name + '_depth.' + args.format
    # set output video writers
    colorwriter = cv2.VideoWriter(color_path, fourcc, FPS, (args.width, height), 1)
    depthwriter = cv2.VideoWriter(depth_path, fourcc, FPS, (args.width, height), 1)

    # define pipeline and its config
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, width, height, rs.format.z16, FPS)
    config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, FPS)

    pipe_profile = pipeline.start(config)

    device = pipe_profile.get_device()
    advnc_mode = rs.rs400_advanced_mode(device)
    advnc_mode.load_json(json_string)

    try:
        # Streaming loop
        while True:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if not depth_frame or not color_frame:
                # If there is no frame, probably camera not connected, return False
                print("Error, impossible to get the frame, make sure that the Intel Realsense camera is correctly connected")
                continue

            # # Define post-processing filters
            # depth_to_disparity = rs.disparity_transform(True)
            # spatial = rs.spatial_filter()

            # # Apply filters to the depth channel
            # filtered_depth = depth_to_disparity.process(depth_frame)
            # filtered_depth = spatial.process(filtered_depth)

            # Create colormap to show the depth of the Objects
            colorizer = rs.colorizer()
            depth_colormap = np.asanyarray(colorizer.colorize(depth_frame).get_data())

            # Convert images to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())

            # Save to disk
            colorwriter.write(color_image)
            depthwriter.write(depth_colormap)
            
            # Show to screen
            cv2.imshow('RGB', color_image)
            cv2.imshow('Depth', depth_colormap)
            
            # if pressed escape exit program
            if cv2.waitKey(1) in [27, ord("q")]:
                break
    finally:
        cv2.destroyAllWindows()
        colorwriter.release()
        depthwriter.release()
        pipeline.stop()


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    print(args)
    main(args)

