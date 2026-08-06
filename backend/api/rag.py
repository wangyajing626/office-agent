from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel
from core.dependencies import get_current_user
from core.rag_engine import load_document, query_document, unload_document, get_current_doc_name

router = APIRouter(prefix="/api/rag", tags=["文档问答"])


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    sources: list = []


@router.post("/load")
def load_doc(
    file: UploadFile = File(...),
    user=Depends(get_current_user)
):
    """上传并加载文档"""
    try:
        contents = file.file.read()
        chunk_count = load_document(contents, file.filename)
        return {
            "status": "success",
            "chunks": chunk_count,
            "doc_name": file.filename
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@router.post("/query", response_model=QueryResponse)
def query(req: QueryRequest, user=Depends(get_current_user)):
    """提问"""
    result = query_document(req.question)
    return QueryResponse(
        answer=result["answer"],
        sources=result["sources"]
    )


@router.post("/unload")
def unload(user=Depends(get_current_user)):
    """卸载文档"""
    unload_document()
    return {"status": "success", "message": "已卸载"}


@router.get("/status")
def status(user=Depends(get_current_user)):
    """获取当前文档状态"""
    doc_name = get_current_doc_name()
    return {"loaded": doc_name is not None, "doc_name": doc_name}