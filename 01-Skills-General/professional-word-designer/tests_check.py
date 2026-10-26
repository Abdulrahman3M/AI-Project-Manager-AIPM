"""Offline integrity test for Professional Word Designer v5."""
from pathlib import Path
import re
import subprocess
import sys

root=Path(__file__).resolve().parent
required=[
'SKILL.md','README.md','CHANGELOG.md','VERSION',
'references/document-contract-v5.md','references/research-to-word-pipeline.md',
'references/research-intelligence.md','references/claim-evidence-system.md',
'references/source-quality-model.md','references/citation-style-engine.md',
'references/literature-review-engine.md','references/academic-document-types.md',
'references/math-equations.md','references/large-document-architecture.md',
'references/normative-example-contract.md','references/word-implementation.md',
'references/enterprise-visual-design.md','references/template-atlas.md',
'references/tool-landscape.md','references/rtl-hardening.md',
'references/visual-explanation-system.md','references/multilingual-localization.md',
'examples/NORMATIVE_EXAMPLES.md','examples/EXAMPLE_COVERAGE.json',
'schemas/document-contract.schema.json','schemas/claim-evidence.schema.json',
'schemas/chapter-manifest.schema.json','scripts/build_chapter_index.py',
'scripts/validate_example_coverage.py','templates/MASTER_PROMPT.md','templates/MASTER_PROMPT_AR.md'
]
missing=[p for p in required if not (root/p).is_file()]
assert not missing,f"Missing required files: {missing}"
skill=(root/'SKILL.md').read_text(encoding='utf-8')
assert skill.startswith('---\nname: professional-word-designer\n')
assert '# Professional Word Designer — v5.1.0' in skill
assert '100 pages or more' in skill
assert '124 fine-grained normative examples' in skill
assert 'Claim–Evidence Matrix' in skill
assert 'Professional Template Atlas' in skill and 'RTL Hardening' in skill
for ref in re.findall(r'`((?:references|templates|examples)/[^`\n]+\.md)`',skill):
    assert (root/ref).is_file(),f"Broken referenced file: {ref}"
r=subprocess.run([sys.executable,str(root/'scripts/validate_example_coverage.py')],capture_output=True,text=True)
assert r.returncode==0,r.stdout+r.stderr
assert 'Coverage: 100.0%' in r.stdout
word=(root/'references/word-implementation.md').read_text(encoding='utf-8')
assert 'TOC \\o "1-3" \\h \\z \\u' in word
assert 'STYLEREF' in word and '`PAGE`' in word
assert all((root/p).stat().st_size>100 for p in required if p != 'VERSION')
assert (root/'VERSION').read_text(encoding='utf-8').strip() == '1.1.0'
print(f"PASS | {len(required)} required v5 files found; example coverage is 100%; core Word structures retained")
