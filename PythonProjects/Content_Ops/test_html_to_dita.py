import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import unittest
import tempfile
from pathlib import Path

import html_to_dita as h2d

SAMPLE_DIAGNOSTICS = """\
<!doctype html>
<html><head><title>Diagnostics Information</title></head>
<body>
  <h1>Diagnostics Information</h1>
  <h3>This page will be updated once the feature is implemented.</h3>
</body></html>
"""

SAMPLE_LUA = """\
<!doctype html>
<html><head><title>LUA program</title></head>
<body>
  <h1>LUA program</h1>
  <div>
    <p>The TRC script editor is a view of the TRC Lua Program that allows you to read/send Lua programs from/to the TRC device.</p>
    <p>Steps to write and modify the Lua programs in N4 database:</p>
    <ul>
      <li>To open the TRC script editor, navigate to the Lua program and select view as "TRC Script Editor."</li>
      <li>Below is the editor, on which the content will be shown from Niagara database.</li>
      <li>In the editor, you will find three buttons at the top: Read, Save, Send.</li>
    </ul>
  </div>
</body></html>
"""

SAMPLE_COMPONENTS = """\
<!doctype html>
<html><head><title>Components</title></head>
<body>
  <h1>Components</h1>
  <p>TRC Components include network, devices, points and other model building blocks associated with a module. You may drag them to a property or wire sheet from the TRC device.</p>
  <h4>Related Links</h4>
  <p>Controllers:</p>
  <ul>
    <li>SXW TRC 3500 Bcc W</li>
    <li>SXW TRC 3500 Bcc X</li>
  </ul>
  <p>Points:</p>
  <ul>
    <li>Analog input</li>
    <li>Analog output</li>
  </ul>
</body></html>
"""

SAMPLE_LABEL_LIST_FALLBACK = """\
<!doctype html>
<html><head><title>Label List Only</title></head>
<body>
  <h1>Label List Only</h1>
  <div>
    <p>Things:</p>
    <ul><li>One</li><li>Two</li></ul>
  </div>
</body></html>
"""


class TestHtmlToDita(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.in_dir = Path(self.tmp.name) / 'in'
        self.out_dir = Path(self.tmp.name) / 'out'
        self.in_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        self.tmp.cleanup()

    def _write(self, name: str, content: str) -> Path:
        p = self.in_dir / name
        p.write_text(content, encoding='utf-8')
        return p

    def _convert(self, path: Path):
        return h2d.convert_one(path, self.out_dir, 'auto', h2d.graphic_rel, h2d.image_scale)

    def test_diagnostics_heading_only_preserved(self):
        src = self._write('DiagnosticsFiles.html', SAMPLE_DIAGNOSTICS)
        out, ttype = self._convert(src)
        self.assertEqual(ttype, 'concept')
        xml = out.read_text(encoding='utf-8')
        self.assertIn('Diagnostics Information', xml)
        self.assertIn('This page will be updated once the feature is implemented.', xml)
        self.assertIn('<section>', xml)

    def test_lua_program_wrappers_and_lists_preserved(self):
        src = self._write('LUAScriptProgram.html', SAMPLE_LUA)
        out, ttype = self._convert(src)
        self.assertEqual(ttype, 'concept')
        xml = out.read_text(encoding='utf-8')
        self.assertIn('The TRC script editor is a view of the TRC Lua Program', xml)
        self.assertIn('<ul>', xml)
        self.assertIn('TRC Script Editor', xml)

    def test_components_label_plus_list_rendering(self):
        src = self._write('Components.html', SAMPLE_COMPONENTS)
        out, ttype = self._convert(src)
        self.assertEqual(ttype, 'concept')
        xml = out.read_text(encoding='utf-8')
        # In a heading-based section, label+list becomes <p><b>Label</b></p> + list
        self.assertIn('<p><b>Controllers</b></p>', xml)
        self.assertIn('SXW TRC 3500 Bcc W', xml)
        self.assertIn('<ul>', xml)

    def test_label_list_fallback_yields_titled_section(self):
        src = self._write('LabelListOnly.html', SAMPLE_LABEL_LIST_FALLBACK)
        out, ttype = self._convert(src)
        self.assertEqual(ttype, 'concept')
        xml = out.read_text(encoding='utf-8')
        # Fallback mode allows titled <section> for label+list
        self.assertIn('<title>Things</title>', xml)
        self.assertIn('<ul>', xml)
        self.assertIn('<li>One</li>', xml)

    def test_doctype_present_for_concept(self):
        src = self._write('DiagnosticsFiles.html', SAMPLE_DIAGNOSTICS)
        out, _ = self._convert(src)
        xml = out.read_text(encoding='utf-8')
        self.assertIn('<!DOCTYPE concept PUBLIC "-//OASIS//DTD DITA Concept//EN" "concept.dtd">', xml)

def test_image_tag_emitted(self):
    # Minimal page with one IMG tag. Use 'graphics' on input to prove normalization → 'graphic' in output.
    html = """<!doctype html><html><body><h1>Img</h1>graphics/pic.png</body></html>"""
    src = self._write('HasImg.html', html)

    # Ensure we normalize to a sibling 'graphic/' folder at import time
    import html_to_dita as h2d
    out, _ = h2d.convert_one(src, self.out_dir, 'auto', 'graphic', h2d.image_scale)

    xml = out.read_text(encoding='utf-8')

    # Look for the literal XML tag (not HTML-escaped).
    self.assertIn('<image href="graphic/pic.png"', xml)

    # (Optional) A more robust check that tolerates attribute order:
    # import re
    # self.assertRegex(xml, r'<image\\s+[^>]*href="graphic/pic\\.png"')

if __name__ == '__main__':
    unittest.main(verbosity=2)