import os
import sys
import json
import urllib.request
import urllib.parse
import argparse

try:
    import tiktoken
    _TIKTOKEN_AVAILABLE = True
except ImportError:
    _TIKTOKEN_AVAILABLE = False

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

def detect_provider():
    """Detect if LM Studio (port 1234) or Ollama (port 11434) is currently running."""
    # Check LM Studio first
    try:
        req = urllib.request.Request("http://localhost:1234/v1/models", headers={"User-Agent": "SDD-Orchestrator"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                return "lmstudio", "http://localhost:1234/v1/chat/completions"
    except Exception:
        pass

    # Check Ollama
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags", headers={"User-Agent": "SDD-Orchestrator"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                return "ollama", "http://localhost:11434/api/generate"
    except Exception:
        pass

    return None, None

def _count_and_report_tokens(final_prompt: str, rules_text: str, prompt_text: str, encoding_name: str) -> None:
    """Print token counts for the composed prompt using tiktoken."""
    if not _TIKTOKEN_AVAILABLE:
        print("⚠️  tiktoken is not installed. Run: pip install tiktoken", file=sys.stderr)
        return

    try:
        enc = tiktoken.get_encoding(encoding_name)
    except Exception as e:
        print(f"⚠️  Unknown tiktoken encoding '{encoding_name}': {e}", file=sys.stderr)
        return

    def count(text: str) -> int:
        return len(enc.encode(text))

    total = count(final_prompt)
    lines = [
        f"📊 Token count  (encoding: {encoding_name})",
        "─" * 44,
    ]
    if rules_text:
        lines.append(f"  rules   : {count(rules_text):>8,} tokens")
    lines.append(    f"  prompt  : {count(prompt_text):>8,} tokens")
    if rules_text:
        lines.append(f"  separator: {'2':>7} tokens")
    lines.append(    "─" * 44)
    lines.append(    f"  TOTAL   : {total:>8,} tokens")
    print("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Query local LLM (LM Studio / Ollama) and save output to a clean UTF-8 file.")
    parser.add_argument("--model", required=False, default="local-model", help="Model name (e.g. qwen2.5-coder:7b or local-model for LM Studio)")
    parser.add_argument("--prompt", required=True, help="Path to the prompt markdown file")
    parser.add_argument("--rules", required=False, help="Path to the framework rules file to prepend to the prompt")
    parser.add_argument("--out", required=True, help="Path to save the generated output (UTF-8)")
    parser.add_argument("--provider", choices=["auto", "lmstudio", "ollama"], default="auto", help="Local LLM provider (default: auto)")
    parser.add_argument("--url", required=False, help="Custom endpoint URL override")
    parser.add_argument("--count-tokens", action="store_true", help="Count tokens in the composed prompt via tiktoken and exit (no LLM request)")
    parser.add_argument("--token-encoding", default="cl100k_base", help="tiktoken encoding to use (default: cl100k_base)")

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

    if args.count_tokens:
        _count_and_report_tokens(final_prompt, rules_text, prompt_text, args.token_encoding)
        sys.exit(0)
        
    provider = args.provider
    target_url = args.url

    if provider == "auto" and not target_url:
        detected_prov, detected_url = detect_provider()
        if not detected_prov:
            notify_error("Neither LM Studio (port 1234) nor Ollama (port 11434) is responding. Please start your local LLM server.")
            sys.exit(1)
        provider = detected_prov
        target_url = detected_url
        print(f"Auto-detected local LLM provider: {provider.upper()} ({target_url})")
    elif not target_url:
        if provider == "lmstudio":
            target_url = "http://localhost:1234/v1/chat/completions"
        else:
            target_url = "http://localhost:11434/api/generate"

    headers = {
        "Content-Type": "application/json"
    }

    if provider == "lmstudio":
        messages = []
        if rules_text:
            messages.append({"role": "system", "content": rules_text})
            messages.append({"role": "user", "content": prompt_text})
        else:
            messages.append({"role": "user", "content": final_prompt})

        payload = {
            "model": args.model,
            "messages": messages,
            "temperature": 0.2,
            "stream": False
        }
    else:
        # Ollama payload format
        payload = {
            "model": args.model if args.model != "local-model" else "qwen2.5-coder:7b",
            "prompt": final_prompt,
            "stream": False
        }

    data = json.dumps(payload).encode('utf-8')
    
    print(f"Sending prompt to {provider.upper()} (model: {payload['model']})...")
    try:
        req = urllib.request.Request(target_url, data=data, headers=headers)
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                result = json.loads(response.read().decode('utf-8'))
                if provider == "lmstudio":
                    generated_text = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                else:
                    generated_text = result.get('response', '')
                
                with open(args.out, 'w', encoding='utf-8', newline='\n') as out_f:
                    out_f.write(generated_text)
                    
                print(f"Successfully generated response and saved to {args.out} (UTF-8)")
            else:
                notify_error(f"{provider.upper()} returned unexpected status: {response.status}")
                sys.exit(1)
    except Exception as e:
        notify_error(f"Failed to communicate with {provider.upper()}: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
