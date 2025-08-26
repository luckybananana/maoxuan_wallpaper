@echo off
echo === 开始打包 WallpaperApp ===

REM 删除旧的打包文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist WallpaperApp.spec del /q WallpaperApp.spec

REM 使用 PyInstaller 打包
pyinstaller -F -w -n WallpaperApp ^
    --add-data "simhei.ttf;." ^
    --add-data "mao_quotes.json;." ^
    --add-data "tray.ico;." ^
    --icon=tray.ico ^
    main.py

echo === 打包完成！可执行文件在 dist\WallpaperApp.exe ===
pause
