from basicFunctions import *

###### EGG
def collectEggData(source='swapno'):
    # ── TEXTS folder থেকে raw text পড়ো ─────────────────────────────
    if source == 'chaldal':
        src = 'chaldal'
        product = 'eggs'
    else:
        src = 'shwapno'
        product = 'egg'

    # TEXTS folder থেকে সবচেয়ে নতুন file টা নাও
    import glob
    files = glob.glob(f'TEXTS/{src}_{product}_*.txt')
    latest_file = max(files, key=os.path.getctime)
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()

    timestamp = latest_file.split('_')[-2] + '_' + latest_file.split('_')[-1].replace('.txt', '')

    # ── Raw text থেকে AI দিয়ে data extract করো ─────────────────────
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

    resp = respGenerator(role=role, prompt=prompt)

    # ── TEXTS folder এ clean file save করো ──────────────────────────
    os.makedirs('TEXTS', exist_ok=True)
    text_filename = f'TEXTS/{src}_{product}_{timestamp}_clean.txt'
    with open(text_filename, 'w', encoding='utf-8') as f:
        f.write(resp)
    print(f'Text saved: {text_filename}')

    # ── Convert response to DataFrame ──────────────────────────────
    df = strLOFDToDf(resp)
    df.dropna(inplace=True)

    prompt2 = """Extract the brand name from each product title and return a JSON array of { brand_name}. otherwise use 'loose'. Do not add any text. 
    [the output is only list of dictionaries without any extra text]
                the product titles are:
                """ + ', '.join(df['product_name'].tolist())
  
    resp = respGenerator(role = role, prompt= prompt2)
    df2 = strLOFDToDf(resp)
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

    df = df[['date', 'time', 'source', 'genera', 'brand_name', 'product_name', 'product_type','unit', 'number_of_unit',  'price']]

    if source == 'chaldal':
      df.to_csv(f'Updated-data/chaldal_egg_data_{now.strftime("%Y%m%d_%H%M%S")}.csv', index=False)
    else:
      df.to_csv(f'Updated-data/swapno_egg_data_{now.strftime("%Y%m%d_%H%M%S")}.csv', index=False)


def collectEggDataFromAllSources():
    collectEggData(source='chaldal')
    collectEggData(source='swapno')

