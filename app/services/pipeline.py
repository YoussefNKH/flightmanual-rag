from app.services.processing import DocumentProcessor

class PipelineService:
    def __init__(self):
        self.processor = DocumentProcessor()
    
    def process_and_store(self, file_path: str, create_vector_store):
        # Process document to get chunks
        chunks = self.processor.process_documents(file_path)
        
        # Create vector store from chunks
        vector_store = create_vector_store(chunks)
        
        return vector_store
        