from parsing import ResumeParser

config = {
    'output_format': 'dict',
    'include_metadata': True,
    'spacy_model': 'en_core_web_md',  # More accurate but slower
    'use_layout_analysis': False,
}
parser = ResumeParser(config=config)
result = parser.parse(r"C:\Users\12345\OneDrive\Desktop\projects\ResumeParsing\data\ritwikresume.pdf")

print(result)
