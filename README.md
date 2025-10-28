# QT Robot Educational Game Platform

A comprehensive Flask-based web application designed for the QT Robot that provides interactive educational games, storytelling experiences, and emotion recognition activities for children of different age groups.

## 🎯 Project Overview

This project creates an interactive educational platform where the QT Robot can engage with children through various games, stories, and activities. The system uses computer vision (ArUco markers), real-time communication (WebSocket), and robot control interfaces to create immersive learning experiences.


## 📝 Notes

- The application is specifically designed for the QT Robot platform
- ROS integration is essential for full functionality
- Web interface works independently for testing
- User data is stored locally in text files
- All robot interactions are logged for analysis


## 🏗️ Project Structure

### Core Application Files
- **`main.py`** - Main Flask application with all routes, Socket.IO handlers, and robot control logic
- **`emotion_card.py`** - Emotion recognition game module using ArUco markers
- **`emotion_card2.py`** - Advanced emotion game for older children
- **`emotion_card3.py`** - Multi-emotion comparison game
- **`object_action_card.py`** - Action card recognition game module
- **`interact_story.py`** - Interactive storytelling functionality

### Web Interface (`templates/`)
The web interface is organized by functionality:

#### Main Pages
- **`main.html`** - Main game selection interface
- **`login.html`** - User login/registration
- **`user_confirm.html`** - User confirmation page

#### Game Templates
- **Emotion Games**: `emotion_game1.html`, `emotion_game2.html`, `emotion_game3.html`
- **Action Games**: `action_game.html`
- **Dice Games**: `dice_*.html` (various dice-based activities)
- **Story Games**: `brown_bear*.html`, `goodnight/`, `red_riding/`

#### Instructional Pages
- **`Taking_Instructions_main.html`** - Main instruction interface
- **`instruction_young/`** - Age-specific instruction pages
- **Hospital/Park Instructions**: Location-based activity instructions

### Static Assets (`static/`)
- **`images/`** - Game assets organized by category:
  - `emotions/` - Emotion recognition images
  - `action_cards/` - Action/object cards
  - `emotion_game_2/` - Advanced emotion game assets
  - `story/` - Story-related images
  - `dice/` - Dice game assets
  - `instruction/` - Instructional images
- **`style.css`** - Main stylesheet
- **`app.js`** - Client-side JavaScript for Socket.IO communication

### Robot Interface Modules
- **`qt_robot_interface/`** - QT Robot service definitions
- **`qt_gesture_controller/`** - Gesture control services
- **`rospy/`** - ROS Python client library
- **`std_msgs/`** - ROS standard message types
- **`sensor_msgs/`** - ROS sensor message types
- **`cv_bridge/`** - OpenCV-ROS bridge

### User Data
- **`user_files/`** - User session logs and data storage

## 🎮 Game Categories

### 1. Emotion Recognition Games
- **Emotion Game 1** (Young): Basic emotion identification using ArUco markers
- **Emotion Game 2** (Older): Advanced emotion recognition with contextual scenarios
- **Emotion Game 3**: Multi-emotion comparison and selection

### 2. Action/Object Games
- Action card recognition and performance
- Object identification and interaction

### 3. Dice-Based Activities
- **Action Dice**: Physical activities (jumping jacks, breathing exercises, songs)
- **Emotion Dice**: Emotion expression and discussion
- **5W1H Dice**: Question-based learning (What, Who, Where, Why, When, How)
- **Board Game Dice**: Movement-based board game mechanics

### 4. Interactive Stories
- **Goldilocks and the Three Bears**: Interactive story with character selection
- **Brown Bear, Brown Bear**: Color and animal recognition story
- **Goodnight Moon**: Bedtime story with visual elements
- **Red Riding Hood**: Adventure story with decision points

### 5. Educational Activities
- **Yes/No Games**: Binary choice learning activities
- **Inference Games**: Critical thinking and reasoning exercises
- **Instruction Following**: Location-based activity instructions (Hospital, Park, Supermarket)

## 🤖 Robot Integration

### Speech and Audio
- Text-to-speech synthesis
- Audio playback for songs and sound effects
- Speech recognition and response

### Gestures and Emotions
- Idle gesture animations
- Emotion expression display
- Context-aware gesture selection
- Interactive gesture responses

### Computer Vision
- ArUco marker detection for card recognition
- Real-time camera feed processing
- Object and action recognition

## 🛠️ Technical Architecture

### Backend (Flask + Socket.IO)
- **Flask**: Web framework for HTTP routes and template rendering
- **Socket.IO**: Real-time bidirectional communication
- **ROS Integration**: Robot control and sensor data processing
- **Threading**: Concurrent speech, gesture, and audio processing

### Frontend (HTML/CSS/JavaScript)
- **Bootstrap**: Responsive UI framework
- **jQuery**: DOM manipulation and AJAX requests
- **Socket.IO Client**: Real-time communication with backend

### Computer Vision
- **OpenCV**: Image processing and ArUco marker detection
- **ArUco Markers**: Physical card recognition system
- **Real-time Processing**: Live camera feed analysis

## 🚀 Setup and Installation

### Prerequisites
- Python 3.7+
- ROS (Robot Operating System) - for robot functionality
- OpenCV
- Flask and related dependencies

### Installation
1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure ROS is properly configured (for robot deployment)
4. Run the application:
   ```bash
   python main.py
   ```

### Development vs Production
- **Development**: Can run on Windows with mock ROS packages for web interface testing
- **Production**: Requires Linux with full ROS installation for robot functionality

## 📊 User Data and Logging

The system automatically logs user interactions:
- User login/logout events
- Game selections and progress
- Robot speech and responses
- User actions and choices
- Session timestamps and duration

Logs are stored in `user_files/` with format: `{username}_{session_number}.txt`



