# QT Robot Game - Development Setup Guide

## Overview
This is a Flask-based web application for the QT Robot that includes educational games and interactive storytelling features.

## Windows Development Setup

### Prerequisites
- Python 3.13.5 (installed)
- Virtual environment (`.QTvenv`)

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

### ROS Packages (Mock Implementation)
This application is designed to run on a QT Robot with ROS (Robot Operating System). For Windows development, **mock packages** have been created in the project root:

- `rospy/` - Mock ROS Python client library
- `std_msgs/` - Mock ROS standard messages
- `sensor_msgs/` - Mock ROS sensor messages
- `cv_bridge/` - Mock OpenCV-ROS bridge
- `qt_robot_interface/` - Mock QT Robot interface services
- `qt_gesture_controller/` - Mock QT Robot gesture controller

These mock packages allow the code to import and run without errors, but **robot functionality will not work** on Windows. They are only for testing the Flask web interface.

### MySQL Database (Optional)
The application is configured for MySQL but the connection is now **optional**. If MySQL is not running, the app will start with a warning but continue to function.

**To use MySQL (optional):**
1. Install MySQL Server for Windows
2. Create a database called `USERS`
3. Update credentials in `main.py` if needed (default: user='root', password='root')

### Running the Application

```bash
python main.py
```

The Flask web server will start, typically on `http://localhost:5000`

### Expected Warnings
When running on Windows, you'll see mock messages like:
- `[Mock ROS] Initialized node: app`
- `[Mock ROS] Created publisher: /qt_robot/speech/say`
- `[WARNING] MySQL connection failed: ...`

These are **normal** and expected for Windows development.

## Production Deployment (QT Robot)

On the actual QT Robot (Linux with ROS):
1. Remove or ignore the mock packages in the project root
2. Ensure ROS is properly installed and configured
3. Ensure MySQL is running if database features are needed
4. The real ROS packages will be used automatically

## Project Structure

- `main.py` - Main Flask application
- `templates/` - HTML templates
- `static/` - Static assets (images, CSS, JS)
- `user_files/` - User session data
- Mock ROS packages (for Windows dev only)

## Troubleshooting

### Import Errors
If you get `ModuleNotFoundError` for ROS packages, ensure the mock packages are in the project root and Python can find them.

### Port Already in Use
If port 5000 is in use, modify the port in `main.py` at the bottom where Flask runs.

### Missing Images/Assets
Ensure all paths in `static/` directory are accessible and images are not corrupted.

## Notes

- This application uses ArUco markers for object detection
- Web interface uses Socket.IO for real-time communication
- The robot features (speech, gestures, emotions) will only work on the actual QT Robot

