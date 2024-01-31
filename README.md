
# Speed Tracker

This Python script, converted into an executable (.exe) using PyInstaller, allows users to calculate and visualize the average speed of motion in a selected region of interest (ROI) within a video. 

This program was designed for high-speed video analysis at high framerates. Analysis of video under 60 fps may yield inconsistent results.

The script utilizes OpenCV for video processing, easygui for file selection, NumPy for math calculations, Matplotlib for real-time graph updates, and PyQT5 for GUI components.


## Algorithm

For speed analysis, the program utilizes the Lucas-Kanade Optical Flow algorithm. 

The Lucas-Kanade optical flow algorithm is a method for estimating the motion vector (optical flow) of pixels between two consecutive frames in a video sequence. Further documentation can be found here:
https://docs.opencv.org/3.4/db/d7f/tutorial_js_lucas_kanade.html

An important note is that it takes the average NOT the actual number of pixels moved, e.g a larger ROI selection on the same video in the same location will yield a smaller pixel/frame speed.
## Features

- ROI Selection: Users can choose a specific region within the video to analyze for motion speed. The ROI will remain visible while the video plays.

- Real-time Graph: A graphical representation of the motion speed over time is displayed.

- Average Speed Calculation: The script calculates the speed of pixels per frame, average speed per second, and overall average speed.

- Data Export: Users can export all speed data to a CSV file and can save the Real-time Graph as a PNG file..
## Requirements

The script is packaged as an executable (.exe), eliminating the need for users to download additional packages or dependencies.
## Usage and Details

Select Video File:  
- A file dialog will appear prompting you to select a video file (must be in .mp4).

Select ROI:     
- A window named "Select ROI" will appear over the first frame of the video. The video will remain paused until the ROI is selected and confirmed. 
- Click and drag to define the ROI.
- Press Enter to confirm the selection.

Graph Window:      
- A window titled "Frame Speed Graph" will appear. The graph will update in real-time as the script processes the video.

Results Window:     
- A window titled "Results" will appear. It will continuously display the current frame's speed as well as the average speed per second, and the total average speed of the ROI. 

Video Playback:     
- The original video will begin playback, the selected ROI will remain visible as a green box. 
- Press the spacebar to pause or resume the video. When paused, speed analysis will be stopped until the video is resumed. 

CSV File:   
- The CSV file will contain columns for Frame, Pixels/Frame, Seconds Elapsed, and Average Pixel/Frame. 
- When saved, it will be named "speed_data - [video_filename].png."

Graph Image:    
- The graph image displays the speed (pixels/frame) over time (frames). 
- When saved, it will be named "speed_graph - [video_filename].png."

Quitting:   
- Press 'q' to quit the script early. This will interupt any processes however data collection will be saved.

Export Data and Save Graph:     
- Upon completion or quit, a prompt will ask if you want to export data and save the graph. Choose "Yes" to export speed data to a CSV file and save the graph as a png image. 
- If a file with the same name already exists, a prompt will appear asking to overwrite the existing file with the current data.
## Bugs and Unintended Interactions
- When the program is first opened it will open an empty terminal and may take up to 30 seconds to run while in a network drive. This is due to how PyInstaller packs python libraries, and can be optimized further if needed. A temporary fix would be to copy the program into a local drive, this will make it start significantly faster, however is still not an instant response.


- If the user clicks out of the ROI selection window then brings it back to focus, an ROI selection cannot be made. A failsafe exists by pressing 'c' and the ROI selection window will be forcibly terminated and ends the script. 

- The user cannot q to quit or space to pause/resume if the graph window is in focus. The user must first click into either the results or video window to quit or pause/resume. 

- If multiple instances of the program is opened, it will never start up, but the terminal windows will still be visible.
