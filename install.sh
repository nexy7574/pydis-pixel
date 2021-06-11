echo "Cloning repo..."
git clone https://github.com/EEKIM10/pydis-pixel > /dev/null
cd pydis-pixel
echo "Creating virtual environment..."
python3 -m venv venv > /dev/null&& \
. ./venv/bin/activate && \
echo "Installing dependencies..." && \
python3 -m pip install -r requirements.txt > /dev/null
echo "Downloading sample image..."
wget https://cdn.discordapp.com/embed/avatars/0.png -O sample-image.png
echo "Installed! Please see python3 main.py --help, and get started!"
