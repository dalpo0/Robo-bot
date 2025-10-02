#!/bin/bash

echo "🤖 Setting up Telegram Custom Bot..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create environment file
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ Please edit .env file with your BOT_TOKEN from @BotFather"
else
    echo "✅ .env file already exists"
fi

echo "🎉 Setup complete!"
echo "🚀 To start the bot:"
echo "   source venv/bin/activate"
echo "   python scripts/run_all.py"
