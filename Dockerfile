# Use Python 3.10 slim
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy bot code
COPY bot.py .

# Start the bot
CMD ["python", "bot.py"]
