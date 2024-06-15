from main import fetch_relevant_documents, generate_prompt, get_llm_response, client
import json

def test_astma_tak():
    question = "asthma"
    
    # Tak has been treated for asthma with two medications

    patient_name = "Tak"
    documents = fetch_relevant_documents(patient_name, question)
    prompt = generate_prompt(patient_name, question, documents)
    response = get_llm_response(prompt)
    result_dict = json.loads(response)
    assert result_dict["patient"] == patient_name
    assert len(result_dict["medications"]) == 2
    medications = sorted([m["medication"].lower() for m in result_dict["medications"]])
    assert medications == ['beclometason', 'salbutamol']

def test_astma_almeda():
    question = "asthma"

    # Almeda has not been treated for asthma
    patient_name = "Almeda"
    documents = fetch_relevant_documents(patient_name, question)
    prompt = generate_prompt(patient_name, question, documents)
    response = get_llm_response(prompt)
    result_dict = json.loads(response)

    assert result_dict["patient"] == patient_name
    assert len(result_dict["medications"]) == 0


def test_pijnstilling_tak():
    question = "pijnstilling"

    patient_name = "Tak"
    documents = fetch_relevant_documents(patient_name, question)
    prompt = generate_prompt(patient_name, question, documents)
    response = get_llm_response(prompt)
    result_dict = json.loads(response)

    assert result_dict["patient"] == patient_name
    assert len(result_dict["medications"]) == 2

    medications = sorted([m["medication"].lower() for m in result_dict["medications"]])
    assert medications == ['ibuprofen','paracetamol']

def test_pijnstilling_devries():
    question = "pijnstilling"

    patient_name = "de Vries"
    documents = fetch_relevant_documents(patient_name, question)
    prompt = generate_prompt(patient_name, question, documents)
    response = get_llm_response(prompt)
    result_dict = json.loads(response)

    assert result_dict["patient"] == patient_name
    medications = sorted([m["medication"].lower() for m in result_dict["medications"]])
    assert len(medications) == 4
    assert medications == ['butylscopolamine', 'diclofenac', 'ibuprofen', 'sumatriptan']

def test_compare_models_pijnstilling_devries():
    format = json.dumps(
        {
        "score_one": "likert scale number judging the quality of the first input",
        "score_two": "likert scale number judging the quality of the second input",
        "explanation": "reasoning behind the scope",
        }
    )

    question = "pijnstilling"
    patient_name = "de Vries"

    documents = fetch_relevant_documents(patient_name, question)
    prompt = generate_prompt(patient_name, question, documents)
    gpt4_response = get_llm_response(prompt, model="gpt-4o")
    print(json.dumps(gpt4_response))

    documents = fetch_relevant_documents(patient_name, question)
    prompt = generate_prompt(patient_name, question, documents)
    gpt35_response = get_llm_response(prompt, model="gpt-3.5-turbo-0125")
    print(json.dumps(gpt35_response))

    response = client.chat.completions.create(
    model="gpt-4o",
    response_format={ "type": "json_object" },
    messages=[
        {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
        {"role": "system", "content": f"Your responses are always structured in the following {format} "},
        {"role": "system", "content": "Your job is to judge the output of two models and rate them with a likert scale number"},
        {"role": "system", "content": "Accuracy is valued. Explain your reasoning as well as possible. Ties are allowed"},
        {"role": "user", "content": f"input data: {documents}"},
        {"role": "user", "content": f"submission one: {gpt4_response}"},
        {"role": "user", "content": f"submission two: {gpt35_response}"},
    ]
    )
    result_dict = json.loads(response.choices[0].message.content)
    print(result_dict)
    assert result_dict["score_one"] > result_dict["score_two"]


    