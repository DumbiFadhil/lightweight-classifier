"""FastAPI server for Indonesian Query Classification."""

from fastapi import FastAPI, HTTPException  # type: ignore
from pydantic import BaseModel  # type: ignore
from typing import List, Optional, Dict, Any
import uvicorn  # type: ignore
import logging
from classifier import IndonesianQueryClassifier
from query_logger import QueryLogger, ModelTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Indonesian Query Classifier",
    description="Lightweight DistilBERT-based classifier for Indonesian DataFrame queries",
    version="1.0.0"
)

classifier = IndonesianQueryClassifier()
query_logger = QueryLogger()
model_trainer = ModelTrainer(classifier)

# Pydantic models
class QueryRequest(BaseModel):
    query: str
    columns: Optional[List[str]] = ["column1", "column2", "column3"]
    session_id: Optional[str] = None
    user_id: Optional[str] = None

class QueryResponse(BaseModel):
    # query_id: int
    operation: str
    confidence: float
    query: str
    generated_code: str
    columns_used: List[str]

class HealthResponse(BaseModel):
    status: str
    message: str

class FeedbackRequest(BaseModel):
    query_id: int
    feedback: str
    correct_operation: Optional[str] = None
    comments: Optional[str] = None

class StatisticsResponse(BaseModel):
    total_queries: int
    queries_by_operation: Dict[str, int]
    queries_with_feedback: int
    average_confidence: float
    verified_training_samples: int
    model_needs_retraining: bool

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="Indonesian Query Classifier is running"
    )

@app.post("/classify", response_model=QueryResponse)
async def classify_query(request: QueryRequest):
    """Classify Indonesian query and generate DataFrame operation."""
    try:
        columns = request.columns or ["column1", "column2", "column3"]
        result = classifier.generate_dataframe_query(
            request.query, 
            columns
        )
        # Uncomment to enable query logging (require sqlite setup, can take up space)
        # query_id = query_logger.log_query(
        #     request.query,
        #     result,
        #     session_id=request.session_id,  # type: ignore
        #     user_id=request.user_id  # type: ignore
        # )
        
        return QueryResponse(
            # query_id=query_id,
            operation=result["operation"],
            confidence=result["confidence"],
            query=result["query"],
            generated_code=result["generated_code"],
            columns_used=columns
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/feedback")
async def submit_feedback(feedback_request: FeedbackRequest):
    """Submit feedback for a classified query."""
    try:
        query_logger.add_feedback(
            feedback_request.query_id,
            feedback_request.feedback,
            feedback_request.correct_operation  # type: ignore
        )
        should_retrain = model_trainer.should_retrain(min_new_samples=20)
        response = {
            "message": "Feedback recorded successfully",
            "query_id": feedback_request.query_id,
            "feedback": feedback_request.feedback
        }
        if should_retrain:
            response["suggestion"] = "Model has enough new data for retraining"
        return response
        
    except Exception as e:
        logger.error(f"Error recording feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/statistics", response_model=StatisticsResponse)
async def get_statistics():
    """Get system statistics and model performance metrics"""
    try:
        stats = query_logger.get_query_statistics()
        needs_retraining = model_trainer.should_retrain(min_new_samples=20)
        
        return StatisticsResponse(
            total_queries=stats["total_queries"],
            queries_by_operation=stats["queries_by_operation"],
            queries_with_feedback=stats["queries_with_feedback"],
            average_confidence=stats["average_confidence"],
            verified_training_samples=stats["verified_training_samples"],
            model_needs_retraining=needs_retraining
        )
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/operations")
async def get_supported_operations():
    """Get list of supported DataFrame operations"""
    return {
        "supported_operations": list(classifier.query_categories.values()),
        "descriptions": {
            "MAX": "Find maximum value - nilai maksimum, terbesar, tertinggi",
            "MIN": "Find minimum value - nilai minimum, terkecil, terendah",
            "SUM": "Calculate sum - jumlah, total, penjumlahan",
            "MEAN": "Calculate average - rata-rata, rerata",
            "COUNT": "Count rows/values - hitung, jumlah baris",
            "FILTER": "Filter data - cari, dimana, yang memiliki",
            "SORT": "Sort data - urutkan, sorting",
            "GROUP": "Group data - kelompokkan, grup"
        }
    }

@app.get("/examples")
async def get_example_queries():
    """Get example Indonesian queries for each operation type"""
    return {
        "examples": {
            "MAX": [
                "nilai maksimum harga",
                "berapa harga tertinggi",
                "cari nilai terbesar dari gaji"
            ],
            "MIN": [
                "nilai minimum harga", 
                "berapa harga terendah",
                "cari nilai terkecil"
            ],
            "SUM": [
                "jumlah total harga",
                "total penjumlahan gaji",
                "berapa total keseluruhan"
            ],
            "MEAN": [
                "rata-rata harga",
                "rerata gaji karyawan", 
                "berapa rata-rata umur"
            ],
            "COUNT": [
                "hitung jumlah baris",
                "berapa banyak data",
                "jumlah karyawan"
            ],
            "FILTER": [
                "cari data dimana harga lebih dari 100",
                "filter karyawan yang gajinya tinggi",
                "tampilkan data yang memiliki nilai"
            ],
            "SORT": [
                "urutkan berdasarkan harga",
                "sorting data dari terkecil",
                "arrange menurut nama"
            ],
            "GROUP": [
                "kelompokkan berdasarkan kategori",
                "group by departemen",
                "grup data menurut jenis"
            ]
        }
    }

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Indonesian Query Classifier API with Learning Capabilities",
        "version": "0.0.1",
        "description": "Lightweight DistilBERT-based classifier that learns from user feedback",
        "features": [
            "Query classification",
            "Feedback collection", 
            "Continuous learning",
            "Usage analytics"
        ],
        "endpoints": {
            "/classify": "POST - Classify query and generate DataFrame code",
            "/feedback": "POST - Submit feedback for query improvement",
            "/statistics": "GET - View system statistics and performance",
            "/operations": "GET - List supported operations",
            "/examples": "GET - Get example queries",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        workers=1,
        access_log=True
    )