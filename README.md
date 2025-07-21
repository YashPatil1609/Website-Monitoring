# 🛠️ AWS EC2 Docker App Monitor Script

This Python script monitors the availability of a web application running in a Docker container on an AWS EC2 instance. If the app goes down, it automatically sends an alert, restarts the container, and can even reboot the EC2 instance and bring the app back up.

---

## 📦 Libraries Used

- `requests`: To send GET requests to check the app’s HTTP status.
- `smtplib`: For sending email notifications via Gmail SMTP server.
- `os`: To securely fetch email credentials from environment variables.
- `paramiko`: For SSH-based remote Docker container restart.
- `boto3`: AWS SDK to interact with EC2 instances (reboot, get public IP).
- `schedule`: To run the monitor job at regular intervals (every 30 seconds).
- `time`: For sleep control in the scheduler loop.

---

## 🔐 Environment Variables

Make sure you export these before running the script:

- `EMAIL_ADDRESS`: Your Gmail address.
- `EMAIL_PASSWORD`: Your Gmail **App Password** (not your login password).

---

## 🧠 Functions Overview

### `send_notification(body)`
Sends an email alert with the provided message body using Gmail SMTP.

### `restart_application()`
Uses Paramiko to SSH into the EC2 instance and run a Docker command to restart the app container.

### `restart_server()`
Reboots the EC2 instance using Boto3, waits for it to enter a "running" and "ok" health state, then restarts the app container.

### `monitor_application()`
Main logic:
- Sends a GET request to the app URL.
- If it receives anything other than a 200 status code:
  - Sends a warning email.
  - Restarts the container.
- If the server is unreachable:
  - Sends a critical email.
  - Reboots the EC2 instance.
  - Waits for it to become healthy.
  - Restarts the container.

---

## 🔁 Workflow

1. Fetches EC2 public IP using `boto3`.
2. Defines the `monitor_application()` function.
3. Schedules it to run every 30 seconds using `schedule.every(30).seconds.do(...)`.
4. Runs an infinite loop calling `schedule.run_pending()` every second.

---

## ✅ Use Case

Useful for DevOps or backend engineers who want to:
- Ensure an app inside Docker stays up.
- Automate recovery without needing to manually log in.
- Get alerts immediately when downtime happens.

```bash
python monitor.py
```

Now you’ve got a mini self-healing system for your EC2 app.
