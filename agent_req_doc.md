Product Requirements Document (PRD): AI Assistant for Military Operations

1. Introduction

In modern military operations, timely access to actionable intelligence is critical for mission success. The proposed AI Assistant aims to enhance operational preparedness by providing military personnel with real-time, context-aware insights extracted from classified operational data. This assistant leverages advanced natural language processing to interpret and summarize key factors that influence mission planning.

METT-TC—an acronym for Mission, Enemy, Terrain and Weather, Troops and Support Available, Time Available, and Civil Considerations—is a framework used by the military to assess and plan missions. Understanding and analyzing METT-TC factors are crucial for effective decision-making on the battlefield.

2. Objective

The goal is to develop a secure, intelligent AI assistant capable of ingesting, translating, and summarizing classified operational documents to provide actionable insights based on METT-TC factors. This assistant will reduce the likelihood of repeated mistakes, improve decision-making processes, and streamline knowledge sharing across military units.

3. Requirements

Data Ingestion

	•	Secure Document Handling: The system must securely accept and process classified documents, including After-Action Reports (AARs) in various formats (e.g., .docx, .pdf).
	•	Comprehensive Extraction: Extract all textual content, including headers, footers, and embedded elements, ensuring no information is overlooked.

Natural Language Processing

	•	Advanced Translation: Utilize NLP models trained in military terminology, including slang and idiomatic expressions.
	•	METT-TC Analysis: Extract and summarize key insights based on METT-TC factors.
	•	Language Support: Translate documents from foreign languages (e.g., Ukrainian) to English while preserving semantics and context.

Query Interface

	•	User-Friendly Interaction: Provide an intuitive natural language interface that allows users to query the system using spoken or typed language.
	•	Context-Aware Responses: Support real-time, relevant answers to user inquiries.

Security Compliance

	•	Operational Levels: Operate within Impact Level 4 (IL4) to Impact Level 6 (IL6) security environments.
	•	Data Protection: Ensure confidentiality, integrity, and availability of sensitive information throughout processing and storage.

4. Features

Secure Document Ingestion and Indexing

	•	Implement secure channels for document upload.
	•	Index ingested documents for efficient retrieval and analysis.

Translation and Summarization

	•	Translate operational reports to English accurately, maintaining military terminology.
	•	Generate concise summaries highlighting key actionable insights relevant to METT-TC factors.

Proactive Alerts and Adaptive Checklists

	•	Provide proactive alerts for mission-critical information extracted from documents.
	•	Generate adaptive checklists based on METT-TC analysis to aid mission planning and execution.

Real-Time, Context-Aware Responses

	•	Offer real-time assistance by answering user queries with relevant information.
	•	Understand context to provide accurate and meaningful responses.

5. Implementation Details

Translation Engine

Utilize the Restack AI translation engine for accurate translation of operational documents.

Integration Code Snippet:

from restack_ai.function import function, log
from openai import OpenAI
from dataclasses import dataclass
import os

@dataclass
class FunctionInputParams:
    user_prompt: str

@function.defn()
async def translate(input: FunctionInputParams):
    try:
        log.info("translate function started", input=input)
        if not os.environ.get("OPENBABYLON_API_URL"):
            raise Exception("OPENBABYLON_API_URL is not set")

        client = OpenAI(api_key='openbabylon', base_url=os.environ.get("OPENBABYLON_API_URL"))

        messages = []
        if input.user_prompt:
            messages.append({"role": "user", "content": input.user_prompt})
        print(messages)
        response = client.chat.completions.create(
            model="orpo-mistral-v0.3-ua-tokV2-focus-10B-low-lr-1epoch-aux-merged-1ep",
            messages=messages,
            temperature=0.0
        )
        log.info("translate function completed", response=response)
        return response.choices[0].message
    except Exception as e:
        log.error("translate function failed", error=e)
        raise e

Summarization Algorithm

	•	Implement algorithms capable of extracting key METT-TC insights from documents.
	•	Use machine learning models trained on military operational data to identify critical information.
	•	Ensure summaries are concise and emphasize mission-critical details.

Flow Integration

Map sequence diagram roles to system components to ensure seamless operation.

Technical Architecture

	•	TranslationAgent: Handles document translation.
	•	PreprocessingAgent: Processes raw data for analysis.
	•	DataIngestionAPI: Manages secure data ingestion.
	•	PromptEngine: Generates prompts for the LLM based on user queries.
	•	LLM (Large Language Model): Performs natural language understanding and generates responses.
	•	RAGSystem (Retrieval-Augmented Generation System): Enhances responses with retrieved data.
	•	ChatbotInterface: User-facing interface for interactions.

6. Sequence Diagram Integration

Workflow Description

	1.	Document Ingestion: Users upload classified documents via the DataIngestionAPI.
	2.	Preprocessing: The PreprocessingAgent extracts and cleans the data.
	3.	Translation: The TranslationAgent translates documents into English.
	4.	Indexing: Processed documents are indexed for retrieval.
	5.	User Query: The user interacts with the ChatbotInterface, submitting a query.
	6.	Prompt Generation: The PromptEngine formulates a prompt for the LLM.
	7.	Response Generation: The LLM generates a response, augmented by the RAGSystem.
	8.	Delivery: The ChatbotInterface presents the response to the user.

Component Roles

	•	TranslationAgent: Translates documents, enabling analysis of non-English reports.
	•	PromptEngine: Crafts prompts that guide the LLM to produce relevant responses.
	•	RAGSystem: Enhances LLM outputs with specific data from the indexed documents.
	•	ChatbotInterface: Provides a user-friendly interface for interaction and displays results.

7. Target Audience

Users

	•	Frontline soldiers requiring quick access to operational insights.
	•	Mission planners needing detailed analysis of METT-TC factors.
	•	Intelligence officers analyzing operational reports for strategic planning.

Needs

	•	Rapid retrieval of critical information.
	•	Clear, concise summaries without unnecessary technical jargon.
	•	An intuitive interface that requires minimal training.

8. Performance & Security

Processing Speed

	•	Generate translations and summaries promptly to support time-sensitive operations.
	•	Optimize algorithms for efficiency without compromising accuracy.

Compliance

	•	Adhere strictly to military data security protocols (IL4-IL6).
	•	Implement robust encryption for data at rest and in transit.
	•	Ensure regular security audits and compliance checks.

Sequence Diagram Mapping

Each component of the sequence diagram corresponds to the following PRD sections:
	•	TranslationAgent: Maps to the Translation Engine in Implementation Details.
	•	PreprocessingAgent and DataIngestionAPI: Addressed under Requirements (Data Ingestion).
	•	PromptEngine, LLM, and RAGSystem: Linked to Features (Query Interface and Proactive Assistance).
	•	ChatbotInterface: Tied to Target Audience and usability goals.

By developing this AI Assistant, military personnel will have enhanced capabilities to access and analyze critical operational data swiftly and securely, leading to more informed decision-making and increased mission success rates.