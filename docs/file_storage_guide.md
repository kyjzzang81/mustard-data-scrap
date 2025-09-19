# 파일 저장소 관리 가이드

## 🗄️ **원본 파일 저장 전략**

### **Supabase Storage 사용 (추천)**

#### 장점
- ✅ **클라우드 기반**: 어디서든 접근 가능
- ✅ **자동 백업**: Supabase가 자동으로 백업 관리
- ✅ **API 접근**: REST API로 파일 관리
- ✅ **보안**: RLS(Row Level Security) 지원
- ✅ **확장성**: 필요에 따라 용량 확장

#### 설정 방법

1. **환경 변수 설정**
```bash
cp .env.example .env
# .env 파일에 Supabase 정보 입력
```

2. **저장소 버킷 생성**
```bash
python3 utils/file_storage_manager.py
```

3. **파일 업로드**
```bash
python3 scripts/deploy_files.py --deploy
```

## 📁 **파일 구조**

```
Supabase Storage/
├── metadata/                    # SDGs 메타데이터 PDF 파일들
│   ├── Metadata-01-01-01a.pdf
│   ├── Metadata-01-01-01b.pdf
│   └── ...
├── framework/                   # 프레임워크 Excel 파일
│   └── Global-Indicator-Framework-after-2025-review-English.xlsx
└── processed/                   # 처리된 데이터 파일들
    ├── sdgs_metadata_analysis_20241219.json
    ├── sdgs_supabase_format_20241219.json
    └── indicators/
        ├── indicator_1.1.1.json
        └── ...
```

## 🚀 **사용법**

### **1. 파일 업로드**
```bash
# 전체 파일 배포
python3 scripts/deploy_files.py --deploy

# 특정 폴더만 업로드
python3 -c "
from utils.file_storage_manager import FileStorageManager
storage = FileStorageManager()
storage.upload_directory('data_sources/un_sdg/raw/metadata', 'metadata')
"
```

### **2. 파일 다운로드**
```bash
# 원격 파일 목록 조회
python3 scripts/deploy_files.py --list

# 파일 다운로드
python3 scripts/deploy_files.py --download --local-dir downloads
```

### **3. API 사용**
```bash
# API 서버 시작
python3 utils/file_api.py

# 파일 목록 조회
curl http://localhost:8000/files

# 특정 파일 다운로드
curl http://localhost:8000/files/metadata/Metadata-01-01-01a.pdf
```

## 🔄 **백업 전략**

### **자동 백업**
- **일일 백업**: 매일 오전 2시
- **주간 백업**: 매주 일요일 오전 3시  
- **월간 백업**: 매월 1일 오전 4시
- **자동 정리**: 30일 이상 된 일일 백업 자동 삭제

### **백업 실행**
```bash
# 수동 백업
python3 scripts/backup_strategy.py --daily
python3 scripts/backup_strategy.py --weekly
python3 scripts/backup_strategy.py --monthly

# 백업 상태 확인
python3 scripts/backup_strategy.py --status

# 스케줄러 시작
python3 scripts/backup_strategy.py --schedule
```

## 🔐 **보안 설정**

### **RLS 정책**
```sql
-- 공개 읽기 정책
CREATE POLICY "Allow public read access" ON sdg_metadata_files 
FOR SELECT USING (true);

-- 관리자만 쓰기 허용
CREATE POLICY "Allow admin write access" ON sdg_metadata_files 
FOR ALL USING (auth.role() = 'admin');
```

### **파일 접근 제한**
- PDF/Excel 파일만 업로드 허용
- 파일 크기 제한: 100MB
- 비공개 버킷 사용 (공개 URL은 필요시 생성)

## 📊 **모니터링**

### **파일 상태 확인**
```bash
# 저장소 상태 확인
curl http://localhost:8000/health

# 파일 매니페스트 생성
python3 -c "
from utils.file_storage_manager import FileStorageManager
storage = FileStorageManager()
manifest = storage.generate_file_manifest()
print(json.dumps(manifest, indent=2))
"
```

### **사용량 모니터링**
- Supabase 대시보드에서 저장소 사용량 확인
- 백업 로그 파일로 백업 상태 추적
- API 로그로 접근 패턴 분석

## 🔧 **문제 해결**

### **일반적인 문제들**

1. **업로드 실패**
   - 파일 크기 확인 (100MB 제한)
   - 파일 형식 확인 (PDF, Excel만 허용)
   - 네트워크 연결 확인

2. **다운로드 실패**
   - 파일 경로 확인
   - 권한 설정 확인
   - 저장소 연결 상태 확인

3. **백업 실패**
   - 저장소 용량 확인
   - 권한 설정 확인
   - 로그 파일 확인

### **로그 확인**
```bash
# 백업 로그
cat backup_log.json

# API 로그 (서버 실행 시)
tail -f logs/file_api.log
```

## �� **비용 최적화**

### **저장 비용**
- Supabase Storage: $0.021/GB/월
- 67MB 데이터: 약 $0.001/월
- 백업 포함 시: 약 $0.002/월

### **비용 절약 팁**
1. **압축**: 큰 파일은 압축 후 업로드
2. **정리**: 불필요한 파일 정기적 삭제
3. **계층화**: 자주 사용하지 않는 파일은 별도 저장소로 이동

## 🚀 **확장 계획**

### **단기 (1-3개월)**
- [ ] 자동 백업 스케줄링
- [ ] 파일 버전 관리
- [ ] 사용량 모니터링 대시보드

### **중기 (3-6개월)**
- [ ] CDN 연동으로 다운로드 속도 향상
- [ ] 파일 암호화
- [ ] 다중 지역 백업

### **장기 (6개월+)**
- [ ] AI 기반 파일 분류
- [ ] 자동 메타데이터 추출
- [ ] 파일 검색 엔진
