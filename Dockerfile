FROM python:3.11

WORKDIR /app

# Copy and install dependencies
COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy the Palantiri backend source code
COPY ./src ./src

# Expose the SIL API port
EXPOSE 5000

CMD ["python", "./src/app/main.py"]