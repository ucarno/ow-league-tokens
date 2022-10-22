call ..\venv\Scripts\activate
call cd ..
call pyinstaller main.py --noconfirm --onefile --name OverwatchTokenFarmer --runtime-hook=".\hooks\use_lib.py"
pause
