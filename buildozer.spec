[app]
title = YouTube Downloader
package.name = ytdownloader
package.domain = org.ytdownloader
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
# Ensure yt_dlp is listed here, as it's used in main.py
# ffmpeg-python is often not strictly needed as yt_dlp manages ffmpeg itself.
# certifi is important for SSL certificate verification.
requirements = python3,kivy,yt_dlp,certifi
orientation = portrait
fullscreen = 0
# Permissions for internet access and external storage writes (for downloads)
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
# Target Android API level. Must match a platform installed by sdkmanager in .yml
android.api = 33
# Minimum Android API level
android.minapi = 21
# Removed android.ndk_path: Let Buildozer handle NDK discovery based on android.ndk
# It's less brittle for CI/CD environments.
# Specify the NDK version. Buildozer will download this if not found.
# "25b" is commonly used to refer to NDK 25.1.8937393.
android.ndk = 25b
# android.sdk_path: This path is crucial and must match ANDROID_SDK_ROOT in your .yml
# It tells Buildozer where your Android SDK is located.
android.sdk_path = /home/runner/android-sdk
# Android Build Tools version. Must match what's installed by sdkmanager in .yml.
android.sdk_build_tools = 34.0.0
# Target CPU architectures
android.archs = arm64-v8a
# NDK API level (often same as minapi)
android.ndk_api = 21
copy_libs = 1
allow_backup = 1
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
# This is handled by `yes | sdkmanager --licenses` in the .yml, so it's redundant but harmless.
android.accept_sdk_license = True
