import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Automate worker prompt assembly for Local LLM delegation in sdd-orchestrator.")
    parser.add_argument("--persona", required=False, help="Path to worker persona markdown file")
    parser.add_argument("--instruction", required=True, help="Path to task instruction / specification file (.md or .yaml)")
    parser.add_argument("--rules", required=False, help="Path to additional framework rules or guidelines")
    parser.add_argument("--target", required=False, help="Path to target source file to modify (reads content)")
    parser.add_argument("--out", required=True, help="Path to save the generated output prompt file")

    args = parser.parse_args()

    sections = []

    # 1. Persona
    if args.persona:
        if os.path.exists(args.persona):
            with open(args.persona, 'r', encoding='utf-8') as f:
                sections.append(f"# WORKER ROLE & PERSONA\n\n{f.read().strip()}")
        else:
            print(f"Warning: Persona file not found: {args.persona}", file=sys.stderr)

    # 2. Rules
    if args.rules:
        if os.path.exists(args.rules):
            with open(args.rules, 'r', encoding='utf-8') as f:
                sections.append(f"# MANDATORY RULES & BEST PRACTICES\n\n{f.read().strip()}")
        else:
            print(f"Warning: Rules file not found: {args.rules}", file=sys.stderr)

    # 3. Instruction
    if os.path.exists(args.instruction):
        with open(args.instruction, 'r', encoding='utf-8') as f:
            sections.append(f"# TASK SPECIFICATION & INSTRUCTION\n\n{f.read().strip()}")
    else:
        print(f"Error: Instruction file not found: {args.instruction}", file=sys.stderr)
        sys.exit(1)

    # 4. Target file content if editing
    if args.target:
        if os.path.exists(args.target):
            with open(args.target, 'r', encoding='utf-8') as f:
                sections.append(f"# EXISTING SOURCE FILE TO MODIFY ({args.target})\n\n```text\n{f.read().strip()}\n```")
        else:
            sections.append(f"# TARGET FILE TO CREATE\n\nCreate new file at: `{args.target}`")

    # Combine into single Markdown prompt
    composed_prompt = "\n\n---\n\n".join(sections)

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8', newline='\n') as f:
        f.write(composed_prompt)

    print(f"✅ Successfully assembled worker prompt to {args.out}")

if __name__ == '__main__':
    main()
