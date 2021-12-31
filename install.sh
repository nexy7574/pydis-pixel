echo "Cloning repo..."
git clone https://github.com/EEKIM10/pydis-pixel > /dev/null || exit 1
cd pydis-pixel || exit 1
echo "Creating virtual environment..."
python3 -m venv venv || exit 2
. ./venv/bin/activate
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt > /dev/null 2>/dev/null || exit 2
echo "Downloading sample image..."
wget https://cdn.discordapp.com/embed/avatars/0.png -O sample-image.png || echo "Failed to download ample image."
echo "Installed! Please see python3 main.py --help, and get started!"
