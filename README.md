# AI English Learning Assistant – Your Personal English Tutor

Ứng dụng học tiếng Anh: làm Placement Test để biết trình độ (A1–B2), học qua video YouTube với bài học do Gemini tạo (Summary, Vocabulary, Key Sentences, Quiz).

## 1. Yêu cầu

- Python 3.11+
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
GEMINI_MODEL=gemini-3.5-flash-lite
```

## 3. Chạy ứng dụng

```powershell
streamlit run app.py
```

Trình duyệt thường mở tại `http://localhost:8501`.

## 4. Chạy kiểm thử

```powershell
pip install -r requirements-dev.txt   # một lần, cài thêm pytest
python -m pytest -q
```

Đo thời gian xử lý YouTube (cần API key): xem `docs/week2/07_performance_benchmark.md`.

## 5. Cấu trúc thư mục

```
app.py                  # Khởi chạy + sidebar điều hướng
views/                  # Mỗi file là một trang (Dashboard, Placement Test, ...)
services/               # Xử lý nghiệp vụ (YouTube, Gemini, chấm điểm, SQLite, profile, phiên đăng nhập)
models/                 # Pydantic schema
prompts/                # Prompt cho Gemini
utils/                  # Hàm tiện ích (validate URL, đo thời gian, giờ hiện tại, UI dùng chung)
content/                # Question Bank của Placement Test
data/                   # Database SQLite app.db (tự tạo, không đưa lên Git)
scripts/                # Script benchmark, script chuyển dữ liệu JSON cũ sang SQLite
tests/                  # Unit test
docs/week2/             # Tài liệu Week 2
```

## 6. Luồng YouTube Learning

1. Kiểm tra URL và lấy video ID (`utils/validators.py`).
2. Lấy transcript tiếng Anh (`services/youtube_service.py`) – có cache.
3. Ghép prompt (`prompts/tutor_prompt.py`) và gọi Gemini (`services/gemini_service.py`) – có cache.
4. Pydantic kiểm tra cấu trúc phản hồi.
5. Hiển thị Summary, Vocabulary, Key Sentences, Quiz và thời gian xử lý từng bước.

## 7. Lưu ý

- Không đưa file `.env` lên GitHub.
- Không phải video nào cũng có transcript truy cập được.
- Bài học YouTube được tạo theo trình độ từ Placement Test. Chưa làm test thì dùng A2.
- Không đăng nhập vẫn dùng được ứng dụng và làm test, nhưng kết quả và bài học chỉ được lưu khi đăng nhập. Mật khẩu được băm (xem `docs/week2/09_authentication.md`).
- Dữ liệu lưu trong SQLite `data/app.db` (có sẵn trong Python, không cần cài thêm). Xem `docs/week2/05_json_data_structure.md`.
- File database sẽ mất nếu deploy trên nền tảng không lưu file lâu dài (ví dụ Streamlit Community Cloud).
- LLM có thể mắc lỗi; cần kiểm tra nội dung học liệu trước khi sử dụng chính thức.

## 8. Deploy lên server bằng Docker

Yêu cầu server: Docker + Docker Compose (plugin `docker compose`).

```bash
git clone <repo-url> && cd aia20_group06_anhemchicot
cp .env.example .env        # rồi điền GEMINI_API_KEY
docker compose up -d --build
```

Mở `http://<ip-server>:8501`. Các lệnh thường dùng:

| Việc | Lệnh |
|---|---|
| Cập nhật code mới | `git pull && docker compose up -d --build` |
| Xem log | `docker compose logs -f app` |
| Dừng | `docker compose down` (dữ liệu vẫn còn trong volume) |
| Sao lưu database | `docker compose cp app:/app/data/app.db ./app.db.bak` |

Lưu ý:
- Database nằm trong volume `app-data`. **Đừng** chạy `docker compose down -v` nếu không muốn xóa dữ liệu.
- YouTube thường chặn IP của các cloud lớn (AWS, GCP, Azure...). Nếu lấy transcript bị lỗi "blocked" trên server
  dù chạy local vẫn được, cần chạy ở server có IP khác hoặc cấu hình proxy cho `youtube-transcript-api`.
- Nếu đặt sau reverse proxy (Nginx...), cần bật hỗ trợ WebSocket cho đường dẫn `/_stcore/stream`.
