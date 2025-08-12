# GitHub 저장소 설정 가이드

## 1. GitHub에서 새 저장소 생성

1. [GitHub.com](https://github.com)에 로그인
2. 우측 상단의 `+` 버튼 클릭 → `New repository` 선택
3. 다음 정보 입력:
   - Repository name: `seoul-temperature-prophet` (또는 원하는 이름)
   - Description: `Seoul temperature prediction using Facebook Prophet`
   - Public 선택
   - **DO NOT** initialize with README, .gitignore, or license (이미 로컬에 있음)
4. `Create repository` 클릭

## 2. 로컬 저장소를 GitHub에 연결

GitHub 저장소를 생성한 후, 다음 명령어를 실행하세요:

```bash
# GitHub 저장소 URL로 변경해주세요 (예: https://github.com/YOUR_USERNAME/seoul-temperature-prophet.git)
git remote add origin YOUR_GITHUB_REPOSITORY_URL

# 코드 푸시
git push -u origin main
```

예시:
```bash
git remote add origin https://github.com/yourusername/seoul-temperature-prophet.git
git push -u origin main
```

## 3. 확인

브라우저에서 GitHub 저장소 페이지를 새로고침하면 모든 파일이 업로드된 것을 확인할 수 있습니다.

## 프로젝트 구조

```
seoul-temperature-prophet/
│
├── examples/
│   └── archives/
│       ├── main.py
│       └── seoul_last_5years_hourly.jsonl
│
├── .gitignore
├── README.md
├── PRD.md
├── requirements.txt
├── prepare.py
├── temperature_predictor.py
├── simple_predictor.py
└── test_predictor.py
```

## 추가 설정 (선택사항)

### GitHub Actions 설정 (CI/CD)

`.github/workflows/test.yml` 파일을 생성하여 자동 테스트를 설정할 수 있습니다:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python test_predictor.py
```

### 라이선스 추가

`LICENSE` 파일을 추가하여 오픈소스 라이선스를 명시할 수 있습니다 (MIT, Apache 2.0 등).

### Topics 추가

GitHub 저장소 페이지에서 톱니바퀴 아이콘을 클릭하고 Topics에 다음을 추가:
- `prophet`
- `time-series`
- `weather-prediction`
- `seoul`
- `temperature`
- `machine-learning`
- `python`