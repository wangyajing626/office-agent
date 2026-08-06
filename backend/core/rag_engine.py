import os
import tempfile
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_deepseek import ChatDeepSeek
from core.embeddings import get_embeddings

VECTOR_STORE_DIR = "./data/chroma_db"

_current_vectorstore = None
_current_doc_name = None


def load_document(file_bytes, filename):
    global _current_vectorstore, _current_doc_name

    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp_file:
        tmp_file.write(file_bytes)
        tmp_path = tmp_file.name

    try:
        file_ext = Path(filename).suffix.lower()
        if file_ext == ".pdf":
            loader = PyPDFLoader(tmp_path)
        else:
            loader = TextLoader(tmp_path, encoding="utf-8")

        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=30
        )
        chunks = text_splitter.split_documents(documents)

        embeddings = get_embeddings()
        persist_dir = os.path.join(VECTOR_STORE_DIR, Path(filename).stem)

        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=persist_dir
        )
        vectorstore.persist()

        _current_vectorstore = vectorstore
        _current_doc_name = filename

        return len(chunks)

    finally:
        os.unlink(tmp_path)


def query_document(question: str) -> dict:
    global _current_vectorstore

    if _current_vectorstore is None:
        return {"answer": "请先上传文档", "sources": []}

    try:
        retriever = _current_vectorstore.as_retriever(search_kwargs={"k": 4})

        llm = ChatDeepSeek(
            model="deepseek-chat",
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            temperature=0.3
        )

        # 新版 RAG 链写法
        prompt_template = ChatPromptTemplate.from_template("""
请基于以下上下文内容回答问题。如果上下文中没有相关信息，请说"文档中没有相关内容"。

上下文：
{context}

问题：{question}

回答：
""")

        docs = retriever.invoke(question)
        context_text = "\n\n".join([doc.page_content for doc in docs])
        source_texts = [doc.page_content for doc in docs]

        chain = (
            {"context": lambda x: context_text, "question": RunnablePassthrough()}
            | prompt_template
            | llm
            | StrOutputParser()
        )

        answer = chain.invoke(question)

        return {"answer": answer, "sources": source_texts}

    except Exception as e:
        return {"answer": f"查询失败：{str(e)}", "sources": []}


def unload_document():
    global _current_vectorstore, _current_doc_name
    _current_vectorstore = None
    _current_doc_name = None


def get_current_doc_name():
    return _current_doc_name