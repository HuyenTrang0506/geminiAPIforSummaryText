import pathlib
import textwrap
import google.generativeai as genai
import pandas as pd
import json


# API key của bạn
GOOGLE_API_KEY = "your-api-key"

# Cấu hình API key cho genai
genai.configure(api_key=GOOGLE_API_KEY)

# Khởi tạo mô hình Gemini 1.5 Pro
model = genai.GenerativeModel('gemini-1.0-pro')

# Đọc file Excel
xlsx_file_path = "dataset/Dataset hội nghị IUKM.xlsx"
df = pd.read_excel(xlsx_file_path)

# Hàm sử dụng Google Generative AI để tóm tắt văn bản
def summarize_text_batch(texts):
    prompt = f"""
    Summarize the following 10 comments in Vietnamese. When generating the summaries, consider the following:
    - Identify and include the main ideas, center themes, and crucial plot points.
    - Omit unnecessary detail or tangential information that doesn't contribute to the overall understanding.
    - Use clear and concise language to convey the summaries effectively.

    Input: {json.dumps(texts, ensure_ascii=False)}

    The response should in Json format like this:
    [
        "Summary for first paragraph 1",
        "Summary for second paragraph 2",
        "Summary for third paragraph 3",
        "Summary for fourth paragraph 4",
        ...
    ]
    """
    try:
        # Gọi API để lấy tóm tắt
        response = model.generate_content(prompt)
        text_content = response.text
        decoded_text = json.loads(text_content)
        summaries = decoded_text
        print(summaries)
        return summaries
    except Exception as e:
        # Xử lý lỗi và trả về thông báo lỗi cho tất cả văn bản
        print(f"Error occurred: {e}")
        return [f"Error: {e}"] * len(texts)
# Tạo cột Tóm tắt từ cột Comment đã chỉnh sửa
summaries = []
batch_size = 10
for i in range(0, len(df['Comment đã chỉnh sửa']), batch_size):
    # Chọn 10 dòng tiếp theo từ cột 'Comment đã chỉnh sửa'
    batch = df['Comment đã chỉnh sửa'][i:i+batch_size].tolist()
    try:
        #lay do dai dataset chia 10, vi du 300/10 = 30
        print(f"Sending batch {i // batch_size + 1} of 30: {batch}")
        summary_batch = summarize_text_batch(batch)
        summaries.extend(summary_batch)
        print(f"Batch {i // batch_size + 1} processed successfully")
    except Exception as e:
        summaries.extend([f"Error: {e}"] * len(batch))
        print(f"Batch {i // batch_size + 1} failed - {e}")


df['Tóm tắt'] = summaries

# Ghi lại DataFrame đã cập nhật vào file Excel
output_file = "dataset/dataVietSummaries.xlsx"
df.to_excel(output_file, index=False)
print(f"Dataset đã được lưu với cột 'Tóm tắt' vào {output_file}")
