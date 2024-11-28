from tree_manager import Tree, TreeNode, TreeEdge, init_db, SessionLocal

def populate_database():
    # Initialize the database
    init_db()
    session = SessionLocal()

    try:
        # Create multiple trees
        tree1 = Tree(name="Configuration Tree 1")
        tree2 = Tree(name="Configuration Tree 2")
        session.add_all([tree1, tree2])
        session.commit()

        # Add nodes to Tree 1
        node1_t1 = TreeNode(tree_id=tree1.id, data={"name": "Root Node", "setting": "default"})
        node2_t1 = TreeNode(tree_id=tree1.id, data={"name": "Child Node 1", "setting": "custom"})
        node3_t1 = TreeNode(tree_id=tree1.id, data={"name": "Child Node 2", "setting": "custom"})
        node4_t1 = TreeNode(tree_id=tree1.id, data={"name": "Grandchild Node 1", "setting": "custom"})
        node5_t1 = TreeNode(tree_id=tree1.id, data={"name": "Grandchild Node 2", "setting": "experimental"})
        node6_t1 = TreeNode(tree_id=tree1.id, data={"name": "Child Node 3", "setting": "test"})

        session.add_all([node1_t1, node2_t1, node3_t1, node4_t1, node5_t1, node6_t1])
        session.commit()

        # Add edges to Tree 1
        edge1_t1 = TreeEdge(
            incoming_node_id=node1_t1.id, outgoing_node_id=node2_t1.id, data={"relation": "child"}
        )
        edge2_t1 = TreeEdge(
            incoming_node_id=node1_t1.id, outgoing_node_id=node3_t1.id, data={"relation": "child"}
        )
        edge3_t1 = TreeEdge(
            incoming_node_id=node2_t1.id, outgoing_node_id=node4_t1.id, data={"relation": "grandchild"}
        )
        edge4_t1 = TreeEdge(
            incoming_node_id=node2_t1.id, outgoing_node_id=node5_t1.id, data={"relation": "grandchild"}
        )
        edge5_t1 = TreeEdge(
            incoming_node_id=node1_t1.id, outgoing_node_id=node6_t1.id, data={"relation": "child"}
        )
        session.add_all([edge1_t1, edge2_t1, edge3_t1, edge4_t1, edge5_t1])
        session.commit()

        # Add nodes to Tree 2
        node1_t2 = TreeNode(tree_id=tree2.id, data={"name": "Root Node", "status": "active"})
        node2_t2 = TreeNode(tree_id=tree2.id, data={"name": "Child Node A", "status": "pending"})
        node3_t2 = TreeNode(tree_id=tree2.id, data={"name": "Child Node B", "status": "inactive"})
        node4_t2 = TreeNode(tree_id=tree2.id, data={"name": "Grandchild Node", "status": "active"})
        node5_t2 = TreeNode(tree_id=tree2.id, data={"name": "Child Node C", "status": "experimental"})
        node6_t2 = TreeNode(tree_id=tree2.id, data={"name": "Child Node D", "status": "test"})
        node7_t2 = TreeNode(tree_id=tree2.id, data={"name": "Great Grandchild Node", "status": "active"})

        session.add_all([node1_t2, node2_t2, node3_t2, node4_t2, node5_t2, node6_t2, node7_t2])
        session.commit()

        # Add edges to Tree 2
        edge1_t2 = TreeEdge(
            incoming_node_id=node1_t2.id, outgoing_node_id=node2_t2.id, data={"relation": "child"}
        )
        edge2_t2 = TreeEdge(
            incoming_node_id=node1_t2.id, outgoing_node_id=node3_t2.id, data={"relation": "child"}
        )
        edge3_t2 = TreeEdge(
            incoming_node_id=node2_t2.id, outgoing_node_id=node4_t2.id, data={"relation": "grandchild"}
        )
        edge4_t2 = TreeEdge(
            incoming_node_id=node1_t2.id, outgoing_node_id=node5_t2.id, data={"relation": "child"}
        )
        edge5_t2 = TreeEdge(
            incoming_node_id=node1_t2.id, outgoing_node_id=node6_t2.id, data={"relation": "child"}
        )
        edge6_t2 = TreeEdge(
            incoming_node_id=node4_t2.id, outgoing_node_id=node7_t2.id, data={"relation": "great-grandchild"}
        )
        session.add_all([edge1_t2, edge2_t2, edge3_t2, edge4_t2, edge5_t2, edge6_t2])
        session.commit()

        print("Database populated successfully with more nodes and relations.")

    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    populate_database()
