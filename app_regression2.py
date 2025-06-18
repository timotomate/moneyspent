# 전체 항목 예측용
from flask import Flask, request, render_template_string
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

upload_page = '''
<!doctype html>
<title>월간 지출 그래프 업로드</title>
<h1>엑셀 파일 업로드</h1>
<form action="/" method="post" enctype="multipart/form-data">
  <input type="file" name="file" accept=".xlsx" required>
  <input type="submit" value="업로드">
</form>
{% if img_data %}
<h2>월간 지출 (자동 반영 + 항목별 예측)</h2>
<img src="data:image/png;base64,{{ img_data }}" alt="월간 지출 그래프">
{% endif %}
'''

def to_ten_thousands(x):
    return round(x / 1000) / 10

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file:
            try:
                # 엑셀 파일 pandas로 읽기 (시트명 고정)
                df = pd.read_excel(uploaded_file, sheet_name='25-1-1_25-12-31')

                # 지출 데이터 필터링 및 전처리
                df_expense = df[df['수입/지출'] == '지출'][['날짜', '분류', '금액']]
                df_expense['날짜'] = pd.to_datetime(df_expense['날짜'])

                # 최신 월 자동 감지
                min_month = df_expense['날짜'].dt.month.min()
                max_month = df_expense['날짜'].dt.month.max()
                df_expense = df_expense[(df_expense['날짜'].dt.month >= min_month) & (df_expense['날짜'].dt.month <= max_month)]

                # 분류별 매핑 딕셔너리
                category_map = {
                    '식비(혼밥만)': '식비및커피',
                    '커피': '식비및커피',
                    '술자리및외식': '술자리및외식',
                    '송도생활': '송도생활',
                    '쿠팡': '생활비및용품비',
                    '마트/편의점': '생활비및용품비',
                    '생활용품': '생활비및용품비',
                    '교통/차량': '교통비',
                    '킥보드전기자전거': '교통비',
                    '사치품(전자기기등)': '쇼핑',
                    '패션/미용': '쇼핑',
                    '경조사비': '일회성비용',
                    '선물': '일회성비용',
                    '부모님': '일회성비용',
                    '세탁비': '일회성비용',
                }

                # 매핑 가능한 분류만 필터링
                df_expense = df_expense[df_expense['분류'].isin(category_map.keys())]

                # 분류명 매핑 적용
                df_expense['분류'] = df_expense['분류'].map(category_map)

                df_expense['월'] = df_expense['날짜'].dt.month

                # 월별, 새 분류별 금액 합계 집계
                monthly_sum = df_expense.groupby(['월', '분류'])['금액'].sum().unstack(fill_value=0).sort_index()

                # 총액 컬럼 추가
                monthly_sum['총액'] = monthly_sum.sum(axis=1)

                monthly_sum_display = monthly_sum.applymap(to_ten_thousands)

                # 머신러닝 예측: 각 항목별 다음 달 지출 예측
                X = monthly_sum_display.index.values.reshape(-1, 1)  # 월
                pred_dict = {}

                for category in monthly_sum_display.columns:
                    y = monthly_sum_display[category].values.reshape(-1, 1)
                    model = LinearRegression()
                    model.fit(X, y)
                    next_month = np.array([[monthly_sum_display.index.max() + 1]])
                    pred = model.predict(next_month)[0][0]
                    pred_dict[category] = pred

                # 그래프 그리기 설정
                plt.rcParams['font.family'] = 'Malgun Gothic'
                plt.rcParams['axes.unicode_minus'] = False
                plt.figure(figsize=(16, 9))

                for category in monthly_sum_display.columns:
                    plt.plot(monthly_sum_display.index, monthly_sum_display[category], marker='o', label=category)
                    for x, y_val in zip(monthly_sum_display.index, monthly_sum_display[category]):
                        plt.text(x, y_val, f'{y_val:.1f}만원', fontsize=10, ha='center', va='bottom')

                # 예측값 모두 표시
                next_x = monthly_sum_display.index.max() + 1
                for category, pred_val in pred_dict.items():
                    plt.plot(next_x, pred_val, marker='o', label=f'{category} (예상)')
                    plt.text(next_x, pred_val, f'{pred_val:.1f}만원 (예상)', fontsize=8, ha='center', va='bottom')

                plt.title('월간 지출 (자동 반영 + 항목별 예측)', fontsize=16)
                plt.xlabel('월별', fontsize=14)
                plt.ylabel('총액 (만원)', fontsize=14)
                plt.xticks(list(monthly_sum_display.index) + [next_x], fontsize=12)
                plt.legend(fontsize=10)
                plt.grid(True)

                # 이미지 메모리에 저장 및 base64 인코딩
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                plt.close()
                buf.seek(0)
                img_data = base64.b64encode(buf.getvalue()).decode()

                return render_template_string(upload_page, img_data=img_data)

            except Exception as e:
                return f'오류 발생: {e}'
        else:
            return '파일이 업로드되지 않았습니다.'
    else:
        return render_template_string(upload_page)

if __name__ == '__main__':
    app.run(debug=True)
