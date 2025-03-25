@echo off
echo Downloading FFmpeg...

:: Create a directory for FFmpeg if it doesn't exist
if not exist "ffmpeg" mkdir ffmpeg

:: Use PowerShell to download FFmpeg
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'}"

echo Extracting FFmpeg...
powershell -Command "& {Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'ffmpeg' -Force}"

:: Move the ffmpeg.exe file to the current directory
echo Setting up FFmpeg...
copy "ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe" "ffmpeg.exe"

:: Clean up
echo Cleaning up...
rmdir /S /Q "ffmpeg"
del "ffmpeg.zip"

echo FFmpeg setup complete!
pause 