"""Optional provenance checks against an initialized upstream msopgen checkout."""
import ast
import json
import unittest

from test_environment import ROOT, SCRIPTS


UPSTREAM = ROOT / "msopgen/msopgen/interface/op_tmpl.py"


@unittest.skipUnless(UPSTREAM.is_file(), "msopgen submodule not initialized; recognition snapshots remain self-contained")
class GeneratedTemplateTests(unittest.TestCase):
    def test_host_and_tiling_match_reviewed_upstream_generator(self):
        tree = ast.parse(UPSTREAM.read_text(encoding="utf-8"))
        klass = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "OPTmpl")
        values = {node.targets[0].id: ast.literal_eval(node.value) for node in klass.body
                  if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant)}
        input_data = json.loads((ROOT / "example/quick_start/msopgen/msopgen_demo.json").read_text(encoding="utf-8"))[0]
        parameters = ""
        for kind, key in (("Input", "input_desc"), ("Output", "output_desc")):
            for item in input_data[key]:
                parameters += ('        this->{}("{}")\n            .ParamType(REQUIRED)\n'
                               '            .DataType({{ge::DT_FLOAT16}})\n            .Format({{ge::FORMAT_ND}})\n'
                               '            .UnknownShapeFormat({{ge::FORMAT_ND}});\n').format(kind, item["name"])
        host = (values["OP_HOST_CPP_HEADER"].format(op_fix="add_custom")
                + values["OP_HOST_TILING_FUNC"].format(op_type="AddCustom")
                + values["OP_HOST_INFER_FUNC"] + values["OP_HOST_DEF_BEGIN"].format(op_type="AddCustom")
                + parameters + values["OP_HOST_INFER_REG"] + values["OP_HOST_TILING_REG"]
                + '        this->AICore().AddConfig("__SOC__");\n'
                + values["OP_HOST_DEF_END"].format(op_type="AddCustom"))
        tiling = values["OP_HOST_TILING_DEF_H"].format(op_type="ADD_CUSTOM", op_name="AddCustom")
        for name, expected in (("add_custom.cpp.in", host), ("add_custom_tiling.h.in", tiling)):
            with self.subTest(name=name):
                self.assertEqual((SCRIPTS / "templates" / name).read_text(encoding="utf-8").strip(), expected.strip())


if __name__ == "__main__":
    unittest.main()
