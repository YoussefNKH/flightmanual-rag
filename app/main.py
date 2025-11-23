from app.services.processing import DocumentProcessor

processor = DocumentProcessor()
docs=[r"C:\Users\youss.YOUSSEF\OneDrive\Desktop\rag-test\data\documents\Boeing B737 Manual.pdf"]
processor.process_documents(docs)

