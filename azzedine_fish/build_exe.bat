@echo off
chcp 65001 > nul
python -m pip install -r requirements.txt
python -m PyInstaller --clean --noconfirm AzzedineFish.spec
echo.
echo تم إنشاء البرنامج داخل dist\AzzedineFish.exe
pause

