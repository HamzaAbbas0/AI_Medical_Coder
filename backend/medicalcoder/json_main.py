import json
from json_pipeline import get_icd_hierarchy



result, text_output = get_icd_hierarchy("F41")
print(text_output)
# print(result)
