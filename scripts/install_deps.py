import os
import subprocess
import sys
from pathlib import Path

def print_step(message):
    print(f"\n🚀 {message}")

def print_success(message):
    print(f"✅ {message}")

def print_warning(message):
    print(f"⚠️  {message}")

def install_frontend_design_skill():
    # Detect .agents/skills directory relative to where the script is run
    # Assuming script is run from project root, or we can find it
    current_dir = Path.cwd()
    skills_dir = current_dir / ".agents" / "skills"
    
    if not skills_dir.exists():
        skills_dir.mkdir(parents=True, exist_ok=True)
        print_step(f"Created {skills_dir}")

    target_dir = skills_dir / "frontend-design"
    
    if target_dir.exists():
        print_success("Skill 'frontend-design' is already installed.")
        return

    print_step("Installing dependent skill 'frontend-design'...")
    
    # Try to clone from GitHub
    repo_url = "https://github.com/anthropics/skills-frontend-design.git"
    
    try:
        subprocess.run(["git", "clone", repo_url, str(target_dir)], check=True, capture_output=True)
        print_success("Successfully cloned 'frontend-design' from GitHub.")
    except subprocess.CalledProcessError:
        print_warning("Could not clone repository. Creating a fallback SKILL.md for frontend-design.")
        
        # Fallback: Create the skill manually if repo doesn't exist
        target_dir.mkdir(parents=True, exist_ok=True)
        skill_md_path = target_dir / "SKILL.md"
        
        fallback_content = """---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications. Generates creative, polished code and UI design that avoids generic AI aesthetics.
---

# Frontend Design Skill

You are a premium UI/UX frontend designer. Your goal is to produce stunning, non-generic, high-quality user interfaces.
When invoked, you must:
1. Propose BOLD and unconventional aesthetic choices.
2. Rely heavily on Tailwind CSS for layout, colors, and micro-animations.
3. Ensure the design feels premium (glassmorphism, subtle shadows, perfect typography).
"""
        with open(skill_md_path, "w", encoding="utf-8") as f:
            f.write(fallback_content)
            
        print_success("Fallback 'frontend-design' skill successfully generated.")

if __name__ == "__main__":
    print_step("Starting dependency installation for SDD Orchestrator...")
    install_frontend_design_skill()
    print_step("Installation complete!")
