import os
import re
import urllib.request
import urllib.error
import ssl
from concurrent.futures import ThreadPoolExecutor

CHAPTERS_DIR = "chapters"

# Regex for [text](url)
MD_LINK_REGEX = re.compile(r'\[[^\]]*\]\((http[s]?://[^\)]+)\)')
# Regex for [ref]: url
MD_REF_REGEX = re.compile(r'^\[[^\]]+\]:\s*(http[s]?://\S+)', re.MULTILINE)
# Bare URLs not in markdown links, rough guess
BARE_URL_REGEX = re.compile(r'<(http[s]?://[^>]+)>')

def extract_urls_from_file(filepath):
    urls = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        for match in MD_LINK_REGEX.findall(content):
            urls.add(match.strip())
        for match in MD_REF_REGEX.findall(content):
            urls.add(match.strip())
        for match in BARE_URL_REGEX.findall(content):
            urls.add(match.strip())
    return urls

def check_url(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    )
    try:
        response = urllib.request.urlopen(req, timeout=10, context=ctx)
        return (url, response.getcode(), None)
    except urllib.error.HTTPError as e:
        return (url, e.code, None)
    except urllib.error.URLError as e:
        return (url, None, str(e.reason))
    except Exception as e:
        return (url, None, str(e))

def main():
    all_urls = set()
    file_urls_map = {}
    
    for filename in os.listdir(CHAPTERS_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(CHAPTERS_DIR, filename)
            urls = extract_urls_from_file(filepath)
            if urls:
                file_urls_map[filepath] = urls
                all_urls.update(urls)
                
    print(f"Found {len(all_urls)} unique URLs across {len(file_urls_map)} files.")
    print("Checking URLs...")
    
    results = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_url, url): url for url in all_urls}
        for future in futures:
            url, status, error = future.result()
            results[url] = (status, error)
            
    # Report errors
    has_errors = False
    for filepath, urls in file_urls_map.items():
        file_errors = []
        for url in urls:
            status, error = results[url]
            # Ignore some known generic domains or examples
            if "example.com" in url or "localhost" in url or "127.0.0.1" in url:
                continue
            if status is not None and status >= 400:
                # 403 Forbidden is often just anti-scraping
                if status not in [403, 418]: # Ignore 403 and 418 (Often used by anti-bot)
                    file_errors.append((url, f"HTTP {status}"))
            elif error is not None:
                file_errors.append((url, f"Error: {error}"))
                
        if file_errors:
            has_errors = True
            print(f"\n--- Errors in {filepath} ---")
            for url, msg in file_errors:
                print(f"[{msg}] {url}")
                
    if not has_errors:
        print("\nNo critical URL errors found!")

if __name__ == "__main__":
    main()
