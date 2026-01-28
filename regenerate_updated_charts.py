import subprocess
import os
import sys
import io

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 재생성할 mmd 파일 목록
mmd_files = [
    "partner_inquiry_process.mmd",
    "LAFC_issue_process.mmd",
    "ta_partner_inspection.mmd",
    "domestic_product_register.mmd",
    "hanin_product_register.mmd",
    "ta_inspection.mmd",
    "monitoring_flowchart.mmd"
]

os.chdir("mermaid_images")

for mmd_file in mmd_files:
    png_file = mmd_file.replace(".mmd", ".png")
    print(f"\n생성 중: {mmd_file} → {png_file}")
    
    cmd = f"npx -y @mermaid-js/mermaid-cli -i {mmd_file} -o {png_file} -w 3000 -H 4000 -b transparent"
    
    result = subprocess.run(
        ["powershell", "-Command", cmd],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"완료: {png_file}")
    else:
        print(f"실패: {png_file}")
        if result.stderr:
            print(result.stderr[:500])

print("\n" + "=" * 60)
print("모든 이미지 재생성 완료!")
print("=" * 60)
