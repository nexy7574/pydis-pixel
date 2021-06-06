git clone https://github.com/EEKIM10/pydis-pixel
cd pydis-pixel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
wget https://cdn.discordapp.com/embed/avatars/0.png -O sample-image.png
python3 main.py