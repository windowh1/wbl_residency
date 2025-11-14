# Based on the search results, I have gathered the key information
# Now I'll create the summary and save it to the specified file

output_path = "/Users/user/Library/Mobile Documents/com~apple~CloudDocs/Desktop/WBL/wbl_residency/papers/skills-vs-mcp/experiment3/results/code_execution_tests/code_execution_enabled/20251114_180150/implant_insurance.txt"

content = """건강보험 임플란트 보장 기준

1. 나이 제한
   - 만 65세 이상 건강보험 가입자 또는 피부양자
   - 참고: 2015년 7월 1일 이전에는 만 75세 이상, 2015년 7월 1일~2016년 6월 30일에는 만 70세 이상이었음

2. 보장 개수
   - 1인당 평생 2개까지 급여 적용
   - 단, 치과의사의 의학적 판단 하에 불가피하게 시술을 중단하는 경우 평생 인정 개수에 포함되지 않음

3. 본인부담금
   - 본인부담률: 30%
   - 본인부담상한제 적용

출처: 국민건강보험공단 (www.nhis.or.kr)
"""

with open(output_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"파일이 성공적으로 저장되었습니다: {output_path}")
print("\n저장된 내용:")
print(content)