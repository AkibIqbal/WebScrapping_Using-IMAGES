#Clearing raw text files then making it CLEAN and CSV by using xai/grok-3-mini-instruct model

import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

endpoint = "https://models.github.ai/inference"
model = "xai/grok-3-mini"

from dotenv import load_dotenv
load_dotenv()
token = os.getenv('GITHUB_TOKEN')

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

def respGenerator(role, prompt, model=model, temperature=1, image_path=None):
    
    if image_path:
        import base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        user_content = [
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{image_data}"}
            },
            {
                "type": "text",
                "text": prompt
            }
        ]
    else:
        user_content = prompt

    response = client.complete(
        messages=[
            SystemMessage(content=role),
            UserMessage(content=user_content),
        ],
        temperature=temperature,
        model=model
    )

    return response.choices[0].message.content, model


def strLOFDToDf(resp):
    import pandas as pd
    import ast
    list_of_dicts = ast.literal_eval(resp)
    return pd.DataFrame(list_of_dicts)

import re

def collectEggDataGrok(source='swapno'):

    if source == 'chaldal':
        src = 'chaldal'
        product = 'eggs'
    else:
        src = 'shwapno'
        product = 'eggs'

    import glob
    files = glob.glob(f'TEXTS/{src}_{product}_*.txt')
    files = [f for f in files if 'clean' not in f]
    latest_file = max(files, key=os.path.getctime)
    print(f'Using file: {latest_file}')

    with open(latest_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    match = re.search(r'(\d{8}_\d{6})', latest_file)
    timestamp = match.group(1)

    role = "You are a data engineer that extracts structured data from text."

    prompt = """Extract all chicken egg items from this grocery page text and output them in JSON format like this:
[
    {
        "product_name": "name of the egg product (only chicken egg)",
        "category": "loose or packet",
        "price": "price in numbers only (without ৳ symbol)",
        "number_of_unit": "number of eggs (e.g., 4, 12, etc.)",
        "product_type": "loose or packet"
    }
]
Requirements:
- Include both loose eggs and packed/branded eggs
- For loose eggs sold per piece, calculate price per minimum number of eggs to buy (multiply single egg price by minimum quantity)
- For packed eggs, use the total price
- Category should be either "loose" or "packet"
- Price should be numeric value only, excluding the ৳ symbol
- number_of_unit should reflect the number of eggs (e.g., 4, 12, etc.)
- Only include actual eggs (chicken eggs)
- Exclude egg noodles, egg-based dishes, egg shampoo, or any other non-egg products
- Use current/discounted prices where applicable
from the given text: """ + raw_text

    resp, model_used = respGenerator(role=role, prompt=prompt)

    # model_used theke model_tag banao
    provider = model_used.split('/')[0]
    model_name = model_used.split('/')[1]
    model_tag = f'by_{provider}_{model_name}'

    os.makedirs('TEXTS', exist_ok=True)
    text_filename = f'TEXTS/{src}_{product}_{timestamp}_{model_tag}_clean.txt'
    with open(text_filename, 'w', encoding='utf-8') as f:
        f.write(resp)
    print(f'Text saved: {text_filename}')

    df = strLOFDToDf(resp)
    df.dropna(inplace=True)

    prompt2 = """Extract the brand name from each product title and return a JSON array of { brand_name}. otherwise use 'loose'. Do not add any text. 
    [the output is only list of dictionaries without any extra text]
                the product titles are:
                """ + ', '.join(df['product_name'].tolist())

    resp2, _ = respGenerator(role=role, prompt=prompt2)
    df2 = strLOFDToDf(resp2)
    df2.dropna(inplace=True)

    import pandas as pd
    import datetime
    df = pd.concat([df, df2], axis=1)
    now = datetime.datetime.now()
    df['date'] = now.strftime("%Y-%m-%d")
    df['time'] = now.strftime("%H:%M:%S")
    if source == 'chaldal':
        df['source'] = 'Chaldal'
    else:
        df['source'] = 'Shwapno'
    df['genera'] = 'egg'
    df['unit'] = 'piece'

    df = df[['date', 'time', 'source', 'genera', 'brand_name', 'product_name', 'product_type', 'unit', 'number_of_unit', 'price']]

    os.makedirs('Updated-data', exist_ok=True)
    if source == 'chaldal':
        csv_path = f'Updated-data/chaldal_egg_data_{now.strftime("%Y%m%d_%H%M%S")}_{model_tag}.csv'
    else:
        csv_path = f'Updated-data/swapno_egg_data_{now.strftime("%Y%m%d_%H%M%S")}_{model_tag}.csv'

    df.to_csv(csv_path, index=False)
    print(f'CSV saved: {csv_path}')


def collectEggDataFromAllSourcesGrok():
    collectEggDataGrok(source='chaldal')
    collectEggDataGrok(source='swapno')