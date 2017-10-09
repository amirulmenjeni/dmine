# -*- mode: python -*-

block_cipher = None


a = Analysis(['src/main.py', 'src/spiders/tweet_spider.py', 'src/spiders/reddit_spider.py'],
             pathex=['./src', './py-dependencies', '/home/amenji/git/dmine'],
             binaries=[],
             datas=[('./src/README.md', '.'), ('./src/spiders', './spiders/')],
             hiddenimports=[],
             hookspath=['./hooks'],
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
