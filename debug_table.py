#!/usr/bin/env python3
from bodh import MarkdownToPDF

converter = MarkdownToPDF()

test_content = '''Here is a simple table:
| Quarter | Revenue | Growth |
|---------|---------|---------|
| Q1 2024 | $1.2M | +15% |
| Q2 2024 | $1.5M | +25% |
End of table test.'''

print('Testing table detection...')
print('Original content:')
print(repr(test_content))
print()

result = converter._convert_tables_to_latex(test_content)
print('After table conversion:')
print(repr(result))
print()

if result != test_content:
    print('✅ Table conversion worked')
    print('Converted:')
    print(result)
else:
    print('❌ Table conversion failed')