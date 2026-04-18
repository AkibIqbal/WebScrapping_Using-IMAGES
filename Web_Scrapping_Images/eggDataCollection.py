from basicFunctions import *

###### EGG
def collectEggDataSS(source='swapno'):
    if source == 'chaldal':
        screenshot_path, src, product, timestamp = urlToScreenshot('https://chaldal.com/eggs?')
    else:
        screenshot_path, src, product, timestamp = urlToScreenshot('https://www.shwapno.com/search?q=egg')

    # ── Screenshot থেকে AI দিয়ে data extract করো ───────────────────
    role = "You are a data engineer that extracts structured data from images of grocery websites."

    prompt = prompt = """Extract all text from this screenshot exactly as it appears. 
Do not format, do not summarize, do not add any extra text. 
Just raw text, exactly as shown on the page."""

    resp = respGenerator(role=role, prompt=prompt, image_path=screenshot_path)

    # ── TEXTS folder এ save করো ─────────────────────────────────────
    os.makedirs('TEXTS', exist_ok=True)
    text_filename = f'TEXTS/{src}_{product}_{timestamp}.txt'
    with open(text_filename, 'w', encoding='utf-8') as f:
        f.write(resp)
    print(f'Text saved: {text_filename}')


def collectEggDataFromAllSources_SS():
    collectEggDataSS(source='chaldal')
    collectEggDataSS(source='swapno')