import os
import re
import time
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from tqdm import tqdm

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,en;q=0.5",
    "Connection": "keep-alive",
    "Referer": "https://tsumego.com/sets",
    "Cookie": "lastVisit=2133; mode=1; lightDark=light; lastSet=50; secondsCheck=15460300; misplays=1;"
}

def clean_sgf_js(raw_js_array_content):
    """
    Takes the raw content found inside the JS Blob brackets: 
    e.g. "(;GM[1]...ST[2]"+"\n"+"RU[Japanese]..."+"\n"+""
    
    Returns clean SGF text.
    """
    # 1. Replace the concatenation pattern '"+"\n"+"' where \n is literal backslash-n
    content = raw_js_array_content.replace('"+"\\n"+"', '\n')
    
    # 2. Handle variations with spaces
    content = re.sub(r'"\s*\+\s*"\\n"\s*\+\s*"', '\n', content)

    # 3. Handle the trailing artifact '"+"\n"+""'
    content = content.replace('"+"\\n"+""', '')
    content = re.sub(r'"\s*\+\s*"\\n"\s*\+\s*""', '', content)

    # 4. Remove any remaining " + " patterns if they exist (though usually it's just the newlines)
    content = re.sub(r'"\s*\+\s*"', '', content)

    # 5. Remove the surrounding quotes from the JS string literals.
    content = content.strip()
    if content.startswith('"'):
        content = content[1:]
    if content.endswith('"'):
        content = content[:-1]
        
    return content

def sanitize_filename(name):
    name = name.replace("/", "_")
    name = re.sub(r'[<>:"\\|?*]', '', name)
    return name.strip()

def get_problem_details(problem_url):
    try:
        response = requests.get(problem_url, headers=HEADERS)
        if response.status_code != 200:
            print(f"Failed to load {problem_url}: {response.status_code}")
            return None, None

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # --- Extract Title ---
        title_tag = soup.select_one('#playTitleA')
        raw_title = title_tag.text.strip() if title_tag else f"Problem_{int(time.time())}"

        # --- Extract SGF using Broad Regex ---
        # Capture everything inside the brackets: var blob = new Blob([ CAPTURE_THIS ], {type: "sgf"}
        # We use a non-greedy match until the first ']' followed by ',{'
        match = re.search(r'var blob = new Blob\(\[(.*?)\]\s*,\s*\{', response.text, re.DOTALL)
        
        sgf_content = None
        if match:
            raw_js_content = match.group(1)
            sgf_content = clean_sgf_js(raw_js_content)
        else:
            print(f"No SGF Blob found in {problem_url}")

        return raw_title, sgf_content

    except Exception as e:
        print(f"Error fetching {problem_url}: {e}")
        return None, None

def main():
    parser = argparse.ArgumentParser(description='Download Tsumego Hero collections and convert them to SGF files.')
    parser.add_argument('url', help='The URL of the collection to download (e.g., https://tsumego.com/sets/view/50/1).')
    parser.add_argument('--output', default='.', help='The parent output directory. A subdirectory named after the collection will be created here to store the SGF files.')
    args = parser.parse_args()

    parsed_url = urlparse(args.url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    collection_url = args.url
    
    print(f"Fetching collection: {collection_url}...")
    response = requests.get(collection_url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"Failed to access collection page: {response.status_code}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    # --- 1. Extract Correct Collection Name ---
    collection_name_tag = soup.select_one('.homeLeft .title4')
    collection_name = collection_name_tag.text.strip() if collection_name_tag else "Tsumego_Collection"
    
    folder_name = os.path.join(args.output, sanitize_filename(collection_name))
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created directory: {folder_name}")

    # --- 2. Extract Problem Links ---
    problem_links = []
    link_elements = soup.select('li.statusN a.tooltip, li.statusV a.tooltip')
    for link in link_elements:
        href = link.get('href')
        if href:
            problem_links.append(href)

    print(f"Found {len(problem_links)} problems in '{collection_name}'. Starting download...")

    # --- 3. Iterate and Download ---
    for rel_link in tqdm(problem_links, desc="Downloading problems"):
        full_url = f"{base_url}{rel_link}"
        
        title, sgf_content = get_problem_details(full_url)
        
        if title and sgf_content:
            filename = f"{sanitize_filename(title)}.sgf"
            file_path = os.path.join(folder_name, filename)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(sgf_content)
        else:
            tqdm.write(f"Skipped: {rel_link}")
        
        time.sleep(1)

    print("\nDownload complete.")

if __name__ == "__main__":
    main()