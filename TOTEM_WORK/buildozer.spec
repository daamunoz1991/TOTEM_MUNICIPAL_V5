[app]

title = Totem Municipal
package.name = totemmunicipal
package.domain = cl.proyectoapt

source.dir = client
source.include_exts = py,png,jpg,jpeg,kv,atlas,ttf
source.exclude_patterns = screens/admin.py

version = 3.2

requirements = python3,kivy,requests,androidstorage4kivy

orientation = all
fullscreen = 1

android.permissions = INTERNET,CAMERA

android.api = 36
android.minapi = 24
android.ndk = 29
android.archs = arm64-v8a, armeabi-v7a

android.allow_backup = False

p4a.branch = develop

[buildozer]

log_level = 2
warn_on_root = 1
