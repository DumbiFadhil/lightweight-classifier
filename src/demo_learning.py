"""
Simple dashboard to demonstrate the learning capabilities
Shows how queries improve over time with user feedback
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from classifier import IndonesianQueryClassifier
from query_logger import QueryLogger, ModelTrainer
import time
import json

def simulate_user_queries():
    """Simulate user queries and feedback over time"""
    
    print("=== Indonesian Query Classifier - Learning Demo ===\n")
    
    # Initialize components
    classifier = IndonesianQueryClassifier()
    logger = QueryLogger()
    trainer = ModelTrainer(classifier)
    
    # Sample queries with expected operations
    test_scenarios = [
        ("berapa harga tertinggi dari produk?", "MAX"),
        ("nilai minimum gaji karyawan", "MIN"), 
        ("jumlah total penjualan bulan ini", "SUM"),
        ("rata-rata umur pegawai", "MEAN"),
        ("hitung berapa banyak data", "COUNT"),
        ("cari produk dengan harga di atas 100", "FILTER"),
        ("urutkan berdasarkan tanggal lahir", "SORT"),
        ("kelompokkan data per departemen", "GROUP"),
        ("nilai maksimum dari kolom pendapatan", "MAX"),
        ("berapa jumlah seluruh transaksi", "SUM")
    ]
    
    columns = ["nama", "harga", "gaji", "tanggal", "departemen", "pendapatan"]
    
    print("📊 Starting simulation with queries and feedback...\n")
    
    # Process queries and simulate user feedback
    for i, (query, expected_op) in enumerate(test_scenarios, 1):
        print(f"Query {i}: '{query}'")
        
        # Classify the query
        result = classifier.generate_dataframe_query(query, columns)
        predicted_op = result['operation']
        confidence = result['confidence']
        
        print(f"  Predicted: {predicted_op} (confidence: {confidence:.3f})")
        print(f"  Expected:  {expected_op}")
        
        # Log the query
        query_id = logger.log_query(
            query, 
            result, 
            session_id=f"demo_session_{i//3}", 
            user_id="demo_user"
        )
        
        # Simulate user feedback
        is_correct = predicted_op == expected_op
        feedback = "correct" if is_correct else "incorrect"
        
        print(f"  Feedback:  {feedback}")
        
        # Add feedback to the system
        logger.add_feedback(query_id, feedback, expected_op)
        
        print(f"  Logged as training data ✓")
        print()
        
        # Small delay to simulate real usage
        time.sleep(0.1)
    
    # Show accumulated statistics
    print("📈 Final Statistics:")
    stats = logger.get_query_statistics()
    
    print(f"  Total Queries: {stats['total_queries']}")
    print(f"  Queries with Feedback: {stats['queries_with_feedback']}")
    print(f"  Average Confidence: {stats['average_confidence']:.3f}")
    print(f"  Verified Training Samples: {stats['verified_training_samples']}")
    print()
    
    print("📊 Queries by Operation:")
    for op, count in stats['queries_by_operation'].items():
        print(f"  {op}: {count}")
    print()
    
    # Check if ready for retraining
    if trainer.should_retrain(min_new_samples=5):
        print("🚀 Model is ready for retraining!")
        print("  Sufficient training data accumulated from user feedback")
        
        # Export training data
        export_path = logger.export_training_data()
        print(f"  Training data exported to: {export_path}")
    else:
        print("⏳ Need more feedback for retraining")
        needed = 5 - stats['verified_training_samples']
        print(f"  Need {needed} more verified samples")
    
    print("\n=== Demo Complete ===")
    print("This demonstrates how the system:")
    print("✓ Logs every query and prediction")
    print("✓ Collects user feedback")
    print("✓ Builds verified training dataset")
    print("✓ Tracks performance metrics")
    print("✓ Prepares for model retraining")

def show_api_usage():
    """Show how to use the API for learning"""
    
    print("\n=== API Usage for Continuous Learning ===\n")
    
    print("1. Classify a query:")
    print('''
    curl -X POST "http://localhost:8080/classify" \\
      -H "Content-Type: application/json" \\
      -d '{
        "query": "berapa harga tertinggi?",
        "columns": ["nama", "harga", "kategori"],
        "session_id": "user_session_123",
        "user_id": "user_456"
      }'
    ''')
    
    print("2. Submit feedback:")
    print('''
    curl -X POST "http://localhost:8080/feedback" \\
      -H "Content-Type: application/json" \\
      -d '{
        "query_id": 1,
        "feedback": "correct",
        "correct_operation": "MAX"
      }'
    ''')
    
    print("3. Check statistics:")
    print('''
    curl http://localhost:8080/statistics
    ''')
    
    print("4. View interactive docs:")
    print("   Open browser: http://localhost:8080/docs")

if __name__ == "__main__":
    simulate_user_queries()
    show_api_usage()