#!/usr/bin/env python3
"""
Graph Visualization Tool
========================

Draws the LangGraph workflow as a visual diagram.
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from langgraph_workflow_orchestrator import LangGraphWorkflowOrchestrator
except ImportError as e:
    print(f"❌ Failed to import orchestrator: {e}")
    sys.exit(1)

def draw_graph(output_path: str = None, view: bool = True, check_compile: bool = False):
    """Draw the workflow graph"""
    print("🔧 Initializing orchestrator...")
    
    try:
        orchestrator = LangGraphWorkflowOrchestrator()
        
        if check_compile:
            print("✅ Graph compiled successfully")
            return
        
        print("📊 Generating graph visualization...")
        
        # Try to use graphviz if available
        try:
            import graphviz
            from langgraph.graph.graph import draw_ascii
            
            # Generate ASCII representation
            ascii_graph = draw_ascii(orchestrator.workflow)
            print("\n" + ascii_graph)
            
            # Try to generate PNG if graphviz is available
            try:
                graph = orchestrator.workflow.get_graph()
                graphviz_graph = graphviz.Digraph()
                
                # Add nodes
                for node in graph.nodes:
                    graphviz_graph.node(node.id, label=node.id)
                
                # Add edges
                for edge in graph.edges:
                    graphviz_graph.edge(edge.source, edge.target)
                
                if output_path:
                    graphviz_graph.render(output_path, format='png', cleanup=True)
                    print(f"✅ Graph saved to: {output_path}.png")
                    
                    if view:
                        import subprocess
                        import platform
                        
                        if platform.system() == 'Darwin':  # macOS
                            subprocess.run(['open', f"{output_path}.png"])
                        elif platform.system() == 'Windows':
                            subprocess.run(['start', f"{output_path}.png"], shell=True)
                        else:  # Linux
                            subprocess.run(['xdg-open', f"{output_path}.png"])
                else:
                    print("💡 Use --output <path> to save PNG file")
                    
            except Exception as e:
                print(f"⚠️  Could not generate PNG (graphviz may not be installed): {e}")
                print("   Install with: pip install graphviz")
        
        except ImportError:
            # Fallback to ASCII only
            from langgraph.graph.graph import draw_ascii
            ascii_graph = draw_ascii(orchestrator.workflow)
            print("\n" + ascii_graph)
            print("\n💡 Install graphviz for PNG output: pip install graphviz")
        
    except Exception as e:
        print(f"❌ Error generating graph: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="Visualize the LangGraph workflow")
    parser.add_argument("--output", type=str, help="Output file path (without extension)")
    parser.add_argument("--view", action="store_true", default=True, help="Open image after generation")
    parser.add_argument("--no-view", action="store_false", dest="view", help="Don't open image")
    parser.add_argument("--check-compile", action="store_true", help="Just check if graph compiles")
    
    args = parser.parse_args()
    
    draw_graph(args.output, args.view, args.check_compile)

if __name__ == "__main__":
    main()

