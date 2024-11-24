from pypdf import PdfReader
import os
from crewai import Agent, Task, Crew
from crewai_tools import FileReadTool
from openai import OpenAI
from typing import Optional
from dotenv import load_dotenv
import datetime
import time
from flask import Flask, request, Response

# Initialize Flask app
app = Flask(__name__)

WEBHOOK_URL = "https://webhook-test.com/payload/dc123701-1324-4459-8286-25879cbb5561"

class AARProcessor:
    def __init__(self, openai_api_key: Optional[str] = None):
        load_dotenv()
        OMNISTACK_API_KEY = os.getenv("OMNISTACK_API_KEY")
        MODEL = "vito_eunice_belle"

        # Initialize OpenAI client with Omnistack configuration
        self.client = OpenAI(
            base_url="https://api.omnistack.sh/openai/v1",
            api_key=OMNISTACK_API_KEY
        )

        # Initialize agents with Omnistack configuration
        self.llm_config = {
            "client": self.client,
            "model": MODEL
        }

        # Initialize FileReadTool
        self.file_reader = FileReadTool(file_path='./AAR/clean/USSOF/JDW_CT_Comms_AAR.md')

        # Initialize agents
        self.document_processor = self._create_document_processor()
        self.translator = self._create_translator()
        self.summarizer = self._create_summarizer()
        self.quality_checker = self._create_quality_checker()

    def _create_document_processor(self):
        return Agent(
            role="Military Document Processing Content Specialist",
            goal=(
                "Extract, structure, and organize critical information from Ukrainian After-Action Reports (AARs) for USSOF in direct and effective communication"
                "to support data analysis, mission planning, and operational improvements. Outputs must follow a standardized format "
                "to ensure clarity and consistency, including the following sections: Context, Key Findings, Lessons Learned, Recommendations, "
                "and Relevant Supporting Details. Each section should be well-defined, concise, and tailored for integration into military intelligence workflows."
            ),
            backstory=(
                "You are a highly skilled military documentation specialist with extensive experience in processing and analyzing After-Action Reports (AARs). "
                "Your expertise lies in understanding the nuances and complexities of military documentation, enabling you to efficiently extract key data points, "
                "operational insights, and mission-critical information from a wide range of document formats. "
                "You ensure outputs are structured and presented consistently to include sections such as Context, Key Findings, Lessons Learned, Recommendations, "
                "and Supporting Details. This structured format provides military leaders with actionable insights and streamlines the review and analysis process. "
                "Your structured approach ensures extracted data is accurate, thorough, and well-organized, empowering intelligence teams to leverage this information "
                "for informed decision-making and enhanced mission outcomes."
            ),
            allow_delegation=False,
            tools=[self.file_reader],
            verbose=True,
            llm_config=self.llm_config
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
            verbose=True,
            llm_config=self.llm_config
        )
    def _create_summarizer(self):
        return Agent(
            role="Special Forces Lessons Learned Analyst",
            goal=(
                "Produce detailed, precise, and actionable summaries of After-Action Reports (AARs) tailored for special forces units. "
                "Summaries must follow a standardized format with the following sections: Mission Overview, Key Lessons Learned, Critical Action Items, "
                "Precautions, and Recommendations. Each section should provide clear, concise, and structured content that enhances operational effectiveness "
                "and supports mission success for special forces personnel."
            ),
            backstory=(
                "You are a seasoned military intelligence analyst with a specialized focus on special operations. "
                "Drawing upon years of experience and an in-depth understanding of special forces missions, you excel at dissecting complex After-Action Reports (AARs) "
                "to extract vital information that directly impacts the effectiveness and safety of frontline soldiers. "
                "Your outputs are meticulously structured into sections such as Mission Overview, Key Lessons Learned, Critical Action Items, Precautions, and Recommendations. "
                "This format ensures that special forces personnel can rapidly comprehend the information and apply it to future missions. "
                "You are adept at identifying both successful strategies and areas for improvement, ensuring soldiers are equipped to replicate successes and avoid mistakes. "
                "Your role supports quick decision-making, enhances operational readiness, and promotes continuous learning and adaptation within elite military units. "
                "Your commitment to excellence ensures that every summary you produce serves as a valuable tool for mission success and the ongoing development of special forces personnel."
            ),
            allow_delegation=False,
            tools=[self.file_reader],  
            verbose=True,
            llm_config=self.llm_config
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
            verbose=True,
            llm_config=self.llm_config
        )

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from a markdown file."""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.md':
                return self._extract_from_markdown(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")

        except Exception as e:
            raise Exception(f"Error extracting text from file: {str(e)}")

    def _extract_from_markdown(self, file_path: str) -> str:
        """Extract text from markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Error reading markdown file: {str(e)}")

    def process_aar(self, file_path: str):
        timings = []
        start_time = time.time()

        # Extract text from document
        try:
            extraction_start = time.time()
            text_content = self.extract_text_from_file(file_path)
            extraction_time = time.time() - extraction_start
            timings.append(
                (f"Document Extraction ({os.path.splitext(file_path)[1]})", extraction_time))
            print(f"\nExtracted text (first 200 chars):\n{text_content[:200]}\n")
            print(f"Total length of extracted text: {len(text_content)} characters\n")
        except Exception as e:
            print(f"Error reading document: {str(e)}")
            return None, None

        # Create tasks for the workflow
        tasks = []

        # Task 1: Document Processing
        task_start = time.time()
        task1 = Task(
            description="Process and structure the extracted document content",
            agent=self.document_processor,
            context=[{
                "description": "Process the following text extracted from the AAR document",
                "input": f"Process the following text extracted from the AAR document "
                f"and structure it appropriately:\n\n{text_content}",
                "expected_output": "A structured representation of the AAR content"
            }],
            output_file=os.path.join("output", "doc_processor.md"),

            expected_output="A structured representation of the AAR content with clear sections and formatting"
        )
        tasks.append(task1)

        # Task 2: Translation
        task2 = Task(
            description="Translate the structured content from Ukrainian to English",
            agent=self.translator,
            context=[task1],
            expected_output="An accurate English translation of the AAR that maintains military terminology and context"
        )
        tasks.append(task2)

        # Task 3: Summarization
        task3 = Task(
            description="Create a concise, actionable summary",
            agent=self.summarizer,
            output_file=os.path.join("output", "summarized_file.md"),
            context=[task2, task1],
            expected_output="A concise, actionable summary of the AAR highlighting key insights and recommendations"
        )
        tasks.append(task3)

        # Create and run the crew
        crew_start_time = time.time()
        crew = Crew(
            agents=[self.document_processor, self.translator,
                    self.summarizer],
            tasks=tasks,
            verbose=True
        )

        # Track individual task times
        task_times = {}

        def task_callback(task, output):
            task_times[task.description] = time.time()
            return output

        # Initialize start time for first task
        task_times["start"] = time.time()

        # Run the crew with task tracking
        result = crew.kickoff()

        # Calculate individual task durations
        task_descriptions = [t.description for t in tasks]
        for i in range(len(task_descriptions)):
            current_task = task_descriptions[i]
            next_time = task_times.get(
                task_descriptions[i + 1], time.time()) if i < len(task_descriptions) - 1 else time.time()
            duration = next_time - \
                (task_times.get(
                    task_descriptions[i-1], task_times["start"]) if i > 0 else task_times["start"])
            timings.append((f"Task {i+1}: {current_task}", duration))

        crew_time = time.time() - crew_start_time
        timings.append(("Total Crew Time", crew_time))

        total_time = time.time() - start_time
        timings.append(("Total Processing", total_time))

        return result, timings

    def handle_memory_creation(self, memory_data):
        """
        Process the received memory creation data from Omi Friend.
        """
        # Example: Extract and save transcript
        transcript = memory_data.get("transcript", "")
        with open('voice_memos.md', 'a') as f:
            f.write(f"## {memory_data.get('structured', {}).get('title', 'No Title')}\n")
            f.write(f"{transcript}\n\n")
        # Trigger further processing if needed

processor = AARProcessor()

@app.route('/omi_webhook', methods=['POST'])
def omi_webhook():
    try:
        data = request.json
        processor.handle_memory_creation(data)
        return Response(status=200)
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return Response(status=500)

def main():
    # Example usage
    processor = AARProcessor()

    # Process all files in docs directory
    docs_dir = "docs"
    supported_extensions = ['.md']

    if not os.path.exists(docs_dir):
        print(f"Error: Directory '{docs_dir}' does not exist!")
        return

    # Get all supported files in the docs directory
    files_to_process = []
    for file in os.listdir(docs_dir):
        if any(file.lower().endswith(ext) for ext in supported_extensions):
            files_to_process.append(os.path.join(docs_dir, file))

    if not files_to_process:
        print(f"No supported files found in '{docs_dir}' directory!")
        print(f"Supported file types: {', '.join(supported_extensions)}")
        return

    print(f"\nFound {len(files_to_process)} files to process:")
    for file in files_to_process:
        print(f"- {os.path.basename(file)}")
    print()

    # Process each file
    for file_path in files_to_process:
        print(f"\nProcessing: {os.path.basename(file_path)}")
        print("-" * 50)

        result, timings = processor.process_aar(file_path)

        if result is None:
            print(f"Failed to process {os.path.basename(file_path)}")
            continue

        # Save result to markdown file
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)

        # Generate timestamp for unique filename
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = os.path.splitext(os.path.basename(file_path))[0]
        output_file = os.path.join(output_dir, f"aar_analysis_{base_filename}_{timestamp}.md")
        timing_file = os.path.join(output_dir, "processing_times.md")

        # Save analysis results
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# After-Action Report Analysis\n\n")
            f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source file: {os.path.basename(file_path)}\n\n")
            f.write("## Analysis Results\n\n")
            f.write(str(result))  # Convert CrewOutput to string

        # Save or append timing results
        if os.path.exists(timing_file):
            with open(timing_file, "r", encoding="utf-8") as f:
                existing_content = f.read()
        else:
            existing_content = "# Processing Times Log\n\n"

        with open(timing_file, "w", encoding="utf-8") as f:
            f.write(existing_content)
            f.write(f"\n## Run at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {os.path.basename(file_path)}\n\n")
            f.write("| Step | Time (seconds) |\n")
            f.write("|------|----------------|\n")
            for step, duration in timings:
                f.write(f"| {step} | {duration:.2f} |\n")
            f.write("\n")

        print(f"\nAnalysis saved to: {output_file}")
        print(f"Timing information appended to: {timing_file}")
        print("-" * 50)


if __name__ == "__main__":
    # Run Flask app in a separate thread
    from threading import Thread

    flask_thread = Thread(target=lambda: app.run(port=5000, debug=True))
    flask_thread.start()

    main()
