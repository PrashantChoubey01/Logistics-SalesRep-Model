#!/usr/bin/env python3
"""
Repository Map Generator
========================

Generates a clickable markdown tree that collapses agents, prompts, tests into one view.
"""

import os
from pathlib import Path
from typing import List, Dict

def get_file_tree(root_dir: Path, max_depth: int = 3, exclude_dirs: set = None) -> List[str]:
    """Generate markdown tree structure"""
    if exclude_dirs is None:
        exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '.venv', 'venv'}
    
    lines = []
    indent = "  "
    
    def walk_dir(path: Path, depth: int, prefix: str = ""):
        if depth > max_depth:
            return
        
        if path.name.startswith('.') and path.name not in {'.cursor'}:
            return
        
        if path.is_dir() and path.name in exclude_dirs:
            return
        
        # Get items sorted: directories first, then files
        try:
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        except PermissionError:
            return
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            current_prefix = "└── " if is_last else "├── "
            next_prefix = indent + ("    " if is_last else "│   ")
            
            if item.is_dir():
                lines.append(f"{prefix}{current_prefix}{item.name}/")
                walk_dir(item, depth + 1, prefix + next_prefix)
            else:
                # Only show important file types
                if item.suffix in {'.py', '.md', '.json', '.yaml', '.yml', '.txt', '.sh'}:
                    lines.append(f"{prefix}{current_prefix}{item.name}")
    
    lines.append("# Repository Map")
    lines.append("")
    lines.append("> Generated automatically - click to navigate")
    lines.append("")
    lines.append("```")
    lines.append("logistic-ai-response-model/")
    walk_dir(root_dir, 0, "")
    lines.append("```")
    lines.append("")
    
    # Add agent summary
    agents_dir = root_dir / "agents"
    if agents_dir.exists():
        lines.append("## Agents Summary")
        lines.append("")
        agent_files = sorted([f.stem for f in agents_dir.glob("*.py") if not f.name.startswith("__")])
        lines.append(f"**Total Agents**: {len(agent_files)}")
        lines.append("")
        for agent in agent_files:
            lines.append(f"- `{agent}`")
        lines.append("")
    
    # Add key files
    lines.append("## Key Files")
    lines.append("")
    key_files = [
        ("langgraph_workflow_orchestrator.py", "Main workflow graph"),
        ("models/schemas.py", "Data models and schemas"),
        ("config/settings.py", "Configuration and secrets"),
        ("CUSTOMER_EMAIL_INPUT_OUTPUT_SPEC.md", "Email specification"),
        ("AGENT_AUDIT_REPORT.md", "Agent compliance audit"),
    ]
    
    for file_path, description in key_files:
        full_path = root_dir / file_path
        if full_path.exists():
            lines.append(f"- **[{file_path}]({file_path})** - {description}")
        else:
            lines.append(f"- **{file_path}** - {description} (not found)")
    lines.append("")
    
    return lines

def main():
    """Generate repository map"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    print(f"Generating repository map for: {root_dir}")
    
    lines = get_file_tree(root_dir)
    
    output_file = root_dir / "repo_map.md"
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print(f"✅ Repository map generated: {output_file}")
    print(f"   Open with: code {output_file}")

if __name__ == "__main__":
    main()

