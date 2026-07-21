import os
import sys
import json
import urllib.request
import urllib.parse
import argparse

# Allow importing notify_telegram from the same directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    import notify_telegram
except ImportError:
    notify_telegram = None

def notify_error(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    if notify_telegram:
        notify_telegram.send_message(f"🚨 **QA-Agent Error**\n\n```text\n{msg}\n```")

def main():
    parser = argparse.ArgumentParser(description="Query local Ollama model and save output to a clean UTF-8 file.")
    parser.add_argument("--model", required=True, help="Ollama model name (e.g. deepseek-coder:6.7b)")
    parser.add_argument("--prompt", required=True, help="Path to the prompt markdown file")
    parser.add_argument("--rules", required=False, help="Path to the framework rules file to prepend to the prompt")
    parser.add_argument("--out", required=True, help="Path to save the generated output (UTF-8)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.prompt):
        notify_error(f"Prompt file not found: {args.prompt}")
        sys.exit(1)
        
    try:
        with open(args.prompt, 'r', encoding='utf-8') as f:
            prompt_text = f.read()
    except Exception as e:
        notify_error(f"Failed to read prompt file (ensure it's UTF-8): {e}")
        sys.exit(1)
        
    rules_text = ""
    if args.rules:
        if not os.path.exists(args.rules):
            notify_error(f"Rules file not found: {args.rules}")
            sys.exit(1)
        try:
            with open(args.rules, 'r', encoding='utf-8') as f:
                rules_text = f.read()
        except Exception as e:
            notify_error(f"Failed to read rules file (ensure it's UTF-8): {e}")
            sys.exit(1)
            
    final_prompt = f"{rules_text}\n\n{prompt_text}" if rules_text else prompt_text
        
    url = "http://localhost:11434/api/generate"
    data = json.dumps({
        "model": args.model,
        "prompt": final_prompt,
        "stream": False
    }).encode('utf-8')
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"Sending prompt to Ollama (model: {args.model}). This may take a while depending on the model size...")
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        # Timeout is not explicitly set, allowing the model as much time as it needs to generate.
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                generated_text = result.get('response', '')
                
                with open(args.out, 'w', encoding='utf-8', newline='\n') as out_f:
                    out_f.write(generated_text)
                    
                print(f"Successfully generated response and saved to {args.out} (UTF-8)")
            else:
                notify_error(f"Ollama returned unexpected status: {response.status}")
                sys.exit(1)
    except Exception as e:
        notify_error(f"Failed to communicate with Ollama: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
