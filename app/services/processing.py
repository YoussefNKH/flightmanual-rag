import re
from typing import List, Dict, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from app.core.dependencies import get_embedding
from app.core.config import settings

class DocumentProcessor:
    def __init__(self):
        # separators respecting B737 manual structure
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=[
                "\n\n\n",           # Major section breaks
                "\nProcedure\n",    # Procedure boundaries
                "\nChecklist\n",    # Checklist boundaries
                "\nWARNING:",       # Safety critical - keep with content
                "\nCAUTION:",       # Safety critical - keep with content
                "\nNote:",          # Important notes
                "\n\n",             # Paragraph breaks
                "\n",               # Line breaks
                ". ",               # Sentence boundaries
                " ",                # Word boundaries
                ""                  
            ]
        )

    def extract_chapter_section(self, text: str) -> Tuple[str, str]:
        # Pattern for chapter codes (NP, SP, PD, etc.)

        chapter_pattern = r'\b([A-Z]{2})\.(\d+)\.(\d+)'
        match = re.search(chapter_pattern, text)

        if match:
            chapter = f"{match.group(1)}.{match.group(2)}"
            section = match.group(3)
            return chapter, section
        return "Unknown", "Unknown"

    def identify_content_type(self, text: str) -> str:
        text_lower = text.lower()

        # Procedure identification
        if 'procedure' in text_lower:
            if 'normal' in text_lower:
                return "normal_procedure"
            elif 'emergency' in text_lower or 'non-normal' in text_lower:
                return "emergency_procedure"
            elif 'supplementary' in text_lower:
                return "supplementary_procedure"
            return "procedure"

        # Checklist identification
        if 'checklist' in text_lower:
            return "checklist"

        # Performance data
        if any(term in text_lower for term in ['takeoff', 'landing', 'climb', 'cruise']):
            if any(term in text_lower for term in ['weight', 'limit', 'altitude', 'fuel']):
                return "performance_data"

        # System description
        if 'system' in text_lower or 'description' in text_lower:
            return "system_description"

        # Controls and indicators
        if 'control' in text_lower or 'indicator' in text_lower or 'switch' in text_lower:
            return "controls_indicators"

        # Limitations
        if 'limit' in text_lower or 'limitation' in text_lower:
            return "limitations"

        return "general"

    def extract_safety_annotations(self, text: str) -> List[str]:
        annotations = []

        if 'WARNING:' in text or 'Warning:' in text:
            annotations.append("WARNING")
        if 'CAUTION:' in text or 'Caution:' in text:
            annotations.append("CAUTION")
        if 'Note:' in text or 'NOTE:' in text:
            annotations.append("NOTE")

        return annotations

    def extract_aircraft_systems(self, text: str) -> List[str]:
        systems = {
            "hydraulic": ["hydraulic", "hyd system", "pressure"],
            "electrical": ["electrical", "generator", "battery", "bus"],
            "fuel": ["fuel system", "fuel tank", "fuel pump"],
            "flight_controls": ["flight control", "elevator", "rudder", "aileron", "stabilizer"],
            "engines": ["engine", "thrust", "n1", "n2", "egt"],
            "landing_gear": ["landing gear", "gear system", "brake"],
            "pneumatic": ["pneumatic", "bleed air", "pack"],
            "ice_rain_protection": ["anti-ice", "de-ice", "ice protection"],
            "navigation": ["navigation", "fmc", "autopilot", "ils"],
            "fire_protection": ["fire", "overheat", "smoke"],
            "oxygen": ["oxygen", "crew oxygen", "passenger oxygen"],
            "doors": ["door", "entry", "overwing", "cargo"]
        }

        detected_systems = []
        text_lower = text.lower()

        for system, keywords in systems.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_systems.append(system)

        return detected_systems

    def extract_metadata(self, text: str, source: str) -> Dict:

        metadata = {
            "source": source,
            "char_count": len(text),
            "aircraft_type": "Boeing 737"
        }

        # Extract chapter and section
        chapter, section = self.extract_chapter_section(text)
        metadata["chapter"] = chapter
        metadata["section"] = section

        # Identify content type
        metadata["content_type"] = self.identify_content_type(text)

        # Extract safety annotations
        safety_annotations = self.extract_safety_annotations(text)
        if safety_annotations:
            metadata["safety_level"] = "critical" if "WARNING" in safety_annotations else "important"
            metadata["annotations"] = ", ".join(safety_annotations)

        # Extract system references
        systems = self.extract_aircraft_systems(text)
        if systems:
            metadata["systems"] = ", ".join(systems)

        # Identify if contains checklist
        if "checklist" in text.lower():
            metadata["has_checklist"] = True

        # Identify if contains performance data
        if any(term in text.lower() for term in ['table', 'weight', 'altitude', 'pressure']):
            metadata["has_performance_data"] = True

        # Extract flap settings if mentioned
        flap_pattern = r'[Ff]laps?\s+(\d+)'
        flaps = re.findall(flap_pattern, text)
        if flaps:
            metadata["flap_settings"] = ", ".join(set(flaps))

        return metadata

    def smart_chunk_text(self, text: str, metadata: Dict) -> List[Document]:
        content_type = metadata.get("content_type", "general")

        # For procedures and checklists, try to keep them intact if possible
        if content_type in ["procedure", "checklist", "normal_procedure", "emergency_procedure"]:
            # If the content is small enough, keep as single chunk
            if len(text) <= settings.CHUNK_SIZE * 1.5:
                doc = Document(page_content=text, metadata=metadata.copy())
                return [doc]

        # For performance tables, adjust chunk size to capture complete tables
        if metadata.get("has_performance_data"):
            # Use larger chunks for tables
            table_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE * 2,
                chunk_overlap=settings.CHUNK_OVERLAP,
                length_function=len,
                separators=["\n\n\n", "\n\n", "\n"]
            )
            chunks = table_splitter.split_text(text)
        else:
            # Standard chunking
            chunks = self.text_splitter.split_text(text)

        # Create documents with enhanced metadata
        documents = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)

            # Re-analyze chunk for specific metadata
            chunk_systems = self.extract_aircraft_systems(chunk)
            if chunk_systems:
                chunk_metadata["chunk_systems"] = ", ".join(chunk_systems)

            doc = Document(page_content=chunk, metadata=chunk_metadata)
            documents.append(doc)

        return documents

    def load_documents(self, file_path: str) -> List[Document]:
        loader = PyPDFLoader(file_path)
        return loader.load()

    def process_documents(self, file_paths: List[str]) -> List[Document]:
     
        all_chunks = []

        for file_path in file_paths:
            print(f"\nProcessing: {file_path}")

            # Load documents
            documents = self.load_documents(file_path)
            print(f"  Loaded {len(documents)} pages")

            # Process each page
            for page_num, doc in enumerate(documents):
                # Extract base metadata
                base_metadata = self.extract_metadata(doc.page_content, file_path)
                base_metadata["page_number"] = page_num + 1

                # Smart chunk the page
                page_chunks = self.smart_chunk_text(doc.page_content, base_metadata)

                # Add unique chunk IDs
                for i, chunk in enumerate(page_chunks):
                    chunk.metadata["chunk_id"] = f"p{page_num+1}_c{i}"

                all_chunks.extend(page_chunks)

            print(f"  Created {len([c for c in all_chunks if c.metadata['source'] == file_path])} chunks")

        print(f"\n✓ Total chunks created: {len(all_chunks)}")
        return all_chunks

    