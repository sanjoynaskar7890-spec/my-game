[app]
title = Hyper Shift: Ultra Pro Max
package.name = hypershift
package.domain = org.game
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,pygame

orientation = portrait
fullscreen = 0
android.permissions = INTERNET

# --- Crucial Fixes for Toolchain Error ---
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_version = 25b
android.accept_sdk_license = True

ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master
ios.ios_deploy_url = https://github.com/tcentaur/ios-deploy
ios.ios_deploy_branch = master
