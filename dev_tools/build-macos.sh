# NB! YOU CAN BUILD FOR MACOS **ONLY** UNDER MACOS - USE PYTHON 3.11.X

# root directory
cd ..  # /

# venv
source venv/Scripts/activate

# output directory + cleanup
mkdir -p dist
rm -rf dist/*

# !! actual build !!
pyinstaller ./src/main.py --noconfirm --name ow-league-tokens --icon=".\assets\icon.icns" --runtime-hook="./hooks/use_lib.py"

# make 'lib' structure
cd dist  # /dist
mv ow-league-tokens lib
mkdir ow-league-tokens
mv lib ow-league-tokens/lib
cd ow-league-tokens  # /dist/ow-league-tokens

# those files are needed (in root directory) for the app to start
mv lib/ow-league-tokens .
mv lib/base_library.zip .
mv lib/lib-dynload .
mv lib/Python .

cd ..  # /dist
zip -9 -rXq ow-league-tokens_macOS.zip ow-league-tokens
