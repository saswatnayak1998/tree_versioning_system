# Tree Manager

A Python library to manage hierarchical tree structures in SQL databases.

### Installation

```bash
https://github.com/saswatnayak1998/tree_versioning_system.git
cd tree_manager
pip install -e .
```

### Run tests

```bash
python tests/test_tree_manager.py
```

### Database Implementation

## Models

### Tree

- **Attributes**:
  - `id`: Unique identifier for the tree.
  - `name`: Name of the tree.
  - `description`: A brief description of the tree.
  - `root_node_id`: Reference to the root node of the tree.
  - `created_at`: Timestamp of when the tree was created.
  - `updated_at`: Timestamp of the last update to the tree.
- **Relationships**: Has many `TreeNode` and `TreeTag` instances.

### TreeNode

- **Attributes**:
  - `id`: Unique identifier for the node.
  - `tree_id`: Reference to the associated tree.
  - `parent_id`: Reference to the parent node (if any).
  - `name`: Name of the node.
  - `data`: Additional data associated with the node.
  - `created_at`: Timestamp of when the node was created.
  - `updated_at`: Timestamp of the last update to the node.
- **Relationships**: Has many `TreeEdge` instances and may have a parent and many child `TreeNode` instances.

### TreeEdge

- **Attributes**:
  - `id`: Unique identifier for the edge.
  - `source_node_id`: Reference to the source node.
  - `target_node_id`: Reference to the target node.
  - `weight`: Optional weight for the edge.
  - `created_at`: Timestamp of when the edge was created.
- **Relationships**: Connects two `TreeNode` instances.

### TreeTag

- **Attributes**:
  - `id`: Unique identifier for the tag.
  - `tree_id`: Reference to the associated tree.
  - `name`: Name of the tag.
  - `snapshot`: JSON representation of the tree's state at the time of tagging.
  - `created_at`: Timestamp of when the tag was created.
- **Relationships**: Belongs to a `Tree`.
