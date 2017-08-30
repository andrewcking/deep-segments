# -*- mode: python -*-

block_cipher = None
import sys
sys.setrecursionlimit(10000)

a = Analysis(['main.py'],
             pathex=['/Users/Andrew/Documents/PycharmProjects/DeepSegments'],
             binaries=[],
             datas=[('circle.png', '.'),('color.png', '.'),('list.png', '.'),('load.png', '.'),('minus.png', '.'),('plus.png', '.'),('run.png', '.'),('save.png', '.'),('splash_mini.png', '.'),('splash.png', '.'),('zoomin.png', '.'),('zoomout.png', '.'),('libmkl_avx2.dylib', '.'),('libmkl_mc.dylib', '.'),('classlabels.txt', '.'),('ranfor.pkl', '.')],
             hiddenimports=['pywt._extensions._cwt'],
             hookspath=[],
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
          name='DeepSegments',
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='icon.icns')
coll = COLLECT(exe,
          a.binaries,
          a.zipfiles,
          a.datas,
          strip=False,
          upx=True,
          name='DeepSegments')
app = BUNDLE(coll,
          name='DeepSegments.app',
          icon='icon.icns',
          bundle_identifier=None,
          info_plist={
             'NSHighResolutionCapable': 'True'
             },
          )
