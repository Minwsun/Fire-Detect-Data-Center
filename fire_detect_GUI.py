import tkinter as tk
from tkinter import ttk
import serial
import threading
import queue
import joblib
import pandas as pd
import os
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import time
import re

model = joblib.load('fire_detection_model.pkl')

ser = serial.Serial('COM5', 9600)

data_queue = queue.Queue()

root = tk.Tk()
root.title("Fire Detection Dashboard")
root.geometry("900x700")

frame_data = ttk.LabelFrame(root, text="Sensor Data")
frame_data.pack(fill="x")

labels = {
    "T1": tk.StringVar(),
    "H1": tk.StringVar(),
    "T2": tk.StringVar(),
    "H2": tk.StringVar(),
    "CO2": tk.StringVar(),
    "PM2.5": tk.StringVar(),
    "PM10": tk.StringVar(),
    "Result": tk.StringVar()
}

for i, (key, var) in enumerate(labels.items()):
    if key != "Result":
        ttk.Label(frame_data, text=f"{key}:").grid(row=i//4, column=(i%4)*2, sticky='w')
        ttk.Label(frame_data, textvariable=var).grid(row=i//4, column=(i%4)*2+1, sticky='w')

label_result = tk.Label(root, textvariable=labels["Result"], font=("Arial", 24, "bold"))
label_result.pack(anchor='ne', padx=20, pady=10)

frame_plot = ttk.LabelFrame(root, text="Live Charts")
frame_plot.pack(fill="both", expand=True)

fig = Figure(figsize=(10, 6))
ax_temp = fig.add_subplot(311)
ax_humid = fig.add_subplot(312)
ax_other = fig.add_subplot(313)

lines = {
    "T1": ax_temp.plot([], [], label="T1")[0],
    "T2": ax_temp.plot([], [], label="T2")[0],
    "H1": ax_humid.plot([], [], label="H1")[0],
    "H2": ax_humid.plot([], [], label="H2")[0],
    "CO2": ax_other.plot([], [], label="CO2")[0],
    "PM2.5": ax_other.plot([], [], label="PM2.5")[0],
    "PM10": ax_other.plot([], [], label="PM10")[0]
}

for ax in [ax_temp, ax_humid, ax_other]:
    ax.legend(loc="upper right")
    ax.grid()

canvas = FigureCanvasTkAgg(fig, master=frame_plot)
canvas.get_tk_widget().pack(fill="both", expand=True)

history = {
    "time": [],
    "T1": [],
    "T2": [],
    "H1": [],
    "H2": [],
    "CO2": [],
    "PM2.5": [],
    "PM10": []
}

os.makedirs("logs", exist_ok=True)

def extract_float(value):
    try:
        return float(re.findall(r"[-+]?\d*\.\d+|\d+", value)[0])
    except:
        return 0.0
    
def read_serial():
    while True:
        try:
            line = ser.readline().decode(errors='ignore').strip()
            if "T1:" in line:
                values = {}
                for _ in range(7):  
                    l = line if _ == 0 else ser.readline().decode(errors='ignore').strip()
                    if "T1:" in l:
                        values["T1"] = extract_float(l.split("T1:")[1].split("H1:")[0])
                        values["H1"] = extract_float(l.split("H1:")[1])
                    elif "T2:" in l:
                        values["T2"] = extract_float(l.split("T2:")[1].split("H2:")[0])
                        values["H2"] = extract_float(l.split("H2:")[1])
                    elif "CO2:" in l:
                        values["CO2"] = extract_float(l.split("CO2:")[1])
                    elif "PM2.5:" in l:
                        values["PM2.5"] = extract_float(l.split("PM2.5:")[1])
                    elif "PM10" in l:
                        values["PM10"] = extract_float(l.split("PM10")[-1])
                data_queue.put(values)
        except Exception as e:
            print("Serial error:", e)

threading.Thread(target=read_serial, daemon=True).start()

def popup_fire_alert():
    popup = tk.Toplevel()
    popup.title("Fire Alert!")
    popup.geometry("300x150")
    popup.configure(bg='red')
    tk.Label(popup, text="FIRE DETECTED!!!", font=("Arial", 18, "bold"), fg="white", bg='red').pack(expand=True)
    tk.Button(popup, text="Dismiss", command=popup.destroy, font=("Arial", 12)).pack(pady=10)

fire_alert_shown = False

def update_gui():
    global fire_alert_shown
    while not data_queue.empty():
        data = data_queue.get()
        for k in labels:
            if k != "Result" and k in data:
                labels[k].set(f"{data[k]:.2f}")

        prediction = None
        try:
            df = pd.DataFrame([[data["T1"], data["H1"], data["T2"], data["H2"],
                                data["CO2"], data["PM2.5"], data["PM10"]]],
                              columns=["T1", "H1", "T2", "H2", "CO2", "PM2.5", "PM10"])
            prediction = model.predict(df)[0]

            if prediction == 1:
                labels["Result"].set("🔥 Fire Detected!")
                label_result.config(fg="red")
                if not fire_alert_shown:
                    fire_alert_shown = True
                    popup_fire_alert()
            else:
                labels["Result"].set("✅ Safe")
                label_result.config(fg="green")
                fire_alert_shown = False
        except Exception as e:
            labels["Result"].set("❓ Model Error")
            label_result.config(fg="orange")

        history["time"].append(time.time())
        for k in data:
            history[k].append(data[k])
        if len(history["time"]) > 100:
            for k in history:
                history[k] = history[k][-100:]

        t = [x - history["time"][0] for x in history["time"]]
        for key in lines:
            lines[key].set_data(t, history[key])

        for ax in [ax_temp, ax_humid, ax_other]:
            ax.relim()
            ax.autoscale_view()

        canvas.draw()

        log_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "T1": data["T1"],
            "H1": data["H1"],
            "T2": data["T2"],
            "H2": data["H2"],
            "CO2": data["CO2"],
            "PM2.5": data["PM2.5"],
            "PM10": data["PM10"],
            "Prediction": "Fire" if prediction == 1 else "Safe" if prediction == 0 else "Unknown"
        }
        log_file = f"logs/fire_log_{datetime.now().strftime('%Y-%m-%d')}.csv"
        pd.DataFrame([log_data]).to_csv(log_file, mode='a', header=not os.path.exists(log_file), index=False)

    root.after(1000, update_gui)

update_gui()
root.mainloop()
