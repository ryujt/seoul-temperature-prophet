# PRD

* seoul_last_5years_hourly.jsonl을 읽어서 날짜와 시간을 입력하면 온도를 예측하도록 코드를 작성해줘.
  *seoul_last_5years_hourly.jsonl의 데이터 구조는 다음과 같다.
    * {"date": "2022-01-01", "time": "00:00", "temperature": -8.9, "humidity": 33, "precip_probability": null, "is_rain": 0, "is_snow": 0}
* facebook의 Prophet 라이브러리를 사용해줘.
* 코드를 작성하고 테스트하여 오류가 없을 때까지 반복해줘.
* 파이썬 코드로 작성하고, 필요한 라이브러리는 직접 설치해줘 (python3)