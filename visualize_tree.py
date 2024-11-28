import networkx as nx
import matplotlib.pyplot as plt
import sys
from tree_manager import Tree, TreeNode, TreeEdge, init_db, SessionLocal

def visualize_tree_by_id(session, tree_id):
    try:
        tree = session.query(Tree).filter_by(id=tree_id).first()
        if not tree:
            print(f"No tree found with ID: {tree_id}.")
            return
        
        print(f"Visualizing Tree ID: {tree.id}, Name: {tree.name}")
        
        G = nx.DiGraph()
        
        nodes = session.query(TreeNode).filter_by(tree_id=tree.id).all()
        for node in nodes:
            G.add_node(node.id, label=node.data.get("name", f"Node {node.id}"))
        
        edges = session.query(TreeEdge).join(TreeNode, TreeEdge.incoming_node_id == TreeNode.id).filter(TreeNode.tree_id == tree.id).all()
        for edge in edges:
            G.add_edge(
                edge.incoming_node_id,
                edge.outgoing_node_id,
                label=edge.data.get("relation", "Edge")
            )
        
        node_labels = {node: data["label"] for node, data in G.nodes(data=True)}
        edge_labels = {(u, v): data["label"] for u, v, data in G.edges(data=True)}

        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G) 
        nx.draw(G, pos, with_labels=True, labels=node_labels, node_size=3000, node_color="skyblue", font_size=10)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=9)
        plt.title(f"Visualization of Tree ID {tree.id}: {tree.name}")
        plt.show()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python visualize.py <tree_id>")
        sys.exit(1)

    tree_id = int(sys.argv[1])
    init_db()
    session = SessionLocal()

    visualize_tree_by_id(session, tree_id=tree_id)
