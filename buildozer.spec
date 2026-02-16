[app]

title = ZipBloat
package.name = zipbloat

package.domain = org.zipbloat

source.dir = .
source.files = %(source.dir)s/main.py,%(source.dir)s/ZipBloat_Android.py

source.dir_ext = include/

source.include_exts = py,png,jpg,kv,atlas

version = 1.0.0

requirements = python3,kivy,pyjnius,android

# presplash.filename = %(source.dir)s/presplash.png

# icon.filename = %(source.dir)s/icon.png

orientation = portrait

fullscreen = 0

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33

android.minapi = 21

android.ndk = 25b

android.archs = arm64-v8a,armeabi-v7a

android.buildtools = 33.0.0

android.accepts_license = True

[buildozer]

log_level = 2

warn_on_root = 1
