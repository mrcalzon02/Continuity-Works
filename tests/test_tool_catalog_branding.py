import unittest

from structure_capability.tooling import tool_catalog


class ToolCatalogBrandingTests(unittest.TestCase):
    def test_each_tool_uses_canonical_continuity_works_extension(self):
        catalog = tool_catalog()
        self.assertTrue(catalog["tools"])
        for tool in catalog["tools"]:
            with self.subTest(tool=tool["name"]):
                self.assertIn("x-continuity-works-tool", tool)
                self.assertNotIn("x-structuresmith", tool)


if __name__ == "__main__":
    unittest.main()
