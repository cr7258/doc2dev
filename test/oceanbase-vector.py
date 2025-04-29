import os

from dotenv import load_dotenv
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.documents import Document
from langchain_oceanbase.vectorstores import OceanbaseVectorStore

load_dotenv()

DASHSCOPE_API = os.environ.get("DASHSCOPE_API_KEY", "")
connection_args = {
    "host": "127.0.0.1",
    "port": "2881",
    "user": "root@test",
    "password": "admin",
    "db_name": "doc2dev",
}

embeddings = DashScopeEmbeddings(
    model="text-embedding-v3", dashscope_api_key=DASHSCOPE_API
)

vector_store = OceanbaseVectorStore(
    embedding_function=embeddings,
    table_name="langchain_vector",
    connection_args=connection_args,
    vidx_metric_type="l2",
    drop_old=True,
)

document_1 = Document(page_content="foo", metadata={"source": "https://foo.com"})
document_2 = Document(page_content="bar", metadata={"source": "https://bar.com"})
document_3 = Document(page_content="baz", metadata={"source": "https://baz.com"})
documents = [document_1, document_2, document_3]
vector_store.add_documents(documents=documents, ids=["1", "2", "3"])


results = vector_store.similarity_search(
    query="bar", k=1
)
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")


document_4 = Document(page_content="cat", metadata={"source": "https://cat.com"})
document_5 = Document(page_content="dog", metadata={"source": "https://dog.com"})
document_6 = Document(page_content="fish", metadata={"source": "https://fish.com"})
documents = [document_4, document_5, document_6]
OceanbaseVectorStore.from_documents(
    documents=documents,
    embedding=embeddings,
    connection_args=connection_args,
    drop_old=False,
)

# filter 好像不生效
# https://python.langchain.com/docs/integrations/vectorstores/oceanbase/
results = vector_store.similarity_search(
    query="fish", k=1, filter={"source": "https://example.com"}
)
for doc in results:
    print(f"* {doc.page_content} [{doc.metadata}]")
