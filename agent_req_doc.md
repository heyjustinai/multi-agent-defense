Product Requirements Document (PRD): AI Agent for Translating and Summarizing Ukrainian After-Action Reports (AARs)

1. Objective

Develop an AI Agent capable of translating Ukrainian After-Action Reports (AARs) in Microsoft Word (.docx) format into concise, actionable English summaries. The translation must preserve all semantics, nuances, cultural slang, and context to ensure frontline soldiers receive clear and pertinent information swiftly.

2. Key Requirements

2.1 Data Ingestion
    •    The AI Agent shall accept Ukrainian AARs in .docx format.
    •    It shall extract all text content, including headers, footers, and embedded tables, ensuring no information is overlooked.

2.2 Translation
    •    The AI Agent shall employ advanced Natural Language Processing (NLP) models trained in Ukrainian-English translation, with a focus on military terminology and slang.
    •    It shall accurately handle idiomatic expressions and cultural references, maintaining the original report’s intent and context.

2.3 Summarization
    •    The AI Agent shall generate concise summaries that highlight key actionable insights relevant to mission planning.
    •    Summaries shall be structured to emphasize critical information, ensuring clarity and brevity for quick comprehension.

2.4 Output Generation
    •    The AI Agent shall produce summaries in plain text or PDF format, based on operational requirements.
    •    It shall ensure the output is clear, focusing on readability and brevity to facilitate rapid understanding by frontline soldiers.

3. Implementation Details

3.1 Translation Engine

Utilize the Restack AI translation engine for the translation component. The following code snippet demonstrates the integration:

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

3.2 Summarization Algorithm
    •    Implement algorithms capable of identifying and extracting key information pertinent to military operations.
    •    Ensure the summarization process retains critical details while reducing verbosity.

4. Performance and Efficiency
    •    The AI Agent shall process and generate summaries within a reasonable timeframe to support operational needs.
    •    It shall maintain high accuracy, preserving the original report’s intent and context.

5. Security and Compliance
    •    The AI Agent shall comply with military data security standards, ensuring confidentiality and integrity of sensitive information.
    •    It shall handle varying volumes of AARs without performance degradation.

6. Target Audience
    •    The final output shall cater to frontline soldiers who prioritize speed and clarity in operational briefings.
    •    The AI Agent shall ensure the summaries are easily digestible, avoiding lengthy, technical jargon that could confuse the end-user.

By adhering to these requirements, the AI Agent will effectively translate and summarize Ukrainian AARs, providing frontline soldiers with clear, actionable insights in a timely manner.