# Use the official Python image from the Docker Hub
FROM python:3.12.10

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /app
COPY . /app

# Make port 80 available to the world outside this container
EXPOSE 80

ENV PYTHONPATH="${PYTHONPATH}:/app/src"

# Run main.py when the container launches
CMD ["python", "src/api/main.py"]