import os
import json
import base64
import tempfile
from typing import List, Dict, Any
from openai import OpenAI

AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN", "default-aiproxy-token")
client = OpenAI(
    api_key=AIPROXY_TOKEN,
    base_url="https://aiproxy.sanand.workers.dev/openai/"
)

def generate_app(brief: str, attachments: List[Any], task: str, round_num: int, checks: List[str]) -> Dict[str, str]:
    attach_contents = {}
    temp_files = []
    for att in attachments or []:
        if att.url.startswith('data:'):
            header, encoded = att.url.split(',', 1)
            content = base64.b64decode(encoded).decode('utf-8')
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{att.name}") as f:
                f.write(content)
                attach_contents[att.name] = f.name
                temp_files.append(f.name)

    attachments_desc = ', '.join([f"{k}: {v}" for k, v in attach_contents.items()])
    prompt = f"""
    Task: {task} Round: {round_num}
    Brief: {brief}
    Attachments: {attachments_desc}
    Checks to pass: {', '.join(checks)}
    
    Generate a minimal single-page web app (HTML/JS/CSS) that fulfills the brief. For Round 2, update the existing app.
    Include:
    - index.html: Main page with Bootstrap 5 if needed.
    - script.js: JS logic.
    - style.css: Styles if needed.
    - README.md: Professional README (summary, setup: 'Fork repo and enable GitHub Pages', usage, code explanation, license).
    
    Output ONLY valid JSON: {{"files": {{"index.html": "content...", "script.js": "content...", "style.css": "content...", "README.md": "content..."}}}}
    Ensure code is clean, no secrets, and passes checks.
    """


    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful code generator. Always output ONLY valid JSON as specified in the user prompt. Do not add extra text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=0.1
        )
        
        generated_text = response.choices[0].message.content
        
        start_idx = generated_text.find('{"files":')
        if start_idx != -1:
            end_idx = generated_text.rfind('}') + 1
            generated_json = json.loads(generated_text[start_idx:end_idx])
        else:
            generated_json = json.loads(generated_text)
        
        files = generated_json.get('files', {})
        
        files['LICENSE'] = """MIT License

Copyright (c) 2025 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
        

        for path in temp_files:
            try:
                os.unlink(path)
            except OSError:
                pass
        
        return files
    except Exception as e:
        print(f"AIPipe generation failed: {e}")
        return {
            'index.html': f'<html><body><h1>{brief}</h1><p>Generated for {task}</p></body></html>',
            'README.md': f'# {task}\n\n{brief}\n\n## Setup\nFork this repo and enable GitHub Pages.\n\n## License\nMIT',
            'LICENSE': files['LICENSE']
        }
