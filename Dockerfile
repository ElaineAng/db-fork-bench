# Use python 3.11
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    protobuf-compiler \
    libpq-dev \
    gcc \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all files
COPY . .

# FIX: Use Python to patch pyproject.toml safely.
# 1. Removes "microbench" dependency.
# 2. Adds "db_setup" to the packages list to satisfy setuptools.
RUN python3 -c "import re, pathlib; \
    p = pathlib.Path('pyproject.toml'); \
    text = p.read_text(); \
    text = text.replace('\"microbench\",', ''); \
    text = re.sub(r'packages\s*=\s*\[.*?\]', 'packages = [\"dblib\", \"microbench\", \"util\", \"db_setup\"]', text, flags=re.DOTALL); \
    p.write_text(text)"

# Install the package
RUN pip install .

# Install gdown manually
RUN pip install gdown

# Set entrypoint
CMD ["/bin/bash"]