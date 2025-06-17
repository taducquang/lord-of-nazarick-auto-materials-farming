# 🎣 Android Fishing Bot Automation

This bot automates the farming materials in an Android game using ADB and OpenCV. It works by detecting on-screen cues and tapping/clicking automatically in your Android emulator.

---

## 📦 Requirements

- Python 3.x
- ADB (Android Debug Bridge)
- Android emulator (e.g., MEmu or LDPlayer)

---

## ⚙️ Installation & Setup

### 1. Install an Android Emulator

Install python requirements:
```
pip install opencv-python numpy
```

Download and install your favorite Android emulator:

- **MEmu** – uses ADB port `21503`
- **LDPlayer** – uses ADB port `5555` (sometimes `5554`)

> Launch the emulator, open your game, and navigate to the **fishing event** where it shows the text:  
> **"Tap to cast the rod"**

---

### 2. Edit `materials.py`

Open the file `fishing_bot.py` and edit the following lines to match your emulator's ADB port and the "Tap to Cast" button position:

```
# === ADB config ===
adb_device = "127.0.0.1:21503"  # For MEmu: use 21503, for LDPlayer: use 5555 or 5554
```

You can use "adb devices" command to check your adb port, remember to have adb.exe on your PATH folder.
###  3. Run the Bot

To start the bot, just double-click on run.bat

This will launch the automation and begin detecting the game state and tapping at the right time.

### 🛠️ What does it do?

The list of farming materials the bot can do:
```
Stone
Wood
Crystal
Fur #Fighting monsters
```

Just comment any lines u dont want to farm
