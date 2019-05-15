REM <stripall>
rd /s /q __pycahce__
rd /s /q dist
rd /s /q C:\tmp
mkdir c:\tmp
xcopy *.* C:\tmp
C:
cd C:\tmp\
pyinstaller --onefile gpvdm.py --icon=Z:\pub\images\icon.ico
move .\dist\*.exe Z:\pub\
time /t
z:
cd z:\pub\gui
