FROM python:3.8.10

ENV PYTHONPATH="${PYTHONPATH}:/app"

RUN \
    # Update pip
    pip install --upgrade pip

# Install our common python requirements
WORKDIR /app/
COPY requirements.txt /app/
RUN \
    # Install requirements
    pip install -r requirements.txt
