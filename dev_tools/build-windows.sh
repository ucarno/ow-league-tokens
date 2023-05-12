# NB! YOU CAN BUILD FOR WINDOWS **ONLY** UNDER WINDOWS - USE PYTHON 3.11.X

# root directory
cd ..  # /

# venv
source venv/Scripts/activate

# output directory + cleanup
mkdir -p dist
rm -rf dist/*

# !! actual build !!
pyinstaller .\\src\\main.py --noconfirm --name ow-league-tokens --icon="./assets/icon.ico" --runtime-hook=".\hooks\use_lib.py"

# make 'lib' structure
cd dist  # /dist
mv ow-league-tokens lib
mkdir ow-league-tokens
mv lib ow-league-tokens/lib
cd ow-league-tokens  # /dist/ow-league-tokens

# those files are needed (in root directory) for the app to start
mv lib/ow-league-tokens.exe .
mv lib/base_library.zip .
mv lib/python311.dll .

echo "ow-league-tokens.exe --nomenu" > Start_Without_Menu.bat

cd ..  # /dist
powershell Compress-Archive ow-league-tokens ow-league-tokens_Windows.zip
