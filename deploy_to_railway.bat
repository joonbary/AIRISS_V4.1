@echo off
chcp 65001 > nul
cls
echo 🚀 AIRISS 새로운 Excel API를 Railway에 배포
echo.

cd /d "C:\Users\apro\OneDrive\Desktop\AIRISS\airiss_v4"

echo 📋 Git 상태 확인...
git status

echo.
echo 📦 변경사항 추가...
git add .

echo.
echo 💾 커밋 생성...
git commit -m "✅ Excel 내보내기 API 완전 개선 + Git merge conflict 해결

🆕 새로운 기능:
- /api/analysis-storage/export-excel (실제 Excel 파일 다운로드)
- /api/analysis-storage/export-csv (BOM 포함 CSV)
- 다중 시트 Excel 생성 (분석 결과, 통계, 점수 분포)
- 한글 컬럼명 및 스타일링

🔧 수정사항:
- Git merge conflict 완전 해결 (text_analyzer.py, hybrid_analyzer.py)
- Procfile 경로 수정 (app.main:app)
- Python 3.13 호환성 개선"

echo.
echo 🚀 Railway에 배포...
git push origin main

echo.
echo ✅ 배포 완료! Railway에서 자동으로 새 버전을 빌드합니다.
echo 📋 약 2-3분 후 새로운 Excel API를 사용할 수 있습니다.
echo.
echo 🌐 배포 후 테스트 URL:
echo https://web-production-4066.up.railway.app/api/analysis-storage/export-excel
echo https://web-production-4066.up.railway.app/api/analysis-storage/export-csv
echo https://web-production-4066.up.railway.app/health
echo.
pause
