[app]

# (str) Title of your application
title = Hyper-Shift-extreme

# (str) Package name
package.name = hypershiftextreme

# (str) Package domain (needed for android packaging)
package.domain = org.errorgamer

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Application directory relative to the spec file
source.dir = .

# (list) Application requirements
requirements = python3==3.10.14,hostpython3==3.10.14,pygame


# (str) Custom icon
#icon.filename = %(source.dir)s/1000079253.png

# (str) Supported orientations
orientation = portrait

# (int) Target Android API
android.api = 34

# (int) Minimum API your APK will support
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25b

# (list) Application architectures
android.archs = armeabi-v7a

# (bool) Automatically accept Android SDK license
android.accept_sdk_license = True

# (str) Version of your application
version = 1.0

# (list) Permissions
android.permissions = INTERNET

# (str) Fullscreen setting
fullscreen = 1

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2
