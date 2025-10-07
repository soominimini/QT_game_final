# QT Robot Game - Development Setup Guide

## Overview
This is a Flask-based web application for the QT Robot includes educational games and interactive storytelling features.

## Windows Development Setup

### Prerequisites
- Python 3.13.5 (installed)

### Installation Steps

1. **Activate the virtual environment:**
   ```bash
   .QTvenv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```

## Important Notes for Windows Development

### ROS Packages (Implementation)
This application is designed to run on a QT Robot(Linux) with ROS (Robot Operating System).

- `rospy/` - ROS Python client library
- `std_msgs/` - ROS standard messages
- `sensor_msgs/` - ROS sensor messages
- `cv_bridge/` - OpenCV-ROS bridge
- `qt_robot_interface/` - QT Robot interface services
- `qt_gesture_controller/` - QT Robot gesture controller

These packages allow the code to import and run without errors, but **robot functionality will not work** on Windows. They are only for testing the Flask web interface.

### Running the Application

```bash
python main.py
```

The Flask web server will start, typically on `http://localhost:5000`

## Production Deployment (QT Robot)

On the actual QT Robot (Linux with ROS):
1. Ensure ROS is properly installed and configured
2. The real ROS packages will be used automatically

## Project Structure

- `main.py` - Main Flask application
- `templates/` - HTML templates
- `static/` - Static assets (images, CSS, JS)
- `user_files/` - User session data
-  ROS packages (for Windows dev only)

## Troubleshooting

### Port Already in Use
If port 5000 is in use, modify the port in `main.py` at the bottom where Flask runs.

### Missing Images/Assets
Ensure all paths in `static/` directory are accessible and images are not corrupted.

## Notes

- This application uses ArUco markers for object detection
- Web interface uses Socket.IO for real-time communication
- The robot features (speech, gestures, emotions) will only work on the actual QT Robot

