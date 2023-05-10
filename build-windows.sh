# NB! YOU CAN BUILD FOR WINDOWS **ONLY** UNDER WINDOWS

source venv/Scripts/activate

mkdir -p dist
cd dist
rm -r *

cd ..
pyinstaller .\\src\\main.py --noconfirm --name ow-league-tokens --runtime-hook=".\hooks\use_lib.py"

cd dist
mv ow-league-tokens lib
mkdir ow-league-tokens

mv lib ow-league-tokens/lib
cd ow-league-tokens

mv lib/ow-league-tokens.exe .
mv lib/python311.dll .
mv lib/base_library.zip .
echo "ow-league-tokens.exe --nomenu" > Start_Without_Menu.bat

cd ..
powershell Compress-Archive ow-league-tokens ow-league-tokens_Windows.zip
