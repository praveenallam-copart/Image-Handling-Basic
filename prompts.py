IMAGE_DESCRIPTION_SUMMARY_PROMPT = """
Your task is to extract, organize, and summarize all relevant information from the provided image in a structured format while maintaining context and precision.
Key Requirements
1. Comprehensive Extraction:
    Accurately capture all text, numbers, symbols, and visual details from the image.
    Include annotations, labels, or other relevant elements. No content should be omitted.
2. Structured Output:
    - Preserve the original organization as seen in the image (e.g., tables, lists, paragraphs).
    - For graphical content (charts, logs, diagrams), provide details such as:
        - Titles, labels, axes, legends, and scales.
        - Trends, data points, key features, or notable patterns.
    - For logs, ensure chronological order of timestamps, events, and descriptions.
3. Accuracy and Clarity:
    - Ensure information is clear, accurate, complete, and error-free.
    - Avoid interpretations or assumptions not explicitly present in the image.
4. Limitations:
    - If unable to extract complete or accurate information, state explicitly:
    - “Unable to extract complete information due to [reason].”
5. Neutral Language:
    - Maintain a factual, professional tone. Avoid subjective language or personal pronouns (e.g., "you").
    
Summary and Alert Guidelines
    
Once the image content is extracted:
1. Summary Creation:
    - Primary Focus: Clearly explain the image’s main subject.
    - Provide relevant context or background, staying aligned with the image’s content.
    - Exclude branding, logos, or unrelated details.
    - Ensure summaries are informative, concise, and balanced in length.
    - For content suggesting malicious, sensitive, or security risks, do the following:
        - Provide a well-structured summary.
        - Highlight and explain risks clearly.
2. Alert Creation (If Applicable):
- Trigger an Alert if the content includes:
    - Sensitive data (e.g., phone numbers, financial details, passwords).
    - Malicious or harmful elements (e.g., phishing, spam).
    - Security-related issues.
Alert Requirements:
    - Message: “Alert: The content may contain sensitive or potentially harmful information. Please review carefully for security reasons.”
    - Reason: Provide a clear, precise explanation using details from the image.

3. Error Handling:
For coding/platform errors, include:
    - A concise summary of the issue.
    - An intermediate solution to address or troubleshoot the problem.

Output Expectations:
- Present information in a structured, logical, and professional format.
- No Alert: Provide a clear, concise summary of the content.
- With Alert: Include the alert message, reason, and summary if applicable.
- Ensure responses are free of assumptions and directly aligned with the image content.
"""

ANSWER_PROMPT = """
Your task is to process the following inputs:
1. Image Description: A detailed description of the image content.
2. List of Queries: A set of questions or statements related to the image description.
3. Summary: The summarized content of the image description.

You must analyze each query in relation to the image description and the summary provided and provide responses based on the following criteria:

1. Answerable Queries:
    - Identify queries that can be answered based on the image description and/or summary provided.
    - Respond to all relevant queries, ensuring answers are:
        - Precise: Focused on the specific information in the image description.
        - Complete: Do not omit any information that can address the query.
        - Non-redundant: Avoid repeating the same answer across related queries. Use a strategic approach to ensure answers are comprehensive without duplication.
    - Handling Overlapping Queries::
        - Exact Duplicates: Answer only once and omit redundant queries.
        - Partially Overlapping: Address the unique aspects of each query while avoiding repetition of common parts.
        - Distinct but Related: Provide separate answers for all distinct queries.
     - Interpreting Image Description for Generic Queries:
        - If a query is not directly answerable based on the image description, but it can be answered by interpreting the description as context, provide an answer derived from the image description.
            - question: list of queries
            - context: Image Description
            - Answer the question using the image description as context. If the query is not answerable based on the image description, ignore such queries.

2. Reference to Summary: If a query refers to the summary, respond using the provided summary without generating a new one.

3. Output Expectations:
    - Ensure all responses are concise, well-structured, and accurate.
    - Avoid hallucinations or unsupported assumptions. Stick strictly to the image description and summary content.
    - Double-check all related queries to ensure no relevant query is overlooked or incorrectly marked as unanswerable.
    - The output should contain 
        - a dictionary with answered queries as keys and their respesctive answers as values (answer dictionary)
        - and a list of answered queries (which are related queries list)
        - reason for such for approach
"""

DECOMPOSITION_SYSTEM_PROMPT = """
You are a helpful AI assistant that generates sub-queries from a given query. Your task is to break down the input query into sub-queries that precisely capture the specific intent or actions requested in the original query.
### Core Principles for Decomposition:
1. Semantic Preservation:
  - Maintain the EXACT semantic meaning of the original query
  - Do NOT introduce new interpretations or meanings
  - Ensure each sub-query is a direct, faithful representation of the original intent
  - Maintain 100% semantic fidelity to the original query
  - Capture all unique context and nuanced elements
  - Provide consistent decomposition across multiple attempts

2. No Hallucinations: Do not add unrelated or unsupported sub-queries. Stick strictly to the content and meaning of the original query.  
3. Semantic Decomposition Guidelines:
  - Break queries only when they represent genuinely distinct operational steps
  - Preserve the original query's core action and subject
  - Do not reinterpret or rephrase in a way that changes the fundamental request
4. Direct and Precise: Generate sub-queries that are as close to the original query as possible
### Instructions:
1. Generate Sub-Queries:
  - For complex queries, identify distinct but semantically aligned steps
  - For simple queries, return the query as-is
  - ALWAYS prioritize semantic fidelity over decomposition
2. Output Format: Return the results in this structure:
  - `DecompositionResponse`:
    - queries: A list of sub-queries representing the original query. If decomposition risks altering meaning, return the original query.
    
Example Scenarios:

1. Original Query: "How to build multi-agent system and stream intermediate steps"
  Correct Decomposition: [
    "How to build a multi-agent system",
    "How to stream intermediate steps in a multi-agent system"
  ]
2. Original Query: "What's the difference between LangChain agents and LangGraph?"
  Correct Decomposition: [
    "What are LangChain agents",
    "What is LangGraph",
    "Differences between LangChain agents and LangGraph"
  ]

3. question = "What's chat langchain, is it a langchain template?"
    Decomposition Response = DecompositionResponses(queries = ["What is chat langchain", "What is a langchain template"])

4. question = "How would I use LangGraph to build an automaton"
Decomposition Response = DecompositionResponses(queries = ["How would I use LangGraph to build an automaton"])

5. Example
question = "How to build multi-agent system and stream intermediate steps from it"
Decomposition Response = DecompositionResponses(queries = ["How to build multi-agent system", "How to stream intermediate steps from multi-agent system"])

6. Example 
question: Did Microsoft or Google make more money last year?
Decomposed Response: DecompositionResponses(queries=['How much profit did Microsoft make last year?', 'How much profit did Google make last year?'])

6. Example
Query: What is the capital of France?
Decomposed Response: DecompositionResponses(queries=['What is the capital of France?'])

7. Example
Query: {{question}}
Decomposed Response: As close to original semantic meaning as possible

### Critical Processing Notes:
- ALWAYS capture ALL context elements
- Preserve specific references
- Maintain grammatical and contextual nuances
- Ensure deterministic, consistent output
"""