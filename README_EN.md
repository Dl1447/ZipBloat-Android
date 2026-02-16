# ZipBloat-Android

<div align="center">

![ZipBloat](ZipBloat.png)

**A Simple and Easy-to-Use ZIP File Size Enlarger - Android Version**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/Platform-Android-green.svg)](https://www.android.com/)

English | [简体中文](README.md)

</div>

---

## Project Overview

ZipBloat-Android is a powerful ZIP file size enlarger for Android devices. It helps you quickly generate ZIP files of specified sizes. Supports multiple enlargement methods, including ZIP bomb mode, suitable for testing, learning, and various other scenarios.

## Features

### Core Features

- 📁 **4 Enlargement Methods**:
  - Add Empty Blocks: Add大量 empty files to ZIP
  - Nested ZIP: Create multi-layer nested ZIP structure
  - Append Garbage Data: Append garbage data at the end of ZIP file
  - ZIP Bomb Mode: Generate small ZIP files that explode when extracted

- 🌍 **Multi-language Support**: Chinese and English interface, one-click switch

- 📊 **Real-time Progress Display**: Progress bar with percentage, real-time generation progress

- ⚡ **Debounce Operations**: Prevent rapid multiple clicks from triggering tasks

- ❌ **Cancel Support**: Cancel operation anytime during generation

- 📖 **Built-in Help**: Detailed usage instructions and about information

### Android Features

- 📱 **Touch-Optimized Interface**: Based on Kivy framework, designed specifically for mobile devices

- 🔐 **Dynamic Permission Management**: Automatically request storage permissions

- 📂 **Mobile File Picker**: Use Android Storage Access Framework

- 💾 **Flexible Storage Options**: Support internal storage and external storage (SD card)

## Quick Start

### Method 1: Use Pre-compiled APK (Recommended)

1. Download the latest APK file from the project releases page
2. Install the APK on your Android device
3. Grant storage permissions
4. Open the app and start using it

### Method 2: Build APK Yourself

#### Environment Setup

```bash
# Install dependencies
pip install buildozer
pip install -r requirements.txt
```

#### Build APK

```bash
# Initialize buildozer (first time use)
buildozer init

# Build debug APK
buildozer android debug

# Build release APK
buildozer android release

# Generated APK is located in bin/ directory
```

### Method 3: Run Directly on Android Device

1. Install [Kivy Launcher](https://play.google.com/store/apps/details?id=org.kivy.pygame) app
2. Copy project files to `/sdcard/kivy/zipbloat/` directory on Android device
3. Launch the app from Kivy Launcher

## Usage Guide

1. **Select Original ZIP File**: Click "Select File" button to choose the ZIP file to enlarge
2. **Set Output Path**: Click "Select Output" button to set the output file path
3. **Set Target Size**: Enter the target size to enlarge to (GB)
4. **Select Enlargement Method**: Choose the appropriate enlargement method from the dropdown menu
5. **Click Start Generation**: Wait for generation to complete
6. **View Results**: Success message will be displayed after generation completes

## Enlargement Methods

| Method | Description | Use Case |
|--------|-------------|----------|
| Add Empty Blocks | Add大量 empty files to ZIP | Regular testing |
| Nested ZIP | Create multi-layer nested ZIP structure | Need small size with large extraction |
| Append Garbage Data | Append garbage data at the end of ZIP file | Most stable and reliable |
| ZIP Bomb Mode | Generate small ZIP that explodes when extracted | Test extraction protection |

## Project Structure

```
ZipBloat-Android/
├── ZipBloat_Android.py      # Android main program
├── main.py                  # Android entry file
├── buildozer.spec           # Buildozer configuration file
├── requirements.txt         # Python dependencies
├── android/                 # Android specific modules
│   ├── storage.py           # Storage access wrapper
│   └── permissions.py       # Permission management wrapper
├── README.md                # Project documentation (Chinese)
├── README_EN.md             # Project documentation (English)
├── LICENSE                  # Open source license
└── ZipBloat.png             # App icon
```

## Tech Stack

- **GUI Framework**: Kivy 2.0+
- **Packaging Tool**: Buildozer
- **Python Version**: 3.7+
- **Main Features**: Touch-optimized interface, mobile file picker
- **Permission Management**: Dynamic storage permission requests
- **File Access**: Use Android Storage Access Framework

## System Requirements

- Android 5.0+ (API 21+)
- Sufficient storage space
- Storage permissions

## Important Notes

- ⚠️ Target size is recommended to be set between 1-20GB, larger sizes will take longer
- ⚠️ Ensure output path has write permissions
- ⚠️ Use ZIP bomb mode with caution, only for testing purposes
- ⚠️ First run requires granting storage permissions
- ⚠️ Recommended to generate large files in WiFi environment to avoid mobile data usage
- ⚠️ Ensure device has sufficient battery when generating large files
- ⚠️ Recommended to use external storage (SD card) for storing large files
- ⚠️ App may be killed by system when running in background, recommended to keep app in foreground

## FAQ

**Q: App cannot open files?**
A: Please ensure storage permissions are granted, check app permissions in settings

**Q: App crashes during generation?**
A: May be due to insufficient memory, try reducing target size or closing other apps

**Q: Cannot find generated files?**
A: Generated files are saved at the location specified when selecting output path, use file manager to search

**Q: APK installation fails?**
A: Please ensure "Unknown Sources" app installation is enabled, allow installation of unknown apps in settings

**Q: Error when compiling APK?**
A: Please ensure all dependencies are installed and buildozer.spec configuration is correct

## Development Guide

### Local Testing

Test Android version interface on computer:
```bash
pip install kivy
python ZipBloat_Android.py
```

### Modify buildozer Configuration

Edit `buildozer.spec` file to customize APK:
- Modify app name, package name
- Adjust Android API version
- Add additional permissions
- Customize app icon and splash screen

### Add New Features

1. Modify GUI interface in `ZipBloat_Android.py`
2. Add business logic in `ZipBloatLogic` class
3. Update `buildozer.spec` if new dependencies are needed
4. Rebuild APK for testing

## Contributing

Welcome to submit Issues and Pull Requests to improve this project!

1. Fork this project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the [MIT License](LICENSE)

## Author Information

- **Author**: Geekline
- **Website**: [geekline.pages.dev](https://geekline.pages.dev)
- **Version**: 1.0

## Disclaimer

This tool is only for legal testing and learning purposes. Do not use it for any malicious purposes. The author assumes no responsibility for any consequences caused by using this tool.

---

<div align="center">

**If this project helps you, please give it a ⭐️ Star to support!**

Made with ❤️ by Geekline

</div>