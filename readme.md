# 편한 가계부 app 으로 월간 지출 예측 웹 애플리케이션
![alt text](image.png)

편한 가계부의 월별 지출 데이터를 엑셀 파일로 업로드하여, 월간 지출 현황을 시각화하고 미래 월의 지출을 예측하는 Flask 웹 app.  
단, 시트 이름은 반드시 '25-1-1_25-12-31'로 고정해야 함.

---

## 프로젝트 구성

- `app_regression.py`  
  - **총액만 단순선형회귀 모델**을 사용하여 다음 달 총 지출액을 예측하고 시각화하는 웹 앱 코드
  - 엑셀 파일을 업로드하면 월별 총액 그래프와 함께 다음 달 총액 예측값을 그래프에 표시
  - ![alt text](image-1.png)
- `app_regression2.py`  
  - **항목별 단순선형회귀 모델**을 사용하여 각 지출 항목별 다음 달 지출액을 예측하고 시각화하는 웹 앱 코드(다변량 변순데 단순선형회귀 사용해서 부정확함)
  - 총액뿐 아니라 각 지출 항목별 예측값도 그래프에 함께 표시(부정확함)
  - ![alt text](image-2.png)

- `app.py`  
  - 월간 지출 데이터를 업로드하여 시각화만 하는 기본 웹 앱 코드
  - 예측 기능 미포함. 스크린샷 생략

---

## 사용 방법
0. 원하는 대로 전처리 파트(분류) 수정하기

  ![alt text](image-4.png)
1. 가상환경 생성 및 활성화(powershell 기준)
2. 필요한 라이브러리 설치  
   ```bash
   venv\Scripts\Activate.ps1
   pip install flask pandas matplotlib openpyxl scikit-learn numpy
   
3. 원하는 앱 스크립트(app_regression.py 또는 app_regression2.py) 실행
    '''bash
   python app_regression.py
   python app_regression.py
4. 파일 업로드 후, '업로드'버튼 클릭

    ![alt text](image-3.png)

## 기술스택 및 환경
    - Python 3.12, Windows 11 64bit
    - Flask (웹 프레임워크)
    - Pandas (데이터 처리)
    - Matplotlib (그래프 시각화)
    - scikit-learn (머신러닝 - 선형회귀)
    - NumPy (수치 계산)