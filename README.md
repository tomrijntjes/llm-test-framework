# Extracting Medicine History - Test Framework

An experiment with structured testing and the LLM-as-Judge approach

## Prequisites

1. docker
1. postgres
1. `cp template.env .env` and add your OpenAI API key

## Run in interactive mode

```
make run
Enter the patient's name: de Vries
Enter the question: pijnstilling
```

## Run tests

```make test```
