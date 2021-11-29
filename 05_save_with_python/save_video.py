import pyrealsense2 as rs
import numpy as np
import cv2
import argparse


def get_parser():
    parser = argparse.ArgumentParser()
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
    parser.add_argument(
        '--visual_preset', default="High Density", type=str, 
        choices=["Custom", "Default", "Hand", "High Accuracy", "High Density"])
    return parser



def main(args):
    # set output video encoding
    if args.format == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    elif args.format == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # set output video names
    color_path = args.name + '_rgb.' + args.format
    depth_path = args.name + '_depth.' + args.format
    # set output video writers
    colorwriter = cv2.VideoWriter(color_path, fourcc, args.FPS, (args.width, args.height), 1)
    depthwriter = cv2.VideoWriter(depth_path, fourcc, args.FPS, (args.width, args.height), 1)

    # define pipeline and its config
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, args.width, args.height, rs.format.z16, args.FPS)
    config.enable_stream(rs.stream.color, args.width, args.height, rs.format.bgr8, args.FPS)

    pipe_profile = pipeline.start(config)
    depth_sensor = pipe_profile.get_device().first_depth_sensor()

    # set visual preset
    preset_range = depth_sensor.get_option_range(rs.option.visual_preset)
    for i in range(int(preset_range.max)):
        visual_preset = depth_sensor.get_option_value_description(rs.option.visual_preset, i)
        if visual_preset == args.visual_preset:
            depth_sensor.set_option(rs.option.visual_preset, i)

    current_preset = depth_sensor.get_option(rs.option.visual_preset)
    current_visual_preset = depth_sensor.get_option_value_description(rs.option.visual_preset, current_preset)
    print("Visual preset", current_visual_preset)

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

            # Define post-processing filters
            depth_to_disparity = rs.disparity_transform(True)
            spatial = rs.spatial_filter()

            # Apply filters to the depth channel
            filtered_depth = depth_to_disparity.process(depth_frame)
            filtered_depth = spatial.process(filtered_depth)

            # Create colormap to show the depth of the Objects
            colorizer = rs.colorizer()
            depth_colormap = np.asanyarray(colorizer.colorize(filtered_depth).get_data())

            # Convert images to numpy arrays
            color_image = np.asanyarray(color_frame.get_data())

            # Save to disk
            colorwriter.write(color_image)
            depthwriter.write(depth_colormap)
            
            # Show to screen
            cv2.imshow('RGB', color_image)
            cv2.imshow('Depth', depth_colormap)
            
            if cv2.waitKey(1) == ord("q"):
                break
    finally:
        colorwriter.release()
        depthwriter.release()
        pipeline.stop()


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    print(args)
    main(args)

