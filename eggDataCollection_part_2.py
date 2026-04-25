from basicFunctions import *
import re

###### EGG
def collectEggData(source='swapno'):

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

    # Extract model name from filename e.g. "by_openai_gpt-4.1-mini"
    model_match = re.search(r'by_(\w+)_([\w.\-]+)\.txt', latest_file)
    if model_match:
        provider = model_match.group(1)
        model_name = model_match.group(2)
        model_tag = f'by_{provider}_{model_name}'
    else:
        model_tag = 'by_unknown'

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


def collectEggDataFromAllSources():
    collectEggData(source='chaldal')
    collectEggData(source='swapno')

