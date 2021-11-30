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
    parser.add_argument(
        '--visual_preset', default="High Density", type=str, 
        choices=["Custom", "Default", "Hand", "High Accuracy", "High Density"])

    return parser


def main(args):
    # json config
    json_path = args.json
    jason_obj = json.load(open(json_path))
    json_string= str(jason_obj).replace("'", '\"')
    width = int(jason_obj['viewer']['stream-width'])
    height = int(jason_obj['viewer']['stream-height'])
    FPS = int(jason_obj['viewer']['stream-fps'])

    # set output video encoding
    if args.format == 'mp4':
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    elif args.format == 'avi':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # set output video names
    color_path = args.name + '_rgb.' + args.format
    depth_path = args.name + '_depth.' + args.format
    # set output video writers
    colorwriter = cv2.VideoWriter(color_path, fourcc, FPS, (width, height), 1)
    depthwriter = cv2.VideoWriter(depth_path, fourcc, FPS, (width, height), 1)

    # define pipeline and its config
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, width, height, rs.format.z16, FPS)
    config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, FPS)

    pipe_profile = pipeline.start(config)
    device = pipe_profile.get_device()

    # Load advanced controls settings
    advnc_mode = rs.rs400_advanced_mode(device)
    advnc_mode.load_json(json_string)

    # DEPTH SENSOR CONFIGURATION
    # these are the stereo module main parameters
    depth_sensor = device.first_depth_sensor()

    # set visual preset -- 0=Custom, 1=Default, 2=Hand, 3=High Accuracy, 4=High Density
    preset_range = depth_sensor.get_option_range(rs.option.visual_preset)
    for i in range(int(preset_range.max)):
        visual_preset = depth_sensor.get_option_value_description(rs.option.visual_preset, i)
        if visual_preset == args.visual_preset:
            depth_sensor.set_option(rs.option.visual_preset, i)

    current_preset = depth_sensor.get_option(rs.option.visual_preset)
    current_visual_preset = depth_sensor.get_option_value_description(rs.option.visual_preset, current_preset)
    print("Depth visual preset:", current_visual_preset)

    depth_sensor.set_option(rs.option.enable_auto_exposure, True)
    depth_sensor.set_option(rs.option.emitter_enabled, 1)  # 1=Laser is the default
    # depth_sensor.set_option(rs.option.hdr_enabled, True)  # DO NOT USE, it makes the image flash

    try:
        # COLORMAPS
        # these are the depth visualization parameters
        colorizer = rs.colorizer()
        colorizer.set_option(rs.option.color_scheme, 0)  # 0 is Jet
        colorizer.set_option(rs.option.visual_preset, 1)  # 0=Dynamic, 1=Fixed, 2=Near, 3=Far
        value_min = 0
        value_max = 6
        colorizer.set_option(rs.option.min_distance, value_min)
        colorizer.set_option(rs.option.max_distance, value_max)
        colorizer.set_option(rs.option.histogram_equalization_enabled, True)

        # POST PROCESSING FILTERS
        decimation_filter = rs.decimation_filter(magnitude=2)  # Performs downsampling by using the median with specific kernel size
        threshold_filter = rs.threshold_filter(min_dist=0, max_dist=6)  # filter out depth values that are either too large or too small, as a software post-processing step
        depth_to_disparity_filter = rs.disparity_transform(transform_to_disparity=True)  # Converts from depth representation to disparity representation and vice
        spatial_filter = rs.spatial_filter(smooth_alpha=0.5, smooth_delta=20, magnitude=2, hole_fill=2)
        # Spatial filter smooths the image by calculating frame with 
        # alpha and delta settings. Alpha defines the weight of the current 
        # pixel for smoothing, and is bounded within [25..100]%. Delta 
        # defines the depth gradient below which the smoothing will occur 
        # as number of depth levels.
        # temporal_filter = rs.temporal_filter()
        disparity_to_depth_filter = rs.disparity_transform(transform_to_disparity=False)  # Converts from depth representation to disparity representation and vice
        

        # Streaming loop
        while True:
            frames = pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()

            if not depth_frame or not color_frame:
                # If there is no frame, probably camera not connected, return False
                print("Error, impossible to get the frame, make sure that the Intel Realsense camera is correctly connected")
                continue

            # Apply filters to the depth channel
            filtered_depth = depth_frame
            filtered_depth = decimation_filter.process(filtered_depth)
            filtered_depth = threshold_filter.process(filtered_depth)
            filtered_depth = depth_to_disparity_filter.process(filtered_depth)
            filtered_depth = spatial_filter.process(filtered_depth)
            # filtered_depth = temporal_filter.process(filtered_depth)
            filtered_depth = disparity_to_depth_filter.process(filtered_depth)
            

            # Apply colormap to show the depth of the Objects
            depth_colormap = np.asanyarray(colorizer.colorize(filtered_depth).get_data())
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

