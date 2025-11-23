"""Main application for Enterprise Document QA and Search Assistant."""
import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from src.rag_pipeline import RAGPipeline
from src.ingestion.pipeline import IngestionPipeline

app = FastAPI(
    title="Enterprise Document QA and Search Assistant",
    description="RAG-based document question answering system with AWS integration",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipelines
rag_pipeline = RAGPipeline()
ingestion_pipeline = IngestionPipeline()


# Request/Response models
class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]
    confidence: float
    validation: dict
    retrieved_docs_count: int


class IngestionResponse(BaseModel):
    documents_processed: int
    chunks_created: int
    status: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Enterprise Document QA and Search Assistant API",
        "version": "1.0.0",
        "endpoints": {
            "query": "/query",
            "ingest_s3": "/ingest/s3",
            "ingest_file": "/ingest/file",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "Enterprise RAG API"}


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the document knowledge base.
    
    Args:
        request: Query request with question and optional top_k
        
    Returns:
        QueryResponse with answer, sources, and validation
    """
    try:
        result = rag_pipeline.query(request.question, top_k=request.top_k)
        return QueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


@app.post("/ingest/s3", response_model=IngestionResponse)
async def ingest_from_s3(s3_key: Optional[str] = None, prefix: Optional[str] = None):
    """
    Ingest documents from S3 bucket.
    
    Args:
        s3_key: Specific S3 key to ingest (optional)
        prefix: S3 prefix to ingest all documents with (optional)
        
    Returns:
        IngestionResponse with processing statistics
    """
    try:
        result = ingestion_pipeline.ingest_from_s3(s3_key=s3_key, prefix=prefix)
        return IngestionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting from S3: {str(e)}")


@app.post("/ingest/file", response_model=IngestionResponse)
async def ingest_file(file: UploadFile = File(...), upload_to_s3: bool = False):
    """
    Upload and ingest a document file.
    
    Args:
        file: Document file to upload
        upload_to_s3: Whether to upload to S3 before processing
        
    Returns:
        IngestionResponse with processing statistics
    """
    try:
        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Determine S3 key if uploading
        s3_key = None
        if upload_to_s3:
            s3_key = f"raw-documents/{file.filename}"
        
        # Ingest
        result = ingestion_pipeline.ingest_local_file(temp_path, s3_key=s3_key)
        
        # Cleanup
        os.remove(temp_path)
        
        return IngestionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting file: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

