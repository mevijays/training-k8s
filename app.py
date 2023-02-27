#!/usr/bin/env python3
#Import open AI OS and System Modules
import openai,os,sys
prompt = sys.argv[1]
openai.api_key = os.environ['OPENAI_KEY']
completions = openai.Completion.create(
    engine="text-davinci-003",
    prompt=prompt,
    max_tokens=1024,
    n=1,
    stop=None,
    temperature=0.5,
)
message = completions.choices[0].text
original_stdout = sys.stdout
with open('result.txt', 'w') as f:
    sys.stdout = f
    print(message)
    sys.stdout = original_stdout 
