import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1-mini"

from dotenv import load_dotenv
load_dotenv()
token = os.getenv('GITHUB_TOKEN')


client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(token),
)

# Reusable Functions
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

    return response.choices[0].message.content




def create_undetectable_chrome_driver():
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    
    chrome_options = Options()
    
    # Basic options to mimic real browser
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # User agent - use a recent Chrome user agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Window size (avoid headless detection)
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    
    # Additional options to avoid detection
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')
    
    # Language and platform
    chrome_options.add_argument('--lang=en-US')
    chrome_options.add_argument('--accept-lang=en-US,en;q=0.9')
    
    # Disable images for faster loading (optional)
    # prefs = {"profile.managed_default_content_settings.images": 2}
    # chrome_options.add_experimental_option("prefs", prefs)
    
    # Set additional preferences
    prefs = {
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_setting_values.notifications": 2
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Initialize driver
    # service = Service(ChromeDriverManager().install())
    import chromedriver_autoinstaller
    chromedriver_autoinstaller.install()

    # from selenium import webdriver
    # driver = webdriver.Chrome()

    # driver = webdriver.Chrome(service=service, options=chrome_options)
    driver = webdriver.Chrome( options=chrome_options)
    # Execute CDP commands to hide webdriver property
    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    })
    
    # Override navigator.webdriver property
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    # Add additional JavaScript to mimic real browser
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
            window.chrome = {
                runtime: {}
            };
            Object.defineProperty(navigator, 'permissions', {
                get: () => ({
                    query: () => Promise.resolve({state: 'prompt'})
                })
            });
        '''
    })
    
    return driver



def urlToScreenshot(url):
    from PIL import Image
    import io, time, os, re

    driver = create_undetectable_chrome_driver()
    driver.set_window_size(1366, 768)
    driver.get(url)
    time.sleep(5)

    # ── Source & Product name ────────────────────────────────────────
    source = re.search(r'https?://(?:www\.)?(chaldal|shwapno)', url).group(1)
    print('Source:', source)
    try:
        product = url.split('q=')[1].split('&')[0].replace('+', '_')
    except:
        product = url.split('/')[-1].split('?')[0].replace('+', '_')
    print('Product:', product)

    now = __import__('datetime').datetime.now()

    viewport_height = driver.execute_script("return window.innerHeight")
    current_pos = 0
    screenshots = []

    while True:
        driver.execute_script(f"window.scrollTo(0, {current_pos});")
        time.sleep(0.8)

        png = driver.get_screenshot_as_png()
        img = Image.open(io.BytesIO(png))
        screenshots.append(img)
        print(f"Screenshot taken at scroll position: {current_pos}")  # debug

        current_pos += viewport_height
        new_total = driver.execute_script("return document.body.scrollHeight")
        print(f"Total page height: {new_total}, Current pos: {current_pos}")  # debug

        if current_pos >= new_total:
            break

    driver.quit()
    print(f"Total screenshots taken: {len(screenshots)}")  # debug

    full_width = screenshots[0].width
    full_height = sum(img.height for img in screenshots)

    merged = Image.new('RGB', (full_width, full_height))
    y_offset = 0
    for img in screenshots:
        merged.paste(img, (0, y_offset))
        y_offset += img.height

  
    os.makedirs('SCREENSHOTS', exist_ok=True)
    filename = f'SCREENSHOTS/{source}_{product}_{now.strftime("%Y%m%d_%H%M%S")}.png'
    merged.save(filename)
    print(f'Screenshot saved: {filename}')
    
    return filename, source, product, now.strftime("%Y%m%d_%H%M%S")

    
def strLOFDToDf(resp):
    import pandas as pd
    import ast
    list_of_dicts = ast.literal_eval(resp)
    return pd.DataFrame(list_of_dicts)
  




  

