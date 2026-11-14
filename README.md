# YouTube English AI Tutor

Ứng dụng MVP chuyển transcript YouTube thành bài học tiếng Anh cho người học trình độ A2.

## 1. Yêu cầu

- Python 3.12+
- Gemini API Key từ Google AI Studio
- Video YouTube có phụ đề mà `youtube-transcript-api` có thể truy cập

## 2. Cài đặt trên Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Sao chép `.env.example` thành `.env`, sau đó điền API Key:

```env
GEMINI_API_KEY=your_real_api_key
GEMINI_MODEL=gemini-2.5-flash
```

## 3. Chạy ứng dụng

```powershell
streamlit run app.py
```

Trình duyệt thường mở tại `http://localhost:8501`.

## 4. Luồng hoạt động

1. Streamlit nhận URL YouTube.
2. `validators.py` kiểm tra URL và trích xuất video ID.
3. `youtube_service.py` lấy transcript.
4. `tutor_prompt.py` ghép learner context, task instructions và transcript.
5. `gemini_service.py` gửi prompt đến Gemini.
6. Pydantic kiểm tra cấu trúc phản hồi.
7. Streamlit hiển thị Summary, Vocabulary, Key Sentences và Quiz.

## 5. Lưu ý

- Không đưa file `.env` lên GitHub.
- Không phải video nào cũng có transcript truy cập được.
- Transcript dài có thể vượt giới hạn đầu vào của model hoặc làm tăng chi phí.
- LLM có thể mắc lỗi; cần kiểm tra nội dung học liệu trước khi sử dụng chính thức.
- Ứng dụng yêu cầu Gemini trả JSON theo schema. Nếu model/API không hỗ trợ model được chọn, hãy đổi `GEMINI_MODEL` sang model Gemini có hỗ trợ structured output trong tài khoản của bạn.
