"""Indonesian Query Classifier with rule-based intents and optional local transformer."""

import torch  # pyright: ignore[reportMissingImports]
import pandas as pd  # pyright: ignore[reportMissingModuleSource]
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification # pyright: ignore[reportMissingImports]
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IndonesianQueryClassifier:
    def __init__(self, model_name: str = "distilbert-base-multilingual-cased"):
        """Prefer fast, deterministic rules; optionally use a local fine-tuned model."""
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")

        self.query_categories = {
            0: "MAX",      # "nilai maksimum", "terbesar", "tertinggi"
            1: "MIN",      # "nilai minimum", "terkecil", "terendah"
            2: "SUM",      # "jumlah", "total", "penjumlahan"
            3: "MEAN",     # "rata-rata", "rerata", "average"
            4: "COUNT",    # "hitung", "jumlah baris", "berapa banyak"
            5: "FILTER",   # "cari", "dimana", "yang memiliki"
            6: "SORT",     # "urutkan", "sorting", "berdasarkan"
            7: "GROUP",    # "kelompokkan", "grup", "group by"
        }

        self.intent_keywords = {
            "MAX": [
                "max", "maks", "maksimum", "terbesar", "tertinggi", "paling tinggi", "nilai tertinggi",
                "puncak", "teratas", "paling tua", "tertua"
            ],
            "MIN": [
                "min", "minimum", "terkecil", "terendah", "paling rendah", "nilai terendah", "bawah", "paling muda", "termuda"
            ],
            "MEAN": ["rata", "rerata", "average", "mean"],
            "SUM": ["total", "penjumlahan", "akumulasi", "totalkan", "menjumlah"],
            "COUNT": ["hitung", "berapa banyak", "jumlah baris", "banyaknya", "count"],
            "SORT": ["urut", "sorting", "susun", "order by", "diurutkan"],
            "GROUP": ["kelompok", "group", "grup", "per grup", "kelompokan"],
            "FILTER": ["cari", "yang ", "dimana", "where", "filter"],
        }

        self.model = None
        self.tokenizer = None
        self.is_finetuned = False
        self.model_name = model_name
        try:
            # Prefer locally vendored fine-tuned model
            local_finetuned = "./models/indonesian-query-classifier"
            local_base = "./models/distilbert-base-multilingual-cased"
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(local_finetuned)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    local_finetuned, num_labels=len(self.query_categories)
                ).to(self.device)
                self.is_finetuned = True
                logger.info("Loaded fine-tuned model from local path")
            except Exception:
                # Fall back to locally downloaded base model directory (no network)
                self.tokenizer = AutoTokenizer.from_pretrained(local_base)
                self.model = AutoModelForSequenceClassification.from_pretrained(
                    local_base, num_labels=len(self.query_categories)
                ).to(self.device)
                logger.info("Loaded base model from local models folder")
        except Exception as e:
            logger.info(
                "Fine-tuned model not found. Falling back to rule-based classification only (reason: %s)",
                str(e)[:120],
            )

    def _load_or_create_model(self, model_name: str):
        """Deprecated; kept for backward compatibility."""
        return self.model

    def _rule_based_classify(self, query: str) -> Tuple[str, float]:
        """Deterministic keyword classification. Returns (operation, confidence)."""
        q = query.lower()

        priority = ["MAX", "MIN", "MEAN", "SUM",
                    "COUNT", "SORT", "GROUP", "FILTER"]
        for op in priority:
            keywords = self.intent_keywords.get(op, [])
            if any(kw in q for kw in keywords):
                base_conf = 0.95 if op in (
                    "MAX", "MIN", "MEAN", "SORT") else 0.9
                return op, base_conf

        if "siapa" in q or "yang mana" in q:
            if "paling tua" in q or "paling tinggi" in q or "tertinggi" in q or "terbesar" in q:
                return "MAX", 0.9
            if "paling muda" in q or "terendah" in q or "terkecil" in q:
                return "MIN", 0.9

        return "", 0.0

    def predict_query_type(self, query: str) -> Tuple[str, float]:
        """Predict operation type for a query."""
        op, conf = self._rule_based_classify(query)
        if op:
            return op, conf

        if self.model is not None and self.tokenizer is not None and self.is_finetuned:
            inputs = self.tokenizer(
                query,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=128,
            ).to(self.device)

            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(
                    outputs.logits, dim=-1)

            confidence, predicted_id = torch.max(predictions, dim=-1)
            operation_type = self.query_categories[predicted_id.item()]
            return operation_type, float(confidence.item())

        return "FILTER", 0.5

    def generate_dataframe_query(self, query: str, df_columns: List[str]) -> Dict:
        """Generate pandas code for the given query and columns."""
        operation_type, confidence = self.predict_query_type(query)

        query_result = {
            "operation": operation_type,
            "confidence": confidence,
            "query": query,
            "generated_code": self._generate_pandas_code(operation_type, query, df_columns)
        }

        return query_result

    def _generate_pandas_code(self, operation: str, query: str, columns: List[str]) -> str:
        """Generate pandas code based on operation type."""

        detected_column = self._detect_column(query, columns)
        q = query.lower()

        wants_row = "siapa" in q or "yang mana" in q

        if wants_row and detected_column:
            name_col = None
            age_col = None
            for col in columns:
                if col.lower() in ["nama", "name"]:
                    name_col = col
                if col.lower() in ["umur", "age"]:
                    age_col = col
                if name_col and age_col:
                    if operation == "MAX":
                        return f"df.loc[df['{detected_column}'].idxmax()][['{name_col}', '{age_col}']]"
                    if operation == "MIN":
                        return f"df.loc[df['{detected_column}'].idxmin()][['{name_col}', '{age_col}']]"

        if operation == "MAX":
            if wants_row and detected_column:
                return f"df.loc[df['{detected_column}'].idxmax()]"
            return f"df['{detected_column}'].max()" if detected_column else "df.max()"
        if operation == "MIN":
            if wants_row and detected_column:
                return f"df.loc[df['{detected_column}'].idxmin()]"
            return f"df['{detected_column}'].min()" if detected_column else "df.min()"
        if operation == "SUM":
            return f"df['{detected_column}'].sum()" if detected_column else "df.sum()"
        if operation == "MEAN":
            return f"df['{detected_column}'].mean()" if detected_column else "df.mean()"
        if operation == "COUNT":
            if "baris" in q:
                return "df.shape[0]"
            return (
                f"df['{detected_column}'].count()" if detected_column else "df.count()"
            )
        if operation == "FILTER":
            return (
                f"df[df['{detected_column}'] > value]" if detected_column else "df[df.column > value]"
            )
        if operation == "SORT":
            return (
                f"df.sort_values('{detected_column}')" if detected_column else "df.sort_values('column')"
            )
        if operation == "GROUP":
            return (
                f"df.groupby('{detected_column}').agg(func)" if detected_column else "df.groupby('column').agg(func)"
            )

        return "# Unknown operation"

    def _detect_column(self, query: str, columns: List[str]) -> str:
        """Simple column detection by keywords and mappings."""
        query_lower = query.lower()

        for col in columns:
            if col.lower() in query_lower:
                return col

        # Common Indonesian column name mappings
        column_mappings = {
            "harga": ["price", "harga", "cost"],
            "nama": ["name", "nama", "title"],
            "umur": ["age", "umur", "usia"],
            "gaji": ["salary", "gaji", "income"],
            "tanggal": ["date", "tanggal", "waktu"]
        }

        for indo_term, possible_cols in column_mappings.items():
            if indo_term in query_lower:
                for col in columns:
                    if any(term in col.lower() for term in possible_cols):
                        return col

        return columns[0] if columns else "column"


class TrainingData:
    """Generate training data examples."""

    @staticmethod
    def generate_sample_data():
        """Return sample training data (query, label)."""
        training_samples = [
            # MAX operations
            ("nilai maksimum harga", 0),
            ("berapa harga tertinggi", 0),
            ("cari nilai terbesar dari gaji", 0),
            ("maksimum umur karyawan", 0),

            # MIN operations
            ("nilai minimum harga", 1),
            ("berapa harga terendah", 1),
            ("cari nilai terkecil dari gaji", 1),
            ("minimum umur karyawan", 1),

            # SUM operations
            ("jumlah total harga", 2),
            ("total penjumlahan gaji", 2),
            ("berapa total keseluruhan", 2),
            ("sum dari semua nilai", 2),

            # MEAN operations
            ("rata-rata harga", 3),
            ("rerata gaji karyawan", 3),
            ("berapa rata-rata umur", 3),
            ("nilai tengah dari data", 3),

            # COUNT operations
            ("hitung jumlah baris", 4),
            ("berapa banyak data", 4),
            ("count total record", 4),
            ("jumlah karyawan", 4),

            # FILTER operations
            ("cari data dimana harga lebih dari 100", 5),
            ("filter karyawan yang gajinya tinggi", 5),
            ("tampilkan data yang memiliki nilai", 5),
            ("where kondisi tertentu", 5),

            # SORT operations
            ("urutkan berdasarkan harga", 6),
            ("sorting data dari terkecil", 6),
            ("arrange menurut nama", 6),
            ("order by tanggal", 6),

            # GROUP operations
            ("kelompokkan berdasarkan kategori", 7),
            ("group by departemen", 7),
            ("grup data menurut jenis", 7),
            ("aggregate per grup", 7)
        ]

        return training_samples


def main():
    """Main function for testing"""
    classifier = IndonesianQueryClassifier()

    # Test queries
    test_queries = [
        "berapa harga tertinggi di data ini?",
        "cari rata-rata gaji karyawan",
        "urutkan data berdasarkan tanggal",
        "jumlah total penjualan bulan ini"
    ]

    sample_columns = ["nama", "harga", "gaji", "tanggal", "kategori"]

    print("=== Indonesian Query Classification Test ===")
    for query in test_queries:
        result = classifier.generate_dataframe_query(query, sample_columns)
        print(f"\nQuery: {query}")
        print(f"Operation: {result['operation']}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Generated Code: {result['generated_code']}")


if __name__ == "__main__":
    main()
