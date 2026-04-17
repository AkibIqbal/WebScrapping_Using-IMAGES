from basicFunctions import *

###### EGG
def collectEggData(source='swapno'):
    if source == 'chaldal':
        screenshot_path, src, product, timestamp = urlToScreenshot('https://chaldal.com/eggs?')
    else:
        screenshot_path, src, product, timestamp = urlToScreenshot('https://www.shwapno.com/search?q=egg')

    # ── Screenshot থেকে AI দিয়ে data extract করো ───────────────────
    role = "You are a data engineer that extracts structured data from images of grocery websites."

    prompt = """Extract all chicken egg items from this grocery page screenshot and output them in JSON format like this:
[
    {
        "product_name": "name of the egg product (only chicken egg)",
        "product_type": "loose or packet",
        "price": "price in numbers only (without ৳ symbol)",
        "number_of_unit": "number of eggs (e.g., 4, 12, etc.)"
    }
]
Requirements:
- Only include actual chicken eggs
- Exclude egg noodles, egg-based dishes, egg shampoo, or any other non-egg products
- Price should be numeric value only
- Use current/discounted prices where applicable
- Output only the JSON list, no extra text"""

    resp = respGenerator(role=role, prompt=prompt, image_path=screenshot_path)

    # ── TEXTS folder এ save করো ─────────────────────────────────────
    os.makedirs('TEXTS', exist_ok=True)
    text_filename = f'TEXTS/{src}_{product}_{timestamp}.txt'
    with open(text_filename, 'w', encoding='utf-8') as f:
        f.write(resp)
    print(f'Text saved: {text_filename}')


def collectEggDataFromAllSources():
    collectEggData(source='chaldal')
    collectEggData(source='swapno')