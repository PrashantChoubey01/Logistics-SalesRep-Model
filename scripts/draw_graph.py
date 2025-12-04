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
        
        # Get the graph structure
        graph = orchestrator.workflow.get_graph()
        print(f"📊 Graph structure: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        
        # Print ASCII representation
        print("\n" + "=" * 80)
        print("📋 WORKFLOW NODES")
        print("=" * 80)
        for i, node in enumerate(graph.nodes, 1):
            node_id = node.id if hasattr(node, 'id') else str(node)
            print(f"  {i:2d}. {node_id}")
        
        print("\n" + "=" * 80)
        print("🔗 WORKFLOW EDGES")
        print("=" * 80)
        for i, edge in enumerate(graph.edges, 1):
            source = edge.source if hasattr(edge, 'source') else edge[0]
            target = edge.target if hasattr(edge, 'target') else edge[1]
            print(f"  {i:2d}. {source} → {target}")
        
        # Try to use graphviz for PNG visualization
        try:
            import graphviz
            
            graphviz_graph = graphviz.Digraph(
                name='LangGraph Workflow',
                format='png',
                graph_attr={'rankdir': 'LR', 'size': '12,8', 'dpi': '300'},
                node_attr={'shape': 'box', 'style': 'rounded,filled', 'fillcolor': 'lightblue'}
            )
                
                # Add nodes
                for node in graph.nodes:
                node_id = node.id if hasattr(node, 'id') else str(node)
                graphviz_graph.node(node_id, label=node_id.replace('_', '\n'))
                
                # Add edges
                for edge in graph.edges:
                source = edge.source if hasattr(edge, 'source') else edge[0]
                target = edge.target if hasattr(edge, 'target') else edge[1]
                graphviz_graph.edge(source, target)
                
                if output_path:
                output_file = graphviz_graph.render(output_path, format='png', cleanup=True)
                print(f"\n✅ Graph saved to: {output_file}")
                    
                    if view:
                        import subprocess
                        import platform
                        
                        if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', output_file])
                        elif platform.system() == 'Windows':
                        subprocess.run(['start', output_file], shell=True)
                        else:  # Linux
                        subprocess.run(['xdg-open', output_file])
                else:
                # Save to default location
                default_path = "workflow_graph"
                output_file = graphviz_graph.render(default_path, format='png', cleanup=True)
                print(f"\n✅ Graph saved to: {output_file}")
                print("💡 Use --output <path> to specify custom output path")
                
                if view:
                    import subprocess
                    import platform
                    
                    if platform.system() == 'Darwin':  # macOS
                        subprocess.run(['open', output_file])
                    elif platform.system() == 'Windows':
                        subprocess.run(['start', output_file], shell=True)
                    else:  # Linux
                        subprocess.run(['xdg-open', output_file])
        
        except ImportError:
            print("\n⚠️  graphviz not installed - cannot generate PNG")
            print("   Install with: pip install graphviz")
            print("   Also install system package: brew install graphviz (macOS) or apt-get install graphviz (Linux)")
        except Exception as e:
            print(f"\n⚠️  Could not generate PNG: {e}")
            print("   Make sure graphviz is installed: pip install graphviz")
            print("   And system package: brew install graphviz (macOS)")
        
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

