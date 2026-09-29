[app]

# (str) Title of your application
title = Hyper Shift

# (str) Package name
package.name = hypershift

# (str) Package domain (needed for android packaging)
package.domain = org.errorgamer

# (list) Source files to include (let it include py and other assets)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application directory relative to the spec file
source.dir = .

# (list) Application requirements
# Add python and pygame here
requirements = python3,pygame,cython

# (str) Supported orientations
orientation = portrait

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Automatically accept Android SDK license
android.accept_sdk_license = True

# (list) Permissions
android.permissions = INTERNET

# (str) Fullscreen setting
fullscreen = 1

version = 1.0
