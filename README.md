# BERT.CPP Docker Setup

This Docker setup allows you to easily test and run the [bert.cpp](https://github.com/skeskinen/bert.cpp) project - a C++ implementation of BERT with 4-bit integer quantization for CPU inference.

## Features

- **Complete BERT.CPP Environment**: Includes all dependencies and build tools
- **Pre-built Binaries**: Both shared libraries and static binaries
- **Sample Model**: Pre-downloaded all-MiniLM-L6-v2 model (Q4_0 quantization, ~14MB)
- **Ready-to-Run Examples**: Dynamic library and client/server examples
- **Persistent Storage**: Models and outputs are stored in Docker volumes

## Quick Start

### Option 1: PowerShell Script (Recommended)
```powershell
./setup.ps1
```

### Option 2: Batch File
```cmd
setup.bat
```

### Option 3: Manual Docker Commands
```bash
# Build the image
docker-compose build

# Start the container
docker-compose up -d

# Enter interactive shell
docker exec -it bert-cpp-test /bin/bash
```

## Usage Examples

Once the container is running, you can execute these commands:

### 1. Interactive Shell
```bash
docker exec -it bert-cpp-test /bin/bash
```

### 2. Run Test Examples
```bash
docker exec -it bert-cpp-test /app/test.sh
```

### 3. Dynamic Library Example
```bash
docker exec -it bert-cpp-test python3 examples/sample_dylib.py models/all-MiniLM-L6-v2/ggml-model-q4_0.bin
```

### 4. Server/Client Example

Start the server (runs in background):
```bash
docker exec -d bert-cpp-test ./build/bin/server -m models/all-MiniLM-L6-v2/ggml-model-q4_0.bin --port 8085
```

Connect with client:
```bash
docker exec -it bert-cpp-test python3 examples/sample_client.py 8085
```

### 5. List Available Models
```bash
docker exec -it bert-cpp-test ls -la models/
```

## What's Included

- **BERT.CPP**: Complete source code and compiled binaries
- **GGML Submodule**: Required mathematical library
- **Pre-built Models**: 
  - `all-MiniLM-L6-v2` in Q4_0 format (~14MB)
- **Examples**:
  - Dynamic library usage (`sample_dylib.py`)
  - TCP server (`server` binary)
  - Client connection (`sample_client.py`)
- **Build Tools**: CMake, GCC, Make
- **Python Environment**: Python 3 with required packages

## Architecture

The Docker setup uses a multi-stage build:

1. **Builder Stage**: 
   - Installs build dependencies
   - Clones repository and initializes submodules
   - Builds both shared and static libraries
   - Downloads sample models

2. **Runtime Stage**:
   - Minimal runtime environment
   - Copies built binaries and models
   - Exposes port 8085 for server examples

## Model Information

The included `all-MiniLM-L6-v2` model:
- **Size**: ~14MB (4-bit quantized)
- **Context Length**: 512 tokens  
- **Embedding Dimension**: 384
- **Use Case**: Sentence embeddings and similarity search

## Ports

- **8085**: BERT.CPP server (mapped to host)

## Volumes

- `bert-models`: Persistent model storage
- `bert-outputs`: Persistent output storage

## Performance

With 4-bit quantization:
- **Model Size**: ~14MB
- **RAM Usage**: Depends on input length (~450KB per token)
- **Speed**: Similar or better than sbert with batch_size=1

## Stopping the Container

```bash
docker-compose down
```

## Troubleshooting

1. **Docker not running**: Make sure Docker Desktop is started
2. **Build failures**: Ensure you have enough disk space (image ~1GB)
3. **Port conflicts**: Change port 8085 in docker-compose.yml if needed
4. **Memory issues**: The container needs at least 2GB RAM for building

## Next Steps

- Try different models by running: `python3 models/download-ggml.py list_models`
- Convert your own HuggingFace models using `models/convert-to-ggml.py`
- Explore quantization options (f32, f16, q4_0, q4_1)
- Integrate the C++ library into your own projects

## References

- [Original BERT.CPP Repository](https://github.com/skeskinen/bert.cpp)
- [GGML Library](https://github.com/ggerganov/ggml)
- [SentenceTransformers](https://sbert.net/)
- [MTEB Benchmark](https://github.com/embeddings-benchmark/mteb)