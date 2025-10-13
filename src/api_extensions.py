"""Additional API endpoints for feedback and model management."""

from typing import Optional, Dict
from pydantic import BaseModel  # type: ignore
from fastapi import HTTPException  # type: ignore
from main import app, query_logger, model_trainer, logger  # type: ignore

class FeedbackRequest(BaseModel):
    query_id: int
    feedback: str  # "correct", "incorrect", "partial"
    correct_operation: Optional[str] = None
    comments: Optional[str] = None

class StatisticsResponse(BaseModel):
    total_queries: int
    queries_by_operation: Dict[str, int]
    queries_with_feedback: int
    average_confidence: float
    verified_training_samples: int
    model_needs_retraining: bool

@app.post("/feedback")
async def submit_feedback(feedback_request: FeedbackRequest):
    """Submit feedback for a classified query."""
    try:
        query_logger.add_feedback(
            feedback_request.query_id,
            feedback_request.feedback,
            feedback_request.correct_operation
        )
        
        # Check if model should be retrained
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
    """Get system statistics and model performance metrics."""
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

@app.post("/retrain")
async def trigger_retraining():
    """Manually trigger model retraining with accumulated data."""
    try:
        # Check if there's enough data
        if not model_trainer.should_retrain(min_new_samples=10):
            return {
                "message": "Insufficient training data for retraining",
                "min_samples_needed": 10,
                "current_samples": query_logger.get_query_statistics()["verified_training_samples"]
            }
        
        # Start retraining process
        success = model_trainer.retrain_model()
        
        if success:
            return {
                "message": "Model retraining completed successfully",
                "training_samples": query_logger.get_query_statistics()["verified_training_samples"]
            }
        else:
            return {
                "message": "Model retraining failed",
                "error": "Check logs for details"
            }
            
    except Exception as e:
        logger.error(f"Error during retraining: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/export-training-data")
async def export_training_data():
    """Export accumulated training data for analysis."""
    try:
        export_path = query_logger.export_training_data()
        stats = query_logger.get_query_statistics()
        
        return {
            "message": "Training data exported successfully",
            "export_path": export_path,
            "samples_exported": stats["verified_training_samples"],
            "download_url": "/data/compiled_training_data.csv"
        }
        
    except Exception as e:
        logger.error(f"Error exporting training data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Indonesian Query Classifier API with Learning Capabilities",
        "version": "2.0.0",
        "description": "Lightweight DistilBERT-based classifier that learns from user feedback",
        "features": [
            "Query classification",
            "Feedback collection", 
            "Continuous learning",
            "Model retraining",
            "Usage analytics"
        ],
        "endpoints": {
            "/classify": "POST - Classify query and generate DataFrame code",
            "/feedback": "POST - Submit feedback for query improvement",
            "/statistics": "GET - View system statistics and performance",
            "/retrain": "POST - Trigger model retraining",
            "/export-training-data": "GET - Export training data",
            "/operations": "GET - List supported operations",
            "/examples": "GET - Get example queries",
            "/health": "GET - Health check",
            "/docs": "GET - API documentation"
        }
    }