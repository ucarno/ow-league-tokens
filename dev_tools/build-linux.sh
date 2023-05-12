# NB! YOU CAN BUILD FOR LINUX **ONLY** UNDER LINUX - USE PYTHON 3.11.X

# root directory
cd ..  # /

# venv
source venv/Scripts/activate

# output directory + cleanup
mkdir -p dist
rm -rf dist/*

# !! actual build !!
pyinstaller ./src/main.py --noconfirm --name ow-league-tokens --runtime-hook="./hooks/use_lib.py"

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
mv lib/libpython3.11.so.1.0 .

echo "ow-league-tokens --nomenu" > Start_Without_Menu.sh

cd ..  # /dist
zip -9 -rXq ow-league-tokens_Linux.zip ow-league-tokens
