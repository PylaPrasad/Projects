[app]
title = YouTube Downloader
package.name = ytdownloader
package.domain = org.ytdownloader
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,yt_dlp,ffmpeg-python,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk_path = /home/runner/android-sdk/ndk/25.1.8937393
android.sdk_path = /home/runner/android-sdk
android.sdk_build_tools = 34.0.0
android.archs = arm64-v8a  # Only arm64 for better compatibility
android.ndk_api = 21
copy_libs = 1
allow_backup = 1
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
android.accept_sdk_license = True
