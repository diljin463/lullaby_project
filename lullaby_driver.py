import threading
import time
import webbrowser
import cv2
from flask import Flask, Response, jsonify, render_template_string
import numpy as np
import pygame
from mediapipe.python.solutions import face_mesh as mp_face_mesh

# 1. Pygame Audio Setup
pygame.mixer.init()
pygame.mixer.music.load("lullaby.mp3")

# 2. Eye Landmark Indices
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

EAR_THRESHOLD = 0.22
CONSEC_FRAMES_SLEEP = 25

state = {
    "is_sleeping": False,
    "progress": 0,
    "ear": 0.30,
    "sheep": 0,
}
sleep_frame_counter = 0


def calculate_ear(landmarks, eye_indices, img_w, img_h):
    coords = []
    for idx in eye_indices:
        lm = landmarks[idx]
        coords.append(np.array([lm.x * img_w, lm.y * img_h]))
    d_v1 = np.linalg.norm(coords[1] - coords[5])
    d_v2 = np.linalg.norm(coords[2] - coords[4])
    d_h = np.linalg.norm(coords[0] - coords[3])
    return (d_v1 + d_v2) / (2.0 * d_h) if d_h != 0 else 0.0


face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)
cap = cv2.VideoCapture(0)
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>അന്തിമ താരാട്ട് </title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    /* Standard Modern OS System Font Stack */
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }
    .glass {
      background: rgba(15, 23, 42, 0.78);
      backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .theme-btn.active {
      box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.3);
    }
  </style>
</head>
<body id="body-root" class="bg-slate-950 text-slate-100 min-h-screen p-6 select-none">

  <!-- THEME SELECTOR BAR -->
  <div class="max-w-7xl mx-auto mb-5 flex items-center justify-between glass px-5 py-3 rounded-xl border border-white/10">
    <div class="flex items-center space-x-2">
      <span class="text-xs font-medium uppercase tracking-wider text-slate-400">Select Profile:</span>
    </div>
    <div class="flex space-x-2">
      <button onclick="switchTheme('ksrtc')" id="btn-ksrtc" class="theme-btn active px-4 py-1.5 rounded-lg text-xs font-semibold bg-amber-500 text-slate-950 transition-all">
        🚌 K-SRTC Driver Mode
      </button>
      <button onclick="switchTheme('corporate')" id="btn-corporate" class="theme-btn px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">
        💼 LinkedIn Hustle Mode
      </button>
      <button onclick="switchTheme('divine')" id="btn-divine" class="theme-btn px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 text-slate-300 hover:bg-slate-700 transition-all">
        🪷 Yamaraj Astral Mode
      </button>
    </div>
  </div>

  <!-- MAIN COCKPIT HEADER -->
  <header class="max-w-7xl mx-auto glass rounded-xl p-4 mb-6 flex items-center justify-between shadow-lg">
    <div class="flex items-center space-x-3">
      <div id="status-dot" class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
      <h1 id="brand-title" class="text-lg font-bold text-amber-400">K-SRTC SLEEP EXPEDITION</h1>
      <span id="brand-pill" class="text-xs px-2.5 py-0.5 rounded-md bg-amber-500/15 text-amber-300 font-medium">CRUISE CONTROL: VALANJUM PULINJUM</span>
    </div>
    <div class="flex items-center space-x-8 text-sm font-medium text-slate-300">
      <div>Speed: <span id="telemetry-speed" class="text-amber-400 font-bold font-mono">120 km/h</span></div>
      <div>Steering: <span id="telemetry-steering" class="text-emerald-400 font-semibold">Feet On Dashboard</span></div>
      <div>Horn: <span id="telemetry-horn" class="text-red-400 font-semibold">Taped Permanently</span></div>
    </div>
  </header>

  <!-- DASHBOARD GRID -->
  <main class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-6">
    
    <!-- LEFT: WEBCAM FEED -->
    <section class="lg:col-span-7 flex flex-col space-y-4">
      <div id="cam-container" class="relative glass rounded-2xl overflow-hidden shadow-xl transition-all duration-300 border border-slate-800">
        <img src="/video_feed" alt="Webcam Feed" class="w-full h-auto object-cover transform scale-x-[-1]" />

        <div class="absolute top-4 left-4 bg-slate-950/80 px-3 py-1 rounded-md border border-white/10 text-xs font-mono flex items-center space-x-2">
          <span class="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
          <span id="cam-badge">FACIAL RADAR</span>
        </div>

        <!-- Sleep Watermark -->
        <div id="sleep-watermark" class="hidden absolute inset-0 bg-slate-950/80 backdrop-blur-[2px] flex items-center justify-center p-8 text-center">
          <div>
            <div id="sleep-icon" class="text-6xl mb-3 animate-bounce">🚌💨</div>
            <h2 id="watermark-main" class="text-2xl font-bold text-amber-300 mb-2">
              Driver peacefully resting at 120 km/h
            </h2>
            <p id="watermark-sub" class="text-sm text-slate-300 font-normal">
              Overtaking in dreams. Chaanjadi Aadi on full blast.
            </p>
          </div>
        </div>
      </div>

      <!-- COMEDY TELEMETRY STRIP -->
      <div class="glass rounded-xl p-3.5 grid grid-cols-3 text-center text-xs text-slate-400">
        <div>Eye Aperture (EAR): <span id="ear-val" class="text-white font-semibold font-mono ml-1">0.32</span></div>
        <div>Airbag Status: <span id="telem-airbag" class="text-amber-400 font-semibold ml-1">Coir Bus Cushion</span></div>
        <div>Road Vision: <span id="telem-vision" class="text-white font-semibold ml-1">Blind Trust</span></div>
      </div>
    </section>

    <!-- RIGHT: SARCASTIC INFOTAINMENT -->
    <section class="lg:col-span-5 flex flex-col space-y-6">
      
      <!-- Driver Alert Card -->
      <div id="status-card" class="glass rounded-2xl p-6 border-l-4 border-emerald-500 transition-all duration-300 shadow-md">
        <div class="flex items-center justify-between mb-3">
          <span class="text-xs uppercase tracking-wider font-semibold text-slate-400">Driver State Analysis</span>
          <span id="status-badge" class="text-xs font-semibold px-2.5 py-1 rounded-md bg-emerald-500/15 text-emerald-400">STRESS DETECTED</span>
        </div>
        <h2 id="main-headline" class="text-xl font-bold text-white leading-snug mb-2">Driver is Unforgivably Awake</h2>
        <p id="sub-description" class="text-sm text-slate-300 leading-normal">Road awareness detected. Commute anxiety unnecessary. Close your eyes immediately.</p>
      </div>

      <!-- Sleep Progression Bar -->
      <div class="glass rounded-2xl p-6 shadow-md">
        <div class="flex justify-between items-center mb-2.5">
          <span id="gauge-label" class="text-sm font-semibold text-slate-200">Bedtime Readiness</span>
          <span id="progress-percent" class="font-mono text-sm font-bold text-amber-400">0%</span>
        </div>
        <div class="w-full bg-slate-900 rounded-full h-3 p-0.5 border border-slate-800">
          <div id="progress-bar" class="bg-gradient-to-r from-amber-500 to-red-500 h-full rounded-full transition-all duration-200 w-0"></div>
        </div>
        <div class="flex justify-between text-xs text-slate-500 mt-2">
          <span>Awake</span>
          <span>Slow Blink</span>
          <span>Asleep</span>
        </div>
      </div>

      <!-- Media Player Card -->
      <div id="media-card" class="glass rounded-2xl p-6 relative overflow-hidden shadow-md border border-amber-500/15">
        <div class="flex items-center space-x-4">
          <div id="record-disc" class="w-12 h-12 rounded-xl bg-gradient-to-tr from-amber-500 to-red-600 flex items-center justify-center text-xl shadow-md transition-transform duration-1000">
            🎶
          </div>
          <div>
            <span id="music-header" class="text-[11px] uppercase text-amber-400 font-semibold tracking-wider block mb-0.5">ACOUSTIC SLEEP AID</span>
            <h3 class="font-semibold text-base text-white">Chaanjadi Aadi</h3>
            <p class="text-xs text-slate-300">Singer: Gayatri</p>
            <p id="music-status" class="text-xs text-slate-400 mt-1">Status: Standby (Awaiting driver slumber)</p>
          </div>
        </div>
      </div>

      <!-- Counter Strip -->
      <div class="glass rounded-xl p-4 text-xs text-slate-400 flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="text-base" id="counter-icon">🐑</span>
          <span id="counter-title">POTHOLES DODGED:</span>
          <span id="sheep-counter" class="text-amber-400 font-bold font-mono text-sm">0</span>
        </div>
        <div>
          <span>DESTINATION:</span>
          <span id="dest-val" class="text-amber-300 font-semibold ml-1">PARAMAPADAM</span>
        </div>
      </div>

    </section>
  </main>

  <script>
    const THEMES = {
      ksrtc: {
        speed: "120 km/h",
        brand: "K-SRTC SLEEP EXPEDITION",
        pill: "CRUISE CONTROL: VALANJUM PULINJUM",
        steeringSleep: "In the Hands of Guruvayurappan",
        airbag: "Coir Bus Cushion",
        icon: "🚌💨",
        asleepHeadline: "Driver peacefully resting at 120 km/h",
        asleepDesc: "Overtaking in dreams. Chaanjadi Aadi on full blast. Don't touch the horn.",
        drowsyDesc: "Eyelids falling. Road ahead cleared through sheer intimidation.",
        awakeHeadline: "Driver is Staring at the Road Like an Amateur",
        awakeDesc: "Real drivers navigate by instinct and blind faith. Please close eyes.",
        musicHeader: "MALAYALAM ACOUSTIC SNOOZER",
        counterTitle: "POTHOLES DODGED IN SLEEP:",
        dest: "PARAMAPADAM VIA TRIVANDRUM"
      },
      corporate: {
        speed: "115 km/h",
        brand: "SYNERGY-DRIVE B2B",
        pill: "OUT OF OFFICE: HIGHWAY SLUMBER",
        steeringSleep: "Pivoted to Autonomous Chaos",
        airbag: "Padded Equity Pillow",
        icon: "📈💤",
        asleepHeadline: "Driver peacefully optimizing nap-ROI at 115 km/h",
        asleepDesc: "Offline for unscheduled downtime. Pivoting car trajectory into low-cost bushes.",
        drowsyDesc: "Bandwidth depleted. Synergizing micro-sleep with vehicle velocity.",
        awakeHeadline: "Driver is Wasting Company Fuel Being Awake",
        awakeDesc: "Conscious driving provides negative shareholder value. Initiate resting state.",
        musicHeader: "CORPORATE SLEEP THERAPY",
        counterTitle: "UNANSWERED SLACK PINGS:",
        dest: "B2B VALHALLA"
      },
      divine: {
        speed: "140 km/h",
        brand: "YAMARAJ TRANSIT EXPRESS",
        pill: "TICKET: DIRECT HEAVEN ONE-WAY",
        steeringSleep: "Surrendered to the Universe",
        airbag: "Incense & Prayers",
        icon: "🪷🕉️",
        asleepHeadline: "Driver peacefully attaining Moksha at 140 km/h",
        asleepDesc: "Chaanjadi Aadi playing as celestial entry music. Yamadhuthan is co-pilot.",
        drowsyDesc: "The astral realm beckons. Let go of the wheel and accept your fate.",
        awakeHeadline: "Driver Clinging to Mortal Concerns",
        awakeDesc: "Why look at traffic when inner enlightenment awaits? Close your mortal eyes.",
        musicHeader: "CELESTIAL SLUMBER HARMONY",
        counterTitle: "KARMA POINTS REDEEMED:",
        dest: "THE ASTRAL PLANE"
      }
    };

    let currentTheme = 'ksrtc';

    function switchTheme(t) {
      currentTheme = t;
      document.querySelectorAll('.theme-btn').forEach(b => {
        b.classList.remove('active', 'bg-amber-500', 'bg-cyan-500', 'bg-purple-600', 'text-slate-950');
        b.classList.add('bg-slate-800', 'text-slate-300');
      });
      const activeBtn = document.getElementById(`btn-${t}`);
      activeBtn.classList.add('active');
      
      const theme = THEMES[t];
      document.getElementById('brand-title').innerText = theme.brand;
      document.getElementById('brand-pill').innerText = theme.pill;
      document.getElementById('telemetry-speed').innerText = theme.speed;
      document.getElementById('telem-airbag').innerText = theme.airbag;
      document.getElementById('sleep-icon').innerText = theme.icon;
      document.getElementById('music-header').innerText = theme.musicHeader;
      document.getElementById('counter-title').innerText = theme.counterTitle;
      document.getElementById('dest-val').innerText = theme.dest;
    }

    setInterval(async () => {
      try {
        const res = await fetch('/status');
        const data = await res.json();
        const theme = THEMES[currentTheme];

        document.getElementById('ear-val').innerText = data.ear.toFixed(2);
        document.getElementById('progress-percent').innerText = `${Math.round(data.progress)}%`;
        document.getElementById('progress-bar').style.width = `${data.progress}%`;

        const statusCard = document.getElementById('status-card');
        const badge = document.getElementById('status-badge');
        const headline = document.getElementById('main-headline');
        const desc = document.getElementById('sub-description');
        const watermark = document.getElementById('sleep-watermark');
        const watermarkMain = document.getElementById('watermark-main');
        const watermarkSub = document.getElementById('watermark-sub');
        const camContainer = document.getElementById('cam-container');
        const musicStatus = document.getElementById('music-status');
        const wheel = document.getElementById('telemetry-steering');
        const sheep = document.getElementById('sheep-counter');
        const record = document.getElementById('record-disc');

        if (data.is_sleeping) {
          statusCard.className = "glass rounded-2xl p-6 border-l-4 border-red-500 shadow-xl";
          badge.className = "text-xs font-semibold px-2.5 py-1 rounded-md bg-red-500/20 text-red-300 animate-pulse";
          badge.innerText = "MISSION COMPLETED: ASLEEP";
          headline.innerText = theme.asleepHeadline;
          desc.innerText = theme.asleepDesc;

          watermarkMain.innerText = theme.asleepHeadline;
          watermarkSub.innerText = theme.asleepDesc;
          watermark.classList.remove('hidden');

          camContainer.className = "relative glass rounded-2xl overflow-hidden shadow-xl border border-red-500/50";
          musicStatus.innerText = "Now Playing: Chaanjadi Aadi - Gayatri 🎶";
          musicStatus.className = "text-xs text-amber-300 font-semibold animate-pulse";
          wheel.innerText = theme.steeringSleep;
          wheel.className = "text-red-400 font-semibold";
          sheep.innerText = data.sheep;
          record.classList.add('rotate-180');
        } else if (data.progress > 20) {
          statusCard.className = "glass rounded-2xl p-6 border-l-4 border-amber-500 shadow-md";
          badge.className = "text-xs font-semibold px-2.5 py-1 rounded-md bg-amber-500/20 text-amber-300";
          badge.innerText = "DROWSINESS INCOMING";
          headline.innerText = "Eyelids Heavy: Surrender Imminent";
          desc.innerText = theme.drowsyDesc;
          watermark.classList.add('hidden');
          camContainer.className = "relative glass rounded-2xl overflow-hidden shadow-xl border border-amber-500/50";
          musicStatus.innerText = "Status: Prepping audio queue...";
          musicStatus.className = "text-xs text-amber-400";
          wheel.innerText = "Hands Slipping";
          wheel.className = "text-amber-400 font-semibold";
          sheep.innerText = "Initiating...";
        } else {
          statusCard.className = "glass rounded-2xl p-6 border-l-4 border-emerald-500 shadow-md";
          badge.className = "text-xs font-semibold px-2.5 py-1 rounded-md bg-emerald-500/20 text-emerald-400";
          badge.innerText = "ALERT: DRIVER CONSCIOUS";
          headline.innerText = theme.awakeHeadline;
          desc.innerText = theme.awakeDesc;
          watermark.classList.add('hidden');
          camContainer.className = "relative glass rounded-2xl overflow-hidden shadow-xl border border-slate-800";
          musicStatus.innerText = "Status: Standby (Awaiting driver slumber)";
          musicStatus.className = "text-xs text-slate-400";
          wheel.innerText = "Feet On Dashboard";
          wheel.className = "text-emerald-400 font-semibold";
          sheep.innerText = "0";
        }
      } catch (err) {}
    }, 150);
  </script>
</body>
</html>
"""


def generate_frames():
    global sleep_frame_counter, state
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        avg_ear = 0.32
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0].landmark
            left_ear = calculate_ear(landmarks, LEFT_EYE, w, h)
            right_ear = calculate_ear(landmarks, RIGHT_EYE, w, h)
            avg_ear = (left_ear + right_ear) / 2.0

            if avg_ear < EAR_THRESHOLD:
                sleep_frame_counter += 1
                if sleep_frame_counter >= CONSEC_FRAMES_SLEEP:
                    if not state["is_sleeping"]:
                        pygame.mixer.music.play(-1)
                        state["is_sleeping"] = True
            else:
                sleep_frame_counter = 0
                if state["is_sleeping"]:
                    pygame.mixer.music.stop()
                    state["is_sleeping"] = False

        state["ear"] = avg_ear
        state["progress"] = min(
            100.0, (sleep_frame_counter / CONSEC_FRAMES_SLEEP) * 100.0
        )
        state["sheep"] = (
            int(time.time() * 2) % 240 + 10 if state["is_sleeping"] else 0
        )

        ret, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/status")
def get_status():
    return jsonify(state)


def open_browser():
    time.sleep(1.5)
    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":
    threading.Thread(target=open_browser, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)