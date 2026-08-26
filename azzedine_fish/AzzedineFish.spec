# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
datas, binaries, hiddenimports = collect_all('customtkinter')
a = Analysis(['main.py'], pathex=[], binaries=binaries, datas=datas,
             hiddenimports=hiddenimports + ['PIL._tkinter_finder','reportlab','qrcode','openpyxl'],
             hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name='AzzedineFish', debug=False,
          bootloader_ignore_signals=False, strip=False, upx=True, console=False,
          disable_windowed_traceback=False, argv_emulation=False, target_arch=None,
          codesign_identity=None, entitlements_file=None, icon=None)

