echo "Cloning repo..."
git clone https://github.com/EEKIM10/pydis-pixel
cd pydis-pixel
echo "Creating virtual environment..."
python3 -m venv venv && \
. ./venv/bin/activate && \
echo "Installing dependencies..." && \
python3 pip install -r requirements.txt
echo "Downloading sample image..."
wget https://cdn.discordapp.com/embed/avatars/0.png -O sample-image.png
echo "Installed! Please see python3 main.py --help, and get started!"