"""Compatibility alias for the stored-position search/alignment/pick runtime."""

from .stored_object_pick_node import StoredObjectPickNode, main

BaseAlignmentNode = StoredObjectPickNode

__all__ = ["BaseAlignmentNode", "StoredObjectPickNode", "main"]


if __name__ == "__main__":
    main()
