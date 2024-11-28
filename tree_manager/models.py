from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    JSON,
    TIMESTAMP,
    func,
)
import json
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.schema import UniqueConstraint


Base = declarative_base()


class Tree(Base):
    __tablename__ = "tree"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())

    nodes = relationship("TreeNode", back_populates="tree", cascade="all, delete-orphan")
    tags = relationship("TreeTag", back_populates="tree", cascade="all, delete-orphan")

    @classmethod
    def get(cls, session, id):
        return session.query(cls).filter_by(id=id).first()
    
    def get_by_tag(self, session, tag_name):
        tag = session.query(TreeTag).filter_by(tag_name=tag_name).first()
        return tag.tree if tag else None

    def create_tag(self, session, tag_name, description=None):
        try:
            existing_tag = session.query(TreeTag).filter_by(tree_id=self.id, tag_name=tag_name).first()
            if existing_tag:
                print(f"Tag '{tag_name}' already exists for this tree with description: '{existing_tag.description}'")
                return f"Tag '{tag_name}' already exists for this tree with description: '{existing_tag.description}'"

            nodes = session.query(TreeNode).filter_by(tree_id=self.id).all()
            edges = session.query(TreeEdge).filter(
                TreeEdge.incoming_node_id.in_([node.id for node in nodes])
            ).all()

            snapshot = {
                "nodes": [{"id": node.id, "data": node.data} for node in nodes],
                "edges": [
                    {
                        "incoming_node_id": edge.incoming_node_id,
                        "outgoing_node_id": edge.outgoing_node_id,
                        "data": edge.data,
                    }
                    for edge in edges
                ],
            }

            tag = TreeTag(
                tree_id=self.id,
                tag_name=tag_name,
                description=description,
                snapshot=json.dumps(snapshot),  # Serialize snapshot to JSON
            )
            session.add(tag)
            session.commit()
            return tag

        except Exception as e:
            session.rollback()
            raise ValueError(f"Failed to create tag '{tag_name}': {e}")


    def create_new_tree_version_from_tag(self, session, tag_name):
        tag = session.query(TreeTag).filter_by(tree_id=self.id, tag_name=tag_name).first()
        if not tag:
            return f"Tag '{tag_name}' does not exist."

        new_tree = Tree(name=f"{self.name}_{tag_name}_branch")
        session.add(new_tree)
        session.commit()

        node_mapping = {}
        for old_node in self.nodes:
            new_node = TreeNode(tree_id=new_tree.id, data=old_node.data)
            session.add(new_node)
            session.commit()  
            node_mapping[old_node.id] = new_node.id

        for old_node in self.nodes:
            edges = session.query(TreeEdge).filter_by(incoming_node_id=old_node.id).all()
            for old_edge in edges:
                new_edge = TreeEdge(
                    incoming_node_id=node_mapping[old_edge.incoming_node_id],
                    outgoing_node_id=node_mapping[old_edge.outgoing_node_id],
                    data=old_edge.data,
                )
                session.add(new_edge)

        session.commit()
        return new_tree

    def restore_from_tag(self, session, tag_name):
        tag = session.query(TreeTag).filter_by(tree_id=self.id, tag_name=tag_name).first()
        if not tag:
            raise ValueError(f"Tag '{tag_name}' does not exist for this tree.")

        snapshot = json.loads(tag.snapshot)

        restored_tree = Tree(name=f"{self.name}_rollback_to_{tag_name}")
        session.add(restored_tree)
        session.commit()

        node_mapping = {}
        for node_data in snapshot["nodes"]:
            new_node = TreeNode(tree_id=restored_tree.id, data=node_data["data"])
            session.add(new_node)
            session.commit()
            node_mapping[node_data["id"]] = new_node.id

        for edge_data in snapshot["edges"]:
            new_edge = TreeEdge(
                incoming_node_id=node_mapping[edge_data["incoming_node_id"]],
                outgoing_node_id=node_mapping[edge_data["outgoing_node_id"]],
                data=edge_data["data"],
            )
            session.add(new_edge)

        session.commit()
        return restored_tree

    def add_node(self, session, data):
        new_node = TreeNode(tree_id=self.id, data=data)
        session.add(new_node)
        session.commit()
        return new_node

    def add_edge(self, session, incoming_node_id, outgoing_node_id, data=None):
        incoming_node = session.query(TreeNode).get(incoming_node_id)
        outgoing_node = session.query(TreeNode).get(outgoing_node_id)

        if not incoming_node or not outgoing_node:
            raise ValueError(f"One or both node IDs are invalid: {incoming_node_id}, {outgoing_node_id}")

        edge = TreeEdge(
            incoming_node_id=incoming_node_id,
            outgoing_node_id=outgoing_node_id,
            data=data or {}
        )
        session.add(edge)
        session.commit()
        return edge


    def get_root_nodes(self, session):
        return [node for node in self.nodes if not node.has_incoming_edges(session)]

    def get_node(self, session, node_id):
        return session.query(TreeNode).filter_by(id=node_id).first()

    def get_child_nodes(self, session, node_id):
        edges = session.query(TreeEdge).filter_by(incoming_node_id=node_id).all()
        return [edge.outgoing_node for edge in edges]

    def get_parent_nodes(self, session, node_id):
        edges = session.query(TreeEdge).filter_by(outgoing_node_id=node_id).all()
        return [edge.incoming_node for edge in edges]

    def get_node_edges(self, session, node_id):
        return session.query(TreeEdge).filter(
            (TreeEdge.incoming_node_id == node_id) | (TreeEdge.outgoing_node_id == node_id)
        ).all()

    def traverse_tree(self, session, start_node_id):
        """
        Traverse the tree starting from a given node and gather information about 
        all connected nodes and edges.

        Args:
            session: SQLAlchemy session to interact with the database.
            start_node_id: The ID of the starting node for traversal.

        Returns:
            dict: A dictionary containing information about the nodes and edges.
        """
        def traverse(node_id, visited):
            if node_id in visited:
                return  
            visited.add(node_id)
            
            node = session.query(TreeNode).filter_by(id=node_id).first()
            if not node:
                return
            
            node_info = {"id": node.id, "data": node.data, "edges": []}
            result["nodes"].append(node_info)

            outgoing_edges = session.query(TreeEdge).filter_by(incoming_node_id=node_id).all()
            for edge in outgoing_edges:
                edge_info = {
                    "incoming_node_id": edge.incoming_node_id,
                    "outgoing_node_id": edge.outgoing_node_id,
                    "data": edge.data,
                }
                node_info["edges"].append(edge_info)
                result["edges"].append(edge_info)

                traverse(edge.outgoing_node_id, visited)

        result = {"nodes": [], "edges": []}
        visited = set()  

        traverse(start_node_id, visited)
        return result

    def start_traversal(self, session):
        
        self.traverse_tree(session, rood_id = 1)

    def get_nodes_at_depth(self, session, depth):
        def traverse(node, current_depth):
            if current_depth == depth:
                return [node]
            child_nodes = self.get_child_nodes(session, node.id)
            nodes = []
            for child in child_nodes:
                nodes.extend(traverse(child, current_depth + 1))
            return nodes

        root_nodes = self.get_root_nodes(session)
        result = []
        for root in root_nodes:
            result.extend(traverse(root, 0))
        return result

    def find_path(self, session, start_node_id, end_node_id):
        visited = set()
        path = []

        def dfs(current_node_id, target_id, current_path):
            if current_node_id in visited:
                return False
            visited.add(current_node_id)
            node = self.get_node(session, current_node_id)
            if current_node_id == target_id:
                current_path.append((node, None))
                path.extend(current_path)
                return True
            edges = self.get_node_edges(session, current_node_id)
            for edge in edges:
                next_node_id = edge.outgoing_node_id if edge.incoming_node_id == current_node_id else edge.incoming_node_id
                if dfs(next_node_id, target_id, current_path + [(node, edge)]):
                    return True
            return False

        dfs(start_node_id, end_node_id, [])
        return path


class TreeTag(Base):
    __tablename__ = "tree_tag"

    id = Column(Integer, primary_key=True)
    tree_id = Column(Integer, ForeignKey("tree.id"), nullable=False)
    tag_name = Column(String, nullable=False)
    description = Column(String)
    snapshot = Column(JSON, nullable=False)  # Store the tree state as JSON
    created_at = Column(TIMESTAMP, default=func.current_timestamp())

    tree = relationship("Tree", back_populates="tags")

    __table_args__ = (UniqueConstraint("tree_id", "tag_name", name="unique_tree_tag_per_tree"),)

class TreeNode(Base):
    __tablename__ = "tree_node"

    id = Column(Integer, primary_key=True)
    tree_id = Column(Integer, ForeignKey("tree.id"), nullable=False)
    data = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())

    tree = relationship("Tree", back_populates="nodes")
    incoming_edges = relationship(
        "TreeEdge", foreign_keys="[TreeEdge.incoming_node_id]", back_populates="incoming_node"
    )
    outgoing_edges = relationship(
        "TreeEdge", foreign_keys="[TreeEdge.outgoing_node_id]", back_populates="outgoing_node"
    )

    def has_incoming_edges(self, session):
        return session.query(TreeEdge).filter_by(outgoing_node_id=self.id).first() is not None


class TreeEdge(Base):
    __tablename__ = "tree_edge"

    id = Column(Integer, primary_key=True)
    incoming_node_id = Column(Integer, ForeignKey("tree_node.id"), nullable=False)
    outgoing_node_id = Column(Integer, ForeignKey("tree_node.id"), nullable=False)
    data = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())

    incoming_node = relationship("TreeNode", foreign_keys=[incoming_node_id])
    outgoing_node = relationship("TreeNode", foreign_keys=[outgoing_node_id])
