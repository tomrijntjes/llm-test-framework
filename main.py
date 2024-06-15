from openai import OpenAI

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv
import os
import json



# Load environment variables from .env file
load_dotenv()

# Set your OpenAI API key from the environment variables
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Database connection details from the environment variables
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

def fetch_relevant_documents(patient_name, question):
    # Connect to the PostgreSQL database
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cursor = conn.cursor(row_factory=dict_row)

    # Query to fetch relevant documents based on the patient name and question
    query = """
    SELECT content
    FROM documents
    WHERE content ILIKE %s
    ORDER BY ts_rank_cd(document_tsvector, plainto_tsquery('dutch', %s)) DESC
    LIMIT 5;
    """

    cursor.execute(query, (f'%{patient_name}%', question))
    documents = cursor.fetchall()

    cursor.close()
    conn.close()

    return [doc['content'] for doc in documents]

def generate_prompt(patient_name, question, documents):
    prompt = f"Patient: {patient_name}\nQuestion: {question}\n\nRelevant Documents:\n"
    for i, doc in enumerate(documents, 1):
        prompt += f"Document {i}:\n{doc}\n\n"
    return prompt

format = json.dumps(
    {
  "patient": "patient name as string",
  "question": "question as string",
  "medications": [
      {
        "medication": "medication name",
        "strength": "strength as integer",
        "unit": "unit, eg. milligrams",
        "dosage": "how often, eg. 4 times a week",
        "purpose": "free text field describing the purpose",
      },
  ]}
)

def get_llm_response(prompt, model="gpt-4o"):
    response = client.chat.completions.create(
    model=model,
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": "You are a helpful assistant designed to output JSON. Based on the following documents, provide a detailed answer to the patient's question."},
        {"role": "system", "content": f"Your responses are always structured in the following {format} "},
        {"role": "system", "content": "the question should have some sort of demarcation of the patients history"},
        {"role": "system", "content": "Do not return results if the treatments found are not relevant to the question"},
        {"role": "system", "content": "medication names should only include the medical name, not the brand name"},
        {"role": "user", "content": prompt}
    ]
    )
    return response.choices[0].message.content



def main():
    patient_name = input("Enter the patient's name: ")
    question = input("Enter the question: ")

    documents = fetch_relevant_documents(patient_name, question)
    prompt = generate_prompt(patient_name, question, documents)
    print(f"Generated Prompt:\n{prompt}\n")

    response = get_llm_response(prompt)
    print(f"GPT-4 Response:\n{response}")

if __name__ == "__main__":
    main()

