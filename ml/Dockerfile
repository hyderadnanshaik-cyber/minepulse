FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and models
COPY . .

# Generate dataset and train model if not present
RUN python data/synthetic/generate_dataset.py && python train.py

# Default execution runs inference engine or prediction worker
CMD ["python", "predict.py", "--serve"]
