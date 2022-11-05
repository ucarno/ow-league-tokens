cd ..
source venv/Scripts/activate

mkdir -p dist
cd dist
rm -r *

cd ..
pyinstaller .\\src\\main.py --noconfirm --name OverwatchTokenFarmer --runtime-hook=".\hooks\use_lib.py"

cd dist
mv OverwatchTokenFarmer lib
mkdir OverwatchTokenFarmer

mv lib OverwatchTokenFarmer/lib
cd OverwatchTokenFarmer

mv lib/OverwatchTokenFarmer.exe .
mv lib/python310.dll .
mv lib/base_library.zip .
echo "OverwatchTokenFarmer.exe nomenu && pause" > Start_Without_Menu.bat

cd ..
powershell Compress-Archive OverwatchTokenFarmer OverwatchTokenFarmer.zip
