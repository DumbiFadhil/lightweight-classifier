"""Query logging and training data collection."""

import json
import os
import sqlite3
import pandas as pd  # type: ignore
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class QueryLogger:
    def __init__(self, db_path: Optional[str] = None):
        """Initialize SQLite DB and tables if missing."""
        # Prefer env override; default to project-relative path for local runs
        resolved = db_path or os.getenv("QUERY_LOG_DB_PATH", "data/query_logs.db")
        self.db_path = resolved
        self.init_database()
    
    def init_database(self):
        """Initialize required tables."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS query_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    query TEXT NOT NULL,
                    predicted_operation TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    generated_code TEXT NOT NULL,
                    columns_used TEXT NOT NULL,
                    user_feedback TEXT,
                    correct_operation TEXT,
                    session_id TEXT,
                    user_id TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    operation_id INTEGER NOT NULL,
                    operation_name TEXT NOT NULL,
                    source TEXT DEFAULT 'user_feedback',
                    verified BOOLEAN DEFAULT FALSE,
                    created_at TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def log_query(self, query: str, prediction_result: Dict, 
                  session_id: Optional[str] = None, user_id: Optional[str] = None) -> int:
        """Log a query and prediction result; return row id."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO query_logs 
                (timestamp, query, predicted_operation, confidence, generated_code, 
                 columns_used, session_id, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                query,
                prediction_result['operation'],
                prediction_result['confidence'],
                prediction_result['generated_code'],
                json.dumps(prediction_result.get('columns_used', [])),
                session_id,
                user_id
            ))
            
            query_id = int(cursor.lastrowid) if cursor.lastrowid is not None else -1
            conn.commit()
            
            logger.info(f"Logged query {query_id}: {query[:50]}...")
            return query_id
    
    def add_feedback(self, query_id: int, user_feedback: str, 
                     correct_operation: Optional[str] = None):
        """Add user feedback for a logged query."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE query_logs 
                SET user_feedback = ?, correct_operation = ?
                WHERE id = ?
            ''', (user_feedback, correct_operation, query_id))
            
            conn.commit()
            logger.info(f"Added feedback for query {query_id}")
            
            if correct_operation and user_feedback.lower() in ['correct', 'good', 'accurate']:
                self._add_to_training_data(query_id, correct_operation)
    
    def _add_to_training_data(self, query_id: int, operation: str):
        """Add verified query to training data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get the query text
            cursor.execute('SELECT query FROM query_logs WHERE id = ?', (query_id,))
            result = cursor.fetchone()
            
            if result:
                query_text = result[0]
                operation_id = self._operation_to_id(operation)
                
                cursor.execute('''
                    INSERT INTO training_data 
                    (query, operation_id, operation_name, source, verified, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    query_text,
                    operation_id,
                    operation,
                    'user_feedback',
                    True,
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                logger.info(f"Added verified training data: {query_text[:50]}... -> {operation}")
    
    def _operation_to_id(self, operation: str) -> int:
        """Convert operation name to ID."""
        operation_mapping = {
            "MAX": 0, "MIN": 1, "SUM": 2, "MEAN": 3,
            "COUNT": 4, "FILTER": 5, "SORT": 6, "GROUP": 7
        }
        return operation_mapping.get(operation, -1)
    
    def get_training_data(self, verified_only: bool = True) -> List[Tuple[str, int]]:
        """Get training data rows (query, operation_id)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = '''
                SELECT query, operation_id FROM training_data 
                WHERE verified = ? OR ? = 0
                ORDER BY created_at DESC
            '''
            
            cursor.execute(query, (verified_only, verified_only))
            return cursor.fetchall()
    
    def get_query_statistics(self) -> Dict:
        """Get statistics of logged queries."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total queries
            cursor.execute('SELECT COUNT(*) FROM query_logs')
            total_queries = cursor.fetchone()[0]
            
            # Queries by operation
            cursor.execute('''
                SELECT predicted_operation, COUNT(*) 
                FROM query_logs 
                GROUP BY predicted_operation
            ''')
            by_operation = dict(cursor.fetchall())
            
            # Queries with feedback
            cursor.execute('SELECT COUNT(*) FROM query_logs WHERE user_feedback IS NOT NULL')
            with_feedback = cursor.fetchone()[0]
            
            # Average confidence
            cursor.execute('SELECT AVG(confidence) FROM query_logs')
            avg_confidence = cursor.fetchone()[0] or 0
            
            # Training data count
            cursor.execute('SELECT COUNT(*) FROM training_data WHERE verified = 1')
            training_samples = cursor.fetchone()[0]
            
            return {
                'total_queries': total_queries,
                'queries_by_operation': by_operation,
                'queries_with_feedback': with_feedback,
                'average_confidence': round(avg_confidence, 3),
                'verified_training_samples': training_samples
            }
    
    def export_training_data(self, output_path: str = "/app/data/compiled_training_data.csv"):
        """Export verified training data to CSV."""
        training_data = self.get_training_data(verified_only=True)
        
        df = pd.DataFrame(training_data, columns=['query', 'operation_id'])
        
        # Add operation names
        operation_names = {
            0: "MAX", 1: "MIN", 2: "SUM", 3: "MEAN",
            4: "COUNT", 5: "FILTER", 6: "SORT", 7: "GROUP"
        }
        df['operation_name'] = df['operation_id'].map(operation_names)
        
        df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(df)} training samples to {output_path}")
        
        return output_path

class ModelTrainer:
    """Incremental model training scaffold."""
    
    def __init__(self, classifier):
        self.classifier = classifier
        self.logger = QueryLogger()
    
    def prepare_training_data(self) -> Tuple[List[str], List[int]]:
        """Prepare (queries, labels) from verified training data."""
        training_data = self.logger.get_training_data(verified_only=True)
        
        if not training_data:
            logger.warning("No verified training data available")
            return [], []
        
        queries, labels = zip(*training_data)
        return list(queries), list(labels)
    
    def should_retrain(self, min_new_samples: int = 50) -> bool:
        """Return True if enough new samples accumulated."""
        stats = self.logger.get_query_statistics()
        return stats['verified_training_samples'] >= min_new_samples
    
    def retrain_model(self, epochs: int = 3):
        """Retrain the model with accumulated data (placeholder)."""
        queries, labels = self.prepare_training_data()
        
        if len(queries) < 10:
            logger.warning("Insufficient training data for retraining")
            return False
        
        logger.info(f"Starting model retraining with {len(queries)} samples")
        
        try:
            logger.info(f"Would retrain model with {len(queries)} samples over {epochs} epochs")
            
            export_path = self.logger.export_training_data()
            logger.info(f"Training data exported to {export_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Model retraining failed: {str(e)}")
            return False

def main():
    """Test the query logger"""
    logger_test = QueryLogger()
    
    # Test logging
    test_result = {
        'operation': 'MAX',
        'confidence': 0.85,
        'generated_code': "df['harga'].max()",
        'columns_used': ['harga']
    }
    
    query_id = logger_test.log_query("berapa harga tertinggi?", test_result, session_id="test_session")
    logger_test.add_feedback(query_id, "correct", "MAX")
    
    # Show statistics
    stats = logger_test.get_query_statistics()
    print("Query Statistics:", json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()