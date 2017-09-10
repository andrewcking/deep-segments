# -*- mode: python -*-
a = Analysis(['main.py'],
             pathex=['C:\\Users\\Andrew\\PycharmProjects\\DeepSegments'],
             datas=[('loading.png', '.'),('circle.png', '.'),('color.png', '.'),('list.png', '.'),('load.png', '.'),('minus.png', '.'),('plus.png', '.'),('run.png', '.'),('save.png', '.'),('splash_mini.png', '.'),('splash.png', '.'),('zoomin.png', '.'),('zoomout.png', '.'),('classlabels.txt', '.'),('preferences.txt', '.'),('ranfor.pkl', '.')],
             hiddenimports=['pywt._extensions._cwt'],
             hookspath=None,
             runtime_hooks=None,
             win_no_prefer_redirects=False,
             win_private_assemblies=False)


import os
block_cipher = None


pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='DeepSegments',
          debug=False,
          strip=False,
          upx=False,
          console=False , icon='icon.ico')

coll = COLLECT(exe,
          a.binaries,
          a.zipfiles,
          a.datas,
          strip=False,
          upx=False,
          name='DeepSegments')
