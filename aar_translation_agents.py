import os
from crewai import Agent, Task, Crew
from openai import OpenAI
from typing import Optional
from PyPDF2 import PdfReader
from dotenv import load_dotenv

class AARProcessor:
    def __init__(self, openai_api_key: Optional[str] = None):
        load_dotenv()
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize agents
        self.document_processor = self._create_document_processor()
        self.translator = self._create_translator()
        self.summarizer = self._create_summarizer()
        self.quality_checker = self._create_quality_checker()
    
    def _create_document_processor(self):
        return Agent(
            role="Document Processor",
            goal="Extract and structure content from Ukrainian AAR documents",
            backstory="You are an expert in processing military documents, "
                     "particularly After-Action Reports. You understand the "
                     "structure and importance of military documentation and "
                     "can effectively extract all relevant information from PDFs.",
            allow_delegation=False,
            verbose=True
        )
    
    def _create_translator(self):
        return Agent(
            role="Military Translator",
            goal="Accurately translate Ukrainian military content to English",
            backstory="You are a specialized military translator with deep "
                     "knowledge of both Ukrainian and English military terminology. "
                     "You understand military slang, idioms, and cultural nuances "
                     "specific to Ukrainian armed forces. Your translations maintain "
                     "the precise meaning and context of the original text.",
            allow_delegation=False,
            verbose=True
        )
    
    def _create_summarizer(self):
        return Agent(
            role="Military Intelligence Summarizer",
            goal="Create concise, actionable summaries of translated AARs",
            backstory="You are an intelligence analyst specialized in creating "
                     "clear, actionable summaries from military reports. You "
                     "understand what information is most critical for frontline "
                     "soldiers and can present it in a clear, structured format "
                     "that enables quick decision-making.",
            allow_delegation=False,
            verbose=True
        )
    
    def _create_quality_checker(self):
        return Agent(
            role="Quality Assurance Specialist",
            goal="Ensure accuracy and completeness of translations and summaries",
            backstory="You are a quality control expert with experience in "
                     "military documentation. You verify that translations "
                     "maintain accuracy, context, and military terminology "
                     "while ensuring summaries contain all critical information "
                     "in an accessible format.",
            allow_delegation=False,
            verbose=True
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text content from a PDF file."""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def process_aar(self, pdf_path: str):
        # Extract text from PDF
        try:
            pdf_text = self.extract_text_from_pdf(pdf_path)
        except Exception as e:
            print(f"Error reading PDF: {str(e)}")
            return None

        # Create tasks for the workflow
        tasks = [
            Task(
                description="Process and structure the extracted PDF content",
                agent=self.document_processor,
                context=[f"Process the following text extracted from the AAR document "
                       f"and structure it appropriately:\n\n{pdf_text[:1000]}..."],  # First 1000 chars for context
                expected_output="A structured representation of the AAR content with clear sections and formatting"
            ),
            Task(
                description="Translate the structured content from Ukrainian to English",
                agent=self.translator,
                context=["Translate the processed content while preserving military "
                       "terminology, slang, and cultural context. Focus on maintaining "
                       "accuracy and clarity in military terms."],
                expected_output="An accurate English translation of the AAR that maintains military terminology and context"
            ),
            Task(
                description="Create a concise, actionable summary",
                agent=self.summarizer,
                context=["Generate a clear summary focusing on key actionable insights. "
                       "Structure the information for quick comprehension by frontline "
                       "soldiers."],
                expected_output="A concise, actionable summary of the AAR highlighting key insights and recommendations"
            ),
            Task(
                description="Verify translation and summary quality",
                agent=self.quality_checker,
                context=["Review the translation and summary for accuracy, completeness, "
                       "and clarity. Ensure all critical information is preserved and "
                       "presented effectively."],
                expected_output="A confirmation that the translation and summary meet quality standards"
            )
        ]
        
        # Create and run the crew
        crew = Crew(
            agents=[self.document_processor, self.translator, 
                   self.summarizer, self.quality_checker],
            tasks=tasks,
            verbose=True
        )
        
        result = crew.kickoff()
        return result

def main():
    # Example usage
    processor = AARProcessor()
    result = processor.process_aar("docs/test.pdf")
    print(result)

if __name__ == "__main__":
    main()
