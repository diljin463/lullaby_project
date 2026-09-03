# (അന്തിമ താരാട്ട്) 🎯

### Basic Details

**Team Name:** [WhyThough]

### Team Members

- **Team Lead:** Diljin C James - [Saintgits College of Applied Sciences]
- **Member 2:** [Ayvin Abraham] - [Saintgits College of Applied Sciences]

---

### Project Description

That is pure malicious compliance—taking standard computer vision safety tech and weaponizing it to guarantee the absolute worst outcome. It aggressively encourages the driver to give up and drift off. When a driver's eyelids droop, the system skips loud alarms and immediately broadcasts the soothing Malayalam lullaby "Chaanjadi Aadi" by Gayatri, encouraging the driver to surrender the steering wheel and enjoy uninterrupted rest at 120 km/h.

---

### The Problem (that doesn't exist)

Modern automotive safety tech is plagued by unnecessary panic. When an exhausted driver falls asleep behind the wheel after a long shift, factory safety systems sound harsh buzzers and vibrate the steering wheel. This spikes cortisol levels and ruins a peaceful nap. Commuters are forced to stare at highway asphalt when they could easily be getting 8 hours of restorative deep sleep across four districts.

---

### The Solution (that nobody asked for)

Minnal Mayakkam brings malicious compliance to road safety:
- **Biometric Eyelid Tracking:** Evaluates real-time Eye Aspect Ratio (EAR) using MediaPipe FaceMesh.
- **Acoustic Sleep Induction:** Replaces collision sirens with Gayatri's "Chaanjadi Aadi" broadcast through cabin speakers.
- **Sarcastic Cockpit HUD:** Displays real-time status banners ("Driver peacefully resting at 120 km/h"), sleep progress meters, and transfers vehicular control directly to divine intervention ("In the hands of Guruvayurappan").

---

### Technical Details

#### Technologies/Components Used

For Software:
- **Languages used:** Python 3.11, JavaScript (ES6+), HTML5, CSS3
- **Frameworks used:** Flask 3.0+, Tailwind CSS
- **Libraries used:** OpenCV (`opencv-python`), MediaPipe (`mediapipe`), Pygame (`pygame`), NumPy (`numpy`)
- **Tools used:** Visual Studio Code, Git, GitHub, Modern Web Browser

---

### Implementation

For Software:

# Installation
```bash
# Clone repository
git clone [https://github.com/tinkerhub/useless_project_temp.git](https://github.com/tinkerhub/useless_project_temp.git)
cd useless_project_temp

# Install dependencies
pip install opencv-python mediapipe pygame flask numpy

# Run

```bash
python lullaby_driver.py

Project Documentation
For Software:

Screenshots (Add at least 3)
![Awake Mode](screenshots/awake_mode.png)
![Drowsy Mode](screenshots/drowsy_mode.png)
![Asleep Mode](screenshots/asleep_mode.png)

Diagram

+-------------------------------------------------------+
|                     1. VIDEO INPUT                    |
|          Webcam Feed  --->  OpenCV Processing         |
+-------------------------------------------------------+
                           |
                           v
+-------------------------------------------------------+
|                 2. EYE TRACKING (EAR)                 |
|  MediaPipe FaceMesh  --->  Calculate Eye Aspect Ratio  |
+-------------------------------------------------------+
                           |
                           v
+-------------------------------------------------------+
|                  3. DECISION CHECK                    |
|            Are eyes closed for 25+ frames?            |
+-------------------------------------------------------+
                 /                   \
           [ YES ]                   [ NO ]
              |                        |
              v                        v
+---------------------------+  +------------------------+
|       DRIVER ASLEEP       |  |      DRIVER AWAKE      |
|  - Play "Chaanjadi Aadi"  |  |  - Audio Stopped       |
|  - Bedtime Alert Active   |  |  - Normal Cruise State |
+---------------------------+  +------------------------+
              \                        /
               \                      /
                v                    v
+-------------------------------------------------------+
|                 4. COCKPIT DASHBOARD                  |
|  Flask Web HUD Displays Live Video, Speed & Telemetry  |
+-------------------------------------------------------+

Workflow Diagram: Real-time webcam frames are tracked via MediaPipe to compute EAR. Sustained eye closure for 25+ frames triggers Pygame to loop Gayatri's lullaby while Flask syncs telemetry to the dashboard.

Project Demo

Video
[demo video](https://drive.google.com/drive/folders/1tsZ3gp4DUhpuywFt8xbdOVtN_1ptgut6?usp=drive_link)

Video demonstrates live webcam eye-tracking, the drowsiness threshold trigger, the Chaanjadi Aadi audio loop, and cockpit HUD telemetry.


Team Contributions
Diljin C James: Computer vision pipeline (MediaPipe & OpenCV), EAR drowsiness math logic, Flask video streaming server, and Pygame audio integration.

[Ayvin Abraham]: Cockpit UI design, Tailwind CSS glassmorphic layout, sarcastic copy generation, and theme switcher logic.



Made with ❤️ at TinkerHub