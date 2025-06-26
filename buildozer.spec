[app]

title = YouTube Downloader
package.name = ytdownloader
package.domain = org.ytdownloader
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,youtube_dl,ffmpeg,certifi
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 31
android.minapi = 21
android.archs = armeabi-v7a,arm64-v8a
android.ndk_api = 21
copy_libs = 1
allow_backup = 1
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
