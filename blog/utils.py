"""
    HierarchyBuilder, facilitates the construction of hierarchical tree structures from a list of items with parent-child relationships.
"""


class HierarchyBuilder:
    def build(self, items, parent=None):
        result = []

        for item in items:
            if item["parent"] == parent:
                children = self.build(items, item["id"])
                if children:
                    item["children"] = children
                result.append(item)

        return result
