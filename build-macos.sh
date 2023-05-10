# NB! YOU CAN BUILD FOR MAC OS **ONLY** UNDER MAC OS

source venv/Scripts/activate

mkdir -p dist
cd dist
rm -r *

cd ..
pyinstaller ./src/main.py --noconfirm --name ow-league-tokens --runtime-hook=".\hooks\use_lib.py"

cd dist
mv ow-league-tokens lib
mkdir ow-league-tokens

mv lib ow-league-tokens/lib
cd ow-league-tokens

mv lib/ow-league-tokens .
mv lib/Python .
mv lib/base_library.zip .
echo "ow-league-tokens --nomenu" > Start_Without_Menu.command

cd ..
zip -9 -rXq ow-league-tokens_MacOS.zip ow-league-tokens
