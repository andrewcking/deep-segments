# -*- mode: python -*-
a = Analysis(['main.py'],
             pathex=['C:\\Users\\Andrew\\PycharmProjects\\DeepSegments'],
             datas=[('circle.png', '.'),('color.png', '.'),('list.png', '.'),('load.png', '.'),('minus.png', '.'),('plus.png', '.'),('run.png', '.'),('save.png', '.'),('splash_mini.png', '.'),('splash.png', '.'),('zoomin.png', '.'),('zoomout.png', '.'),('libmkl_avx2.dylib', '.'),('libmkl_mc.dylib', '.'),('classlabels.txt', '.'),('ranfor.pkl', '.')],
             hiddenimports=['pywt._extensions._cwt'],
             hookspath=None,
             runtime_hooks=None)


import os
import glob
block_cipher = None
import sys
sys.setrecursionlimit(10000)


def extra_datas(path):
    def recursive_glob(path, files):
        for file_path in glob.glob(path):
            if os.path.isfile(file_path):
                files.append(os.path.join(os.getcwd(), file_path))
            recursive_glob('{}/*'.format(file_path), files)

    files = []
    extra_datas = []

    if os.path.isfile(path):
        files.append(os.path.join(os.getcwd(), path))
    else:
        recursive_glob('{}/*'.format(path), files)

    for f in files:
        extra_datas.append((f.split('kano-burners')[1][1:], f, 'DATA'))
    return extra_datas

a.datas += extra_datas(os.path.join(os.getcwd(), '..', '..', 'res'))
a.datas += extra_datas(os.path.join(os.getcwd(), '..', '..', 'win'))
a.datas += extra_datas(os.path.join(os.getcwd(), '..', '..', 'DISCLAIMER'))


pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='DeepSegments.exe',
          debug=False,
          strip=False,
          upx=True,
          console=True , icon='icon.ico')

coll = COLLECT(exe,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          strip=False,
          upx=True,
          name='DeepSegments')
