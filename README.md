# Lightweight Indonesian Query Classifier

A minimal, memory-efficient Docker setup using DistilBERT to classify Indonesian queries into DataFrame operations. This is a much lighter alternative to the full bert.cpp implementation, specifically designed for categorizing Indonesian database queries.

## 🎯 Purpose

Convert Indonesian natural language queries into pandas DataFrame operations:

- **"berapa harga tertinggi?"** → `df['harga'].max()`
- **"rata-rata gaji karyawan"** → `df['gaji'].mean()`
- **"urutkan berdasarkan tanggal"** → `df.sort_values('tanggal')`
- **"jumlah total penjualan"** → `df['penjualan'].sum()`

## 🚀 Quick Start

### Option 1: PowerShell Script (Recommended)
```powershell
./setup-light.ps1
```

### Option 2: Manual Docker Commands
```bash
# Build and start
docker-compose -f docker-compose.light.yml up -d

# Test the classifier
docker exec -it indonesian-classifier python src/test.py
```

## 📊 Supported Operations

| Indonesian Query Examples | Operation | Generated Code |
|----------------------------|-----------|----------------|
| "Hitung jumlah karyawan", "berapa banyak data karyawan" | COUNT | `df['nama'].count()` |
| "nilai maksimum harga", "harga tertinggi" | MAX | `df['harga'].max()` |
| "nilai minimum gaji", "gaji terendah" | MIN | `df['gaji'].min()` |
| "jumlah total", "sum semua nilai" | SUM | `df['column'].sum()` |
| "rata-rata umur", "rerata gaji" | MEAN | `df['umur'].mean()` |
| "Hitung jumlah baris", "berapa banyak data" | COUNT | `df.shape[0]` |
| "cari data dimana", "filter yang memiliki" | FILTER | `df[df['column'] > value]` |
| "urutkan berdasarkan", "sorting data" | SORT | `df.sort_values('column')` |
| "kelompokkan berdasarkan", "group by" | GROUP | `df.groupby('column')` |

## 🔧 Usage Examples

### 1. Test the Classifier (Offline)
```bash
docker exec -it indonesian-classifier python src/test.py
```

### 2. Start API Server
```bash
docker exec -d indonesian-classifier python src/main.py
```

### 3. Use REST API
```bash
# Health check

### Option 3: Local Setup (No Docker) — Python 3.11 + venv (Windows)
Use Python 3.11 and a virtual environment to avoid dependency conflicts.

```powershell
# 1) Create venv and install deps
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r requirements-light.txt

# 2) Enforce offline mode for HF/Transformers (optional but recommended)
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"

# 3) Start API
$env:PYTHONPATH = "$PWD\\src"
.\.venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8080

# 4) Health check
curl http://127.0.0.1:8080/health

# Classify a query
curl -X POST "http://localhost:8080/classify" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "berapa harga tertinggi dari data ini?",
    "columns": ["nama", "harga", "kategori"]
  }'

# Get supported operations
curl http://localhost:8080/operations

# Get example queries
curl http://localhost:8080/examples
```

### 4. Interactive API Documentation
Open browser: http://localhost:8080/docs

### Option 4: Local Setup (Linux) — Python 3.11 + venv (Offline-first)

```bash
# 1) Create venv and install deps
python3.11 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements-light.txt

# 2) Enforce offline mode (recommended for air-gapped servers)
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

# 3) Start API (script will set PYTHONPATH and offline vars too)
chmod +x scripts/run_offline.sh
./scripts/run_offline.sh

# 4) Health check
curl http://127.0.0.1:8080/health
```

Optional: systemd service (Linux)
```ini
[Unit]
Description=Indonesian Query Classifier API (Offline)
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/lightweight-classifier
Environment=HF_HUB_OFFLINE=1
Environment=TRANSFORMERS_OFFLINE=1
Environment=PYTHONPATH=/opt/lightweight-classifier/src
ExecStart=/opt/lightweight-classifier/.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8080
Restart=always
User=www-data
Group=www-data

[Install]
WantedBy=multi-user.target
```

### Server (Linux) with Git LFS (No Hugging Face)

Use Git LFS to bring the models along with the repo and run fully offline (no whitelisting Hugging Face):

```bash
# 0) Install Git LFS (one-time)
# Ubuntu/Debian:
#   sudo apt-get update && sudo apt-get install -y git-lfs
#   git lfs install

# 1) Clone and fetch LFS-tracked model files
git clone -b light-only https://github.com/DumbiFadhil/lightweight-classifier.git
cd lightweight-classifier/BERT-CPP
git lfs pull

# 2) Create venv and install dependencies (from PyPI or your internal mirror)
python3.11 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements-light.txt

# 3) Enforce offline behavior for Transformers/HF (no network calls)
export HF_HUB_OFFLINE=1
export TRANSFORMERS_OFFLINE=1

# 4) Start the API (script sets PYTHONPATH and prefers venv)
chmod +x scripts/run_offline.sh
./scripts/run_offline.sh
```

If Git LFS is blocked, copy the `models/distilbert-base-multilingual-cased/` folder from a connected machine (ZIP/USB/SCP) into the same path on the server. Ensure it contains:

- `config.json`, `tokenizer.json`, `tokenizer_config.json`, `vocab.txt`
- `pytorch_model.bin` or `model.safetensors`

With `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` set, the app will never attempt to download from Hugging Face.

## 📁 Project Structure

```
BERT-CPP/
├── Dockerfile.light              # Lightweight Docker image
├── docker-compose.light.yml      # Docker compose for light version

Notes:
- The commands above are for Windows PowerShell. Replace path separators accordingly on other platforms.
- Running `python src\main.py` sets the script directory to `src/` so module imports work without extra PYTHONPATH tweaks.
- If PyTorch installation fails due to environment constraints, ensure you’re on Python 3.11 and recent pip, then retry. CPU-only wheels are sufficient for this project.
├── requirements-light.txt        # Minimal Python dependencies
├── setup-light.ps1              # PowerShell setup script
├── src/
│   ├── classifier.py             # Main classifier logic
│   ├── main.py                   # FastAPI server
│   └── test.py                   # Testing script
├── data/
│   └── training_data.csv         # Sample training data
├── models/                       # Model storage (auto-created)
└── README-light.md              # This file
```

## 🧠 How It Works

1. **DistilBERT Model**: Uses `distilbert-base-multilingual-cased` for text classification
2. **8 Categories**: Classifies queries into MAX, MIN, SUM, MEAN, COUNT, FILTER, SORT, GROUP
3. **Column Detection**: Simple rule-based column name detection from query text
4. **Code Generation**: Template-based pandas code generation

## 💾 Memory Usage

- **Container Size**: ~800MB (vs 2GB+ for full bert.cpp)
- **Runtime Memory**: ~300-500MB
- **Model Size**: ~135MB (DistilBERT multilingual)
- **Startup Time**: ~10-15 seconds

## 🔧 Configuration

### Environment Variables
- `PYTHONPATH=/app/src`
- Models stored in `/app/models`
- Data files in `/app/data`

### Ports
- **8080**: FastAPI server (mapped to host)

### Volumes
- `./data:/app/data` - Training data and samples
- `./models:/app/models` - Model storage

## 🧪 Testing

The classifier includes sample test data:

```python
# Sample DataFrame
{
    "nama": ["Budi", "Sari", "Andi", "Dewi", "Rudi"],
    "umur": [25, 30, 35, 28, 32],
    "gaji": [5000000, 7500000, 8000000, 6000000, 7000000],
    "departemen": ["IT", "HR", "IT", "Finance", "IT"]
}
```

### Test Queries
- "berapa gaji tertinggi?" → MAX operation
- "rata-rata umur karyawan" → MEAN operation  
- "urutkan berdasarkan umur" → SORT operation
- "kelompokkan berdasarkan departemen" → GROUP operation

## 📴 Offline Model (No Runtime Downloads)

To avoid downloading from Hugging Face at runtime, download the model locally and commit it via Git LFS:

```powershell
# Ensure Python 3.11 venv is active (see Local Setup section)

# 1) (Optional) Ensure huggingface_hub is installed in your venv
pip install huggingface_hub

# 2) Download tokenizer + base model into ./models/distilbert-base-multilingual-cased
py -3.11 scripts\download_model.py --model distilbert-base-multilingual-cased --out-dir models\distilbert-base-multilingual-cased

# 2) Set up Git LFS (one-time per machine)
git lfs install

# 3) Track common model files
git lfs track "models/*/*.bin"
git lfs track "models/*/pytorch_model*.bin"
git lfs track "models/*/model.safetensors"
git lfs track "models/*/rust_model.ot"
git add .gitattributes

# 4) Add and commit the model directory
git add models\distilbert-base-multilingual-cased
git commit -m "chore(models): vendor distilbert-base-multilingual-cased for offline use"
git push
```

The classifier will look for a local fine-tuned model at `./models/indonesian-query-classifier` first; if not found, it will load the locally downloaded base model from `./models/distilbert-base-multilingual-cased`. If neither is present, it falls back to rule-based mode without network access.

To harden offline behavior, the app sets `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` at startup. You can override these via environment variables if needed.

## �🔄 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/classify` | POST | Classify query and generate code |
| `/operations` | GET | List supported operations |
| `/examples` | GET | Get example queries |
| `/docs` | GET | Interactive API documentation |

## 📝 Example API Response

```json
{
  "operation": "MAX",
  "confidence": 0.892,
  "query": "berapa harga tertinggi?",
  "generated_code": "df['harga'].max()",
  "columns_used": ["nama", "harga", "kategori"]
}
```

## 🛠 Development

### Adding New Query Types
1. Update `query_categories` in `classifier.py`
2. Add training samples in `data/training_data.csv`
3. Update code templates in `_generate_pandas_code()`

### Improving Column Detection
Modify `_detect_column()` method to include:
- Named Entity Recognition (NER)
- Fuzzy string matching
- Domain-specific mappings

### Fine-tuning the Model
1. Prepare labeled training data
2. Use the training samples in `TrainingData.generate_sample_data()`
3. Train with standard transformers training loop

## 🚫 Limitations

- **Basic Column Detection**: Simple string matching for column names
- **Template-based Code**: Uses predefined pandas code templates
- **No Batching**: Processes one query at a time
- **Indonesian Focus**: Optimized for Indonesian queries only
- **Simple Operations**: Limited to basic DataFrame operations

## 🔄 Improvements Roadmap

1. **Better NLP**: Add NER for better column detection
2. **More Operations**: Support for JOIN, advanced aggregations
3. **Query Validation**: Validate generated pandas code
4. **Caching**: Cache model predictions
5. **Training Pipeline**: Automated model fine-tuning

## 🐛 Troubleshooting

1. **Container won't start**: Check Docker memory allocation (needs ~1GB)
2. **Model download fails**: Ensure internet connection for first run
3. **Port conflict**: Change port 8080 in docker-compose.light.yml
4. **Memory issues**: Reduce batch size or use smaller model

## 🆚 Comparison with Full BERT.CPP

| Feature | Lightweight | Full BERT.CPP |
|---------|-------------|---------------|
| **Container Size** | ~800MB | ~2GB+ |
| **Memory Usage** | ~300-500MB | ~1-2GB |
| **Startup Time** | ~15 seconds | ~30-60 seconds |
| **Use Case** | Indonesian query classification | General sentence embeddings |
| **Model** | DistilBERT multilingual | Full BERT with quantization |
| **Languages** | Indonesian + multilingual | Universal |

## 📜 License

MIT License - Feel free to use and modify for your projects.

## 🤝 Contributing

1. Add more Indonesian training samples
2. Improve column detection algorithms
3. Add support for more DataFrame operations
4. Optimize memory usage further

---

**Note**: This is a lightweight, specialized version focused on Indonesian query classification. For general-purpose sentence embeddings, use the full bert.cpp implementation.
