FROM python:3.11

WORKDIR /sil

# Copy and install dependencies
COPY requirements.txt .

RUN pip install -r requirements.txt

# Copy the Palantiri backend source code
COPY ./src ./src
COPY ./assets ./assets

# Expose the SIL API port
EXPOSE 5000
ENV PYTHONPATH=/sil:/sil/assets
CMD ["python", "/sil/src/__main__.py"]
