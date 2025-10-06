# Multi-stage build for bert.cpp
# Stage 1: Build environment
FROM ubuntu:22.04 AS builder

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    python3 \
    python3-pip \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Clone the bert.cpp repository
RUN git clone https://github.com/skeskinen/bert.cpp.git .

# Initialize and update submodules (ggml)
RUN git submodule update --init --recursive

# Install Python dependencies for model downloading
RUN pip3 install -r requirements.txt

# Create build directory and build the project
RUN mkdir build && \
    cd build && \
    cmake .. -DBUILD_SHARED_LIBS=ON -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc)

# Build static binaries as well (for server example)
RUN cd build && \
    cmake .. -DBUILD_SHARED_LIBS=OFF -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc)

# Download a sample model for testing
RUN python3 models/download-ggml.py download all-MiniLM-L6-v2 q4_0

# Stage 2: Runtime environment
FROM ubuntu:22.04 AS runtime

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy the built binaries and libraries from builder stage
COPY --from=builder /app/build /app/build
COPY --from=builder /app/models /app/models
COPY --from=builder /app/examples /app/examples
COPY --from=builder /app/requirements.txt /app/requirements.txt

# Install Python dependencies for running examples
RUN pip3 install -r requirements.txt

# Copy necessary source files for examples
COPY --from=builder /app/bert.h /app/bert.h
COPY --from=builder /app/bert.cpp /app/bert.cpp

# Create a simple test script
RUN echo '#!/bin/bash\n\
echo "=== BERT.CPP Test Environment ==="\n\
echo "Available commands:"\n\
echo "1. Run dynamic library example:"\n\
echo "   python3 examples/sample_dylib.py models/all-MiniLM-L6-v2/ggml-model-q4_0.bin"\n\
echo ""\n\
echo "2. Start server (in background):"\n\
echo "   ./build/bin/server -m models/all-MiniLM-L6-v2/ggml-model-q4_0.bin --port 8085 &"\n\
echo ""\n\
echo "3. Run client (after starting server):"\n\
echo "   python3 examples/sample_client.py 8085"\n\
echo ""\n\
echo "4. List available models:"\n\
echo "   ls -la models/"\n\
echo ""\n\
echo "5. Interactive shell: /bin/bash"\n\
echo "==============================="\n\
' > /app/test.sh && chmod +x /app/test.sh

# Expose port for server example
EXPOSE 8085

# Default command
CMD ["/app/test.sh"]