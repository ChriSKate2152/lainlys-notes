# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /data

ENV DB_PATH=/data/user_notes.db

VOLUME ["/data"]

# Expose any necessary ports (none for Discord bot, but optional)
# EXPOSE 80

# Define environment variables if needed (e.g., for config)
# ENV TOKEN=your-discord-token

# Run the bot
CMD ["python", "noter.py"] 