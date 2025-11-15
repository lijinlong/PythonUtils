@Echo off
pyinstaller --onefile --windowed --add-data "taskcfg.json;." --add-data "pic00.png;." --add-data "DejaVuSans.ttf;." --add-data "DejaVuSans-Bold.ttf;." gui_exam.py

pause
