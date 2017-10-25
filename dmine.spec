# -*- mode: python -*-
import os
import re

block_cipher = None

"""
Getting the scripts.
"""
scripts = []
scripts.append(os.path.join(os.getcwd(), 'src', 'main.py'))
spiders_dir = os.path.join(os.getcwd(), 'src', 'spiders')
for f in os.listdir(os.path.join(spiders_dir)):
    fullpath = os.path.join(spiders_dir, f)
    if os.path.isfile(fullpath) and not re.match('^__', f):
        scripts.append(fullpath)

"""
Getting the paths.
"""
paths = []
paths.append(os.path.join(os.getcwd(), 'src'))
paths.append(os.path.join(os.getcwd(), 'dep-py'))
paths.append(os.path.join(os.getcwd(), 'dep-bin'))

"""
Getting the binaries.
"""
binaries = []
binary_dir = os.path.join(os.getcwd(), 'dep-bin')
for root, dirs, files in os.walk(binary_dir):
    for f in files:
        fullpath = os.path.join(root, f)
        if os.access(fullpath, os.X_OK):
            binaries.append((fullpath, os.path.join('./dep-bin')))

"""
Getting the datas.
"""
datas = []
datas.append((os.path.join(os.getcwd(), 'src', 'spiders'), './spiders'))
datas.append((os.path.join(os.getcwd(), 'dep-bin'), './dep-bin'))

"""
Hooks path.
"""
hookspath=[os.path.join(os.getcwd(), 'hooks')]

a = Analysis(scripts,
             pathex=paths,
             binaries=binaries,
             datas=datas,
             hiddenimports=[],
             hookspath=hookspath,
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='dmine',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='dmine')
