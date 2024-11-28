import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tree_manager import Base, Tree, TreeNode, TreeEdge, TreeTag


class TestTreeManager(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.session = self.Session()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def test_create_tag(self):
        tree = Tree(name="Test Tree")
        self.session.add(tree)
        self.session.commit()

        node1 = TreeNode(tree_id=tree.id, data={"name": "Root"})
        node2 = TreeNode(tree_id=tree.id, data={"name": "Child"})
        self.session.add_all([node1, node2])
        self.session.commit()

        edge = TreeEdge(incoming_node_id=node1.id, outgoing_node_id=node2.id, data={"relation": "child"})
        self.session.add(edge)
        self.session.commit()

        tag = tree.create_tag(self.session, "v1.0", description="Initial version")
        self.assertEqual(tag.tag_name, "v1.0")
        self.assertIn("nodes", tag.snapshot)
        self.assertIn("edges", tag.snapshot)

    def test_restore_from_tag(self):
        tree = Tree(name="Test Tree")
        self.session.add(tree)
        self.session.commit()

        node1 = TreeNode(tree_id=tree.id, data={"name": "Root"})
        node2 = TreeNode(tree_id=tree.id, data={"name": "Child"})
        self.session.add_all([node1, node2])
        self.session.commit()

        edge = TreeEdge(incoming_node_id=node1.id, outgoing_node_id=node2.id, data={"relation": "child"})
        self.session.add(edge)

        tag = tree.create_tag(self.session, "v1.0", description="Initial version")

        node3 = TreeNode(tree_id=tree.id, data={"name": "New Node"})
        self.session.add(node3)
        self.session.commit()

        edge = TreeEdge(incoming_node_id=node1.id, outgoing_node_id=node3.id, data={"relation": "child"})
        self.session.add(edge)
        self.session.commit()

        restored_tree = tree.restore_from_tag(self.session, "v1.0")
        self.assertEqual(len(restored_tree.nodes), 2)  
        self.assertEqual(len(restored_tree.nodes[0].incoming_edges), 1)

    def test_add_node(self):
        tree = Tree(name="Test Tree")
        self.session.add(tree)
        self.session.commit()

        node = tree.add_node(self.session, data={"name": "New Node"})
        self.assertEqual(node.data["name"], "New Node")
        self.assertEqual(len(tree.nodes), 1)

    def test_add_edge(self):
        tree = Tree(name="Test Tree")
        self.session.add(tree)
        self.session.commit()

        node1 = tree.add_node(self.session, data={"name": "Node 1"})
        node2 = tree.add_node(self.session, data={"name": "Node 2"})

        edge = tree.add_edge(
            session=self.session,
            incoming_node_id=node1.id,
            outgoing_node_id=node2.id,
            data={"relation": "child"}
        )
        self.assertEqual(edge.data["relation"], "child")
        self.assertEqual(len(node1.incoming_edges), 1)
        self.assertEqual(len(node2.outgoing_edges), 1)

    def test_get_root_nodes(self):
        tree = Tree(name="Test Tree")
        self.session.add(tree)
        self.session.commit()

        node1 = tree.add_node(self.session, data={"name": "Root"})
        node2 = tree.add_node(self.session, data={"name": "Child"})
        node3 = tree.add_node(self.session, data={"name": "Child"})
        tree.add_edge(self.session, incoming_node_id=node1.id, outgoing_node_id=node2.id)
        tree.add_edge(self.session, incoming_node_id=node2.id, outgoing_node_id=node3.id)

        roots = tree.get_root_nodes(self.session)
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0].data["name"], "Root")

    def test_find_path(self):
        tree = Tree(name="Test Tree")
        self.session.add(tree)
        self.session.commit()

        node1 = tree.add_node(self.session, data={"name": "Node 1"})
        node2 = tree.add_node(self.session, data={"name": "Node 2"})
        node3 = tree.add_node(self.session, data={"name": "Node 3"})
        node4 = tree.add_node(self.session, data={"name": "Node 4"})
        node5 = tree.add_node(self.session, data={"name": "Node 5"})

        tree.add_edge(self.session, incoming_node_id=node1.id, outgoing_node_id=node2.id)
        tree.add_edge(self.session, incoming_node_id=node2.id, outgoing_node_id=node3.id)
        tree.add_edge(self.session, incoming_node_id=node2.id, outgoing_node_id=node4.id)
        tree.add_edge(self.session, incoming_node_id=node4.id, outgoing_node_id=node5.id)

        path = tree.find_path(self.session, start_node_id=node5.id, end_node_id=node1.id)
        self.assertEqual(len(path), 4)
        self.assertEqual(path[0][0].data["name"], "Node 5")
        self.assertEqual(path[1][0].data["name"], "Node 4")
        self.assertEqual(path[2][0].data["name"], "Node 2")
        self.assertEqual(path[3][0].data["name"], "Node 1")

if __name__ == "__main__":
    unittest.main()
