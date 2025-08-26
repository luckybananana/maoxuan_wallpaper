@echo off
echo === 打包壁纸程序开始 ===

REM 删除旧的打包文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist WallpaperApp.spec del /q WallpaperApp.spec

REM 执行 PyInstaller 打包
pyinstaller -F -w -n WallpaperApp ^
    --add-data "simhei.ttf;." ^
    --add-data "mao_quotes.json;." ^
    --icon=tray.ico ^
    main.py

echo === 打包完成！可执行文件在 dist\WallpaperApp.exe ===
pause
