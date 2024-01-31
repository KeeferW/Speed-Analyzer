import cv2
import easygui
import numpy as np
import csv
import os
import sys
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

# Fixed size for the result window
RESULT_WINDOW_SIZE = (750, 750)


class GraphWindow(QMainWindow):
    def __init__(self, parent=None):
        super(GraphWindow, self).__init__(parent)
        self.setWindowTitle("Frame Speed Graph")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlabel('Frame')
        self.ax.set_ylabel('Pixels/Frame')

        # Initialize empty lists for frames and speeds
        self.frames = []
        self.speeds = []

    def update_graph(self, frames, speeds):
        self.frames = frames
        self.speeds = speeds

        # Clear the previous plot
        self.ax.clear()

        # Plot the new data
        self.ax.plot(self.frames, self.speeds)

        # Set labels
        self.ax.set_xlabel('Frame')
        self.ax.set_ylabel('Pixels/Frame')

        # Draw the updated plot
        self.canvas.draw()


# Opens the Select ROI window and brings it to focus
def select_roi(frame):
    cv2.namedWindow("Select ROI", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Select ROI", frame.shape[1], frame.shape[0])

    # Set the window to be on top and fullscreen temporarily
    cv2.setWindowProperty("Select ROI", cv2.WND_PROP_TOPMOST, 1)
    cv2.setWindowProperty("Select ROI", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty("Select ROI", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

    roi = cv2.selectROI("Select ROI", frame, fromCenter=False, showCrosshair=False)

    # Check if the "Select ROI" window is still open
    if cv2.getWindowProperty("Select ROI", cv2.WND_PROP_VISIBLE) > 0:
        cv2.destroyWindow("Select ROI")

    return roi


def calculate_speed(video_path, roi, graph_window):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video file.")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    paused = False

    cv2.namedWindow("Original Video (space to pause or q to quit)", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Original Video (space to pause or q to quit)", frame_width, frame_height)

    cv2.namedWindow("Results", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Results", *RESULT_WINDOW_SIZE)

    # Extract the first frame
    ret, frame1 = cap.read()
    if not ret:
        print("Error reading video frame.")
        return

    # Convert the ROI coordinates to integers
    x, y, w, h = map(int, roi)

    # Initial frame within the ROI
    initial_roi_frame = frame1[y:y + h, x:x + w]

    speed_accumulator = 0
    frames_in_second = 0
    total_frames = 0
    seconds_elapsed = 0
    average_speeds = []
    speed_s = 0
    csv_filename = f"speed_data - {os.path.basename(video_path)}.csv"

    # Create a list to store speed data
    speed_data = []

    while True:
        # Read the next frame
        ret, frame2 = cap.read()

        if not ret:
            # If the video has ended, stay on the last frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, cap.get(cv2.CAP_PROP_FRAME_COUNT) - 1)
            frame2 = cap.read()[1]
            paused = True  # Pause the video when it reaches the end

        # Extract the frame within the ROI
        roi_frame = frame2[y:y + h, x:x + w]

        # Calculate optical flow using Lucas-Kanade method on the ROI
        flow = cv2.calcOpticalFlowFarneback(
            cv2.cvtColor(initial_roi_frame, cv2.COLOR_BGR2GRAY),
            cv2.cvtColor(roi_frame, cv2.COLOR_BGR2GRAY),
            None, 0.5, 3, 15, 3, 5, 1.2, 0
        )

        # Calculate the speed based on the optical flow
        magnitude = np.sqrt(flow[..., 0] ** 2 + flow[..., 1] ** 2)
        # Subtracting 0.01 to offset mean inconsistencies
        speed = np.mean(magnitude)

        speed_accumulator += speed
        frames_in_second += 1
        total_frames += 1

        # Append the current frame and speed to the list
        speed_data.append([total_frames, round(speed, 2), seconds_elapsed, round(speed_s, 2)])

        # Update the graph window
        frames_list = [data[0] for data in speed_data]
        speeds_list = [data[1] for data in speed_data]
        graph_window.update_graph(frames_list, speeds_list)

        # Display the speed information in the Results window
        result_window = np.zeros((*RESULT_WINDOW_SIZE, 3), dtype=np.uint8)
        cv2.putText(result_window, f"{speed:.2f} pixels/frame", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (255, 255, 255), 2)

        if frames_in_second >= fps:
            if ret:  # Only update average speed if the video is not at the end
                average_speed = speed_accumulator / frames_in_second
                average_speeds.append(average_speed)

            # Reset the accumulator for the next second
            speed_s = speed_accumulator / total_frames
            speed_accumulator = 0
            frames_in_second = 0
            seconds_elapsed += 1

        # Display all the average speeds
        for i, avg_speed in enumerate(average_speeds):
            cv2.putText(result_window, f"Second {i + 1}: {avg_speed:.2f} pixels/frame", (10, 70 + i * 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        # Calculate and display the total average speed
        if average_speeds:
            total_average_speed = np.mean(average_speeds)
            cv2.putText(result_window, f"Total Average Speed: {total_average_speed:.2f} pixels/frame",
                        (10, 70 + len(average_speeds) * 40 + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

        # Draw the ROI rectangle on the original video
        cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Show the result window
        cv2.imshow("Results", result_window)

        # Show the original video
        cv2.imshow("Original Video (space to pause or q to quit)", frame2)

        # Check for user input
        key = cv2.waitKey(1)
        if key == ord('q') or (not ret and key != -1):
            # Prompt the user if they want to export to a CSV file and save the graph
            export_csv = easygui.ynbox("Do you want to export data to a CSV file and save the graph?",
                                       "Export to CSV", ["Yes", "No"])
            if export_csv:
                # Save the graph as an image file
                graph_filename = f"speed_graph - {os.path.basename(video_path)}.png"
                if os.path.exists(graph_filename):
                    overwrite_graph = easygui.ynbox("The graph image already exists. Do you want to overwrite it?",
                                                    "Overwrite Graph", ["Yes", "No"])
                    if not overwrite_graph:
                        print("Operation canceled by user.")
                        graph_window.close()
                        cap.release()
                        cv2.destroyAllWindows()
                        sys.exit()

                graph_window.figure.savefig(graph_filename)
                print(f"Graph saved as: {graph_filename}")

                # Save the CSV file
                csv_filename = f"speed_data - {os.path.basename(video_path)}.csv"
                if os.path.exists(csv_filename):
                    overwrite_csv = easygui.ynbox("The CSV file already exists. Do you want to overwrite it?",
                                                  "Overwrite CSV", ["Yes", "No"])
                    if not overwrite_csv:
                        print("Operation canceled by user.")
                        graph_window.close()
                        cap.release()
                        cv2.destroyAllWindows()
                        sys.exit()

                with open(csv_filename, mode='w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(['Frame', 'Pixels/Frame', 'Seconds Elapsed', 'Average Pixel/Frame'])
                    csv_writer.writerows(speed_data)

                # Calculate the average pixels/frame from the CSV data
                pixels_frame_column = [data[1] for data in speed_data]
                average_pixels_frame = np.mean(pixels_frame_column)

                # Append the average pixels/frame to the second row of the fifth column
                with open(csv_filename, mode='a', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow(['', '', '', '', round(average_pixels_frame, 2)])

                print(f"CSV data saved as: {csv_filename}")

            # Close the graph window
            graph_window.close()
            cap.release()
            cv2.destroyAllWindows()
            sys.exit()  # Forcefully terminate the program

        elif key == ord(' '):  # Space to pause or continue
            if not ret:
                # If the video has reached the end, ignore spacebar
                continue
            paused = not paused

            # If paused, wait indefinitely until spacebar is pressed again
            while paused:
                key = cv2.waitKey(0)
                if key == ord(' '):
                    paused = not paused


# Ask the user to select a video file
video_path = easygui.fileopenbox(title="Select Video File", filetypes=["*.mp4"], default="*.mp4")

if video_path:
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Error opening video file.")
    else:
        # Read the first frame
        ret, frame = cap.read()

        if ret:
            # Select the ROI
            roi = select_roi(frame)

            # Check if the "Select ROI" window is still open
            if cv2.getWindowProperty("Select ROI", cv2.WND_PROP_VISIBLE) > 0:
                # Set the "Select ROI" window to be on top
                cv2.setWindowProperty("Select ROI", cv2.WND_PROP_TOPMOST, 1)

            # Create and show the graph window
            app = QApplication([])
            graph_window = GraphWindow()
            graph_window.show()

            # CSV filename
            csv_filename = f"speed_data - {os.path.basename(video_path)}.csv"

            # Calculate and display the speed
            calculate_speed(video_path, roi, graph_window)

            # Release resources and close the graph window
            cap.release()
            cv2.destroyAllWindows()
            app.exec_()
else:
    print("No video file selected.")