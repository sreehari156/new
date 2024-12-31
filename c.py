from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright  # Using sync API for simplicity

app = Flask(__name__)

@app.route('/', methods=['POST'])
def extract_id():
    website_url = request.json.get('website_url')

    if not website_url:
        return jsonify({'error': 'Website URL is required'}), 400

    browser = None
    try:
        with sync_playwright() as p:  # Ensuring Playwright's event loop is correctly managed
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Navigate to the provided website URL
            page.goto(website_url)

            # Wait for the page to load
            page.wait_for_selector('body')

            # Execute JavaScript to get the window.__NUXT__ content
            nuxt_content = page.evaluate('window.__NUXT__')

            # Convert the object to a string
            nuxt_content_str = str(nuxt_content)

            # Use regex to find all URLs starting with the specified prefixes
            import re
            regex = r'https:\/\/(?:cdn|cdn3d|cdnl|cdni)\.iconscout\.com\/[^\s"\']+'
            matches = re.findall(regex, nuxt_content_str)

            if matches and len(matches) >= 2:
                # Get the second URL
                second_url = matches[1]

                # Extract the numeric ID before the file extension
                id_match = re.search(r'(\d+)(?=\.\w+$)', second_url)
                if id_match:
                    return jsonify({'id': id_match.group(1)})

            return jsonify({'error': 'Not found'}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    finally:
        # Ensure the browser is closed only if it was initialized
        if browser:
            try:
                browser.close()
            except Exception as e:
                print(f"Error closing browser: {e}")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Bind to all network interfaces
