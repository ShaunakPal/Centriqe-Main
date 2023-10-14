import openai
from time import time, sleep
import os
import textwrap
import sys
from dotenv import load_dotenv



###     file operations
def save_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as outfile:
        outfile.write(content)


def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as infile:
        return infile.read()

def chatbot(conversation, model="gpt-3.5-turbo-16k", temperature=0):
    max_retry = 7
    retry = 0
    while True:
        try:
            response = openai.ChatCompletion.create(model=model, messages=conversation, temperature=temperature)
            text = response['choices'][0]['message']['content']
            return text, response['usage']['total_tokens']
        except Exception as oops:
            print(f'\n\nError communicating with OpenAI: "{oops}"')
            if 'maximum context length' in str(oops):
                a = conversation.pop(0)
                print('\n\n DEBUG: Trimming oldest message')
                continue
            retry += 1
            if retry >= max_retry:
                print(f"\n\nExiting due to excessive errors in API: {oops}")
                exit(1)
            print(f'\n\nRetrying in {2 ** (retry - 1) * 5} seconds...')
            sleep(2 ** (retry - 1) * 5)

def get_user_input():
    # get user input
    text = input('\n\n\nUSER:\n\n')
    
    # check if scratchpad updated, continue
    if 'DONE' in text:
        print('\n\n\nThank you for participating in this survey! Your results have been saved. Program will exit in 5 seconds.')
        sleep(5)
        exit(0)
    if text == '':
        # empty submission, probably on accident
        None
    else:
        return text

def compose_conversation(ALL_MESSAGES, a, system_message):
    # continue with composing conversation and response
    ALL_MESSAGES.append({'role': 'user', 'content': a})
    conversation = list()
    conversation += ALL_MESSAGES
    conversation.append({'role': 'system', 'content': system_message})
    return conversation

def generate_chat_response(ALL_MESSAGES, conversation):
    # generate a response
    response, tokens = chatbot(conversation)
    print(tokens)
    if tokens > 7500:
        print('Unfortunately, this conversation has become too long, so the conversation must come to an end. Program will end in 5 seconds.')
        sleep(5)
        exit(0)
    ALL_MESSAGES.append({'role': 'assistant', 'content': response})
    print('\n\n\n\nCHATBOT:\n')
    formatted_lines = [textwrap.fill(line, width=120, initial_indent='    ', subsequent_indent='    ') for line in response.split('\n')]
    formatted_text = '\n'.join(formatted_lines)
    print(formatted_text)


if __name__ == '__main__':
    load_dotenv() # load the environment
    # instantiate chatbot, variables
    openai.api_key = os.getenv("OPENAI_API_KEY")
    system_message = open_file('system.txt')
    ALL_MESSAGES = list()
    start_time = time()
    
    # compose the conversation
    a = input('\n\nUSER: ')
    conversation = compose_conversation(ALL_MESSAGES, a, system_message)
    generate_chat_response(ALL_MESSAGES, conversation)

    while True:
        a = get_user_input()
        if not a:
            continue
        
        conversation = compose_conversation(ALL_MESSAGES, a, system_message)      
        generate_chat_response(ALL_MESSAGES, conversation)