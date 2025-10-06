"""
Simple test script for Indonesian Query Classifier
Can be run without the full API server
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from classifier import IndonesianQueryClassifier
import pandas as pd

def create_sample_dataframe():
    """Create a sample DataFrame for testing"""
    data = {
        "nama": ["Budi", "Sari", "Andi", "Dewi", "Rudi"],
        "umur": [25, 30, 35, 28, 32],
        "gaji": [5000000, 7500000, 8000000, 6000000, 7000000],
        "departemen": ["IT", "HR", "IT", "Finance", "IT"],
        "tanggal_masuk": ["2020-01-15", "2019-03-20", "2018-05-10", "2021-02-01", "2020-08-30"]
    }
    return pd.DataFrame(data)

def test_classifier():
    """Test the classifier with Indonesian queries"""
    print("=== Indonesian Query Classifier Test ===\n")
    
    # Initialize classifier
    classifier = IndonesianQueryClassifier()
    
    # Create sample data
    df = create_sample_dataframe()
    columns = df.columns.tolist()
    
    print("Sample DataFrame:")
    print(df)
    print(f"\nColumns: {columns}\n")
    
    # Test queries
    test_queries = [
        "berapa gaji tertinggi?",
        "siapa yang umurnya paling muda?",
        "jumlah total gaji semua karyawan",
        "rata-rata umur karyawan",
        "hitung berapa banyak karyawan",
        "cari karyawan dari departemen IT", 
        "urutkan berdasarkan umur",
        "kelompokkan berdasarkan departemen"
    ]
    
    print("=== Query Classification Results ===\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. Query: '{query}'")
        
        # Get classification result
        result = classifier.generate_dataframe_query(query, columns)
        
        print(f"   Operation: {result['operation']}")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   Generated Code: {result['generated_code']}")
        
        # Try to execute the code (simplified)
        try:
            if result['operation'] in ['MAX', 'MIN', 'SUM', 'MEAN', 'COUNT']:
                code = result['generated_code'].replace('df', 'sample_df')
                sample_df = df  # For execution context
                exec_result = eval(code)
                print(f"   Execution Result: {exec_result}")
        except Exception as e:
            print(f"   Execution: Could not execute ({str(e)[:50]}...)")
            
        print()

def test_manual_execution():
    """Test manual execution of generated queries"""
    print("\n=== Manual Execution Test ===\n")
    
    df = create_sample_dataframe()
    
    # Test some operations manually
    operations = {
        "Maximum Gaji": df['gaji'].max(),
        "Minimum Umur": df['umur'].min(), 
        "Total Gaji": df['gaji'].sum(),
        "Rata-rata Umur": df['umur'].mean(),
        "Jumlah Karyawan": df.shape[0],
        "Sort by Umur": df.sort_values('umur')[['nama', 'umur']].to_string(),
        "Group by Departemen": df.groupby('departemen').size().to_string()
    }
    
    for operation, result in operations.items():
        print(f"{operation}: {result}")
        print()

if __name__ == "__main__":
    test_classifier()
    test_manual_execution()