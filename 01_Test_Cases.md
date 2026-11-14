# BỘ KIỂM THỬ (TEST CASES)

# DỰ ÁN YOUTUBE ENGLISH AI TUTOR

## 1. Thông tin chung

| Thuộc tính         | Nội dung                                                             |
| ------------------ | -------------------------------------------------------------------- |
| Tên dự án          | YouTube English AI Tutor                                             |
| Loại kiểm thử      | Chức năng, tích hợp, kiểm tra dữ liệu, giao diện, bảo mật, hiệu năng |
| Ngôn ngữ lập trình | Python                                                               |
| Framework          | Streamlit                                                            |
| Mô hình AI         | Gemini 2.5 Flash                                                     |
| Tổng số Test Case  | 30                                                                   |
| Trạng thái         | Chưa thực thi                                                        |

## 2. Danh sách Test Cases

| TC ID | Kịch bản kiểm thử           | Các bước thực hiện                              | Kết quả mong đợi                                    | Mức độ ưu tiên | Trạng thái    |
| ----- | --------------------------- | ----------------------------------------------- | --------------------------------------------------- | -------------- | ------------- |
| TC001 | Khởi chạy ứng dụng          | Chạy ứng dụng Streamlit                         | Ứng dụng khởi chạy thành công                       | Cao            | Chưa thực thi |
| TC002 | URL YouTube hợp lệ          | Nhập URL dạng youtube.com/watch                 | Hệ thống chấp nhận URL                              | Cao            | Chưa thực thi |
| TC003 | URL YouTube rút gọn         | Nhập URL dạng youtu.be                          | Hệ thống chấp nhận URL                              | Cao            | Chưa thực thi |
| TC004 | URL YouTube Shorts          | Nhập URL dạng Shorts                            | Hệ thống nhận diện URL hợp lệ                       | Trung bình     | Chưa thực thi |
| TC005 | URL YouTube Embed           | Nhập URL dạng embed                             | Hệ thống chấp nhận URL                              | Trung bình     | Chưa thực thi |
| TC006 | URL không hợp lệ            | Nhập URL Facebook hoặc website khác             | Hiển thị thông báo URL không hợp lệ                 | Cao            | Chưa thực thi |
| TC007 | URL bị bỏ trống             | Không nhập URL và nhấn phân tích                | Hệ thống không thực hiện phân tích                  | Cao            | Chưa thực thi |
| TC008 | Video ID không hợp lệ       | Nhập URL có Video ID sai định dạng              | Hiển thị thông báo lỗi                              | Cao            | Chưa thực thi |
| TC009 | Video có phụ đề tiếng Anh   | Nhập video có English Transcript                | Hệ thống lấy được transcript                        | Cao            | Chưa thực thi |
| TC010 | Video có phụ đề tiếng Việt  | Nhập video có Vietnamese Transcript             | Hệ thống lấy được transcript nếu khả dụng           | Trung bình     | Chưa thực thi |
| TC011 | Video không có phụ đề       | Nhập video không có transcript                  | Hiển thị thông báo lỗi phù hợp                      | Cao            | Chưa thực thi |
| TC012 | Video không thể truy cập    | Nhập video bị giới hạn hoặc không khả dụng      | Hệ thống xử lý lỗi lấy transcript                   | Cao            | Chưa thực thi |
| TC013 | Gemini API Key hợp lệ       | Cấu hình API Key hợp lệ                         | Hệ thống kết nối được Gemini API                    | Cao            | Chưa thực thi |
| TC014 | Thiếu Gemini API Key        | Xóa API Key khỏi cấu hình                       | Hiển thị thông báo thiếu API Key                    | Cao            | Chưa thực thi |
| TC015 | Gemini API Key không hợp lệ | Cấu hình API Key sai                            | Hệ thống xử lý lỗi API                              | Cao            | Chưa thực thi |
| TC016 | Transcript rỗng             | Gửi nội dung transcript rỗng đến Gemini Service | Hệ thống không thực hiện phân tích                  | Cao            | Chưa thực thi |
| TC017 | Phân tích video thành công  | Nhập video hợp lệ và API Key hợp lệ             | Trả về kết quả phân tích                            | Cao            | Chưa thực thi |
| TC018 | Kiểm tra Summary            | Phân tích video tiếng Anh                       | Trả về tóm tắt tiếng Anh và tiếng Việt              | Cao            | Chưa thực thi |
| TC019 | Kiểm tra Vocabulary         | Phân tích video                                 | Trả về từ 5–10 từ vựng                              | Cao            | Chưa thực thi |
| TC020 | Kiểm tra Key Sentences      | Phân tích video                                 | Trả về đúng 5 câu quan trọng                        | Cao            | Chưa thực thi |
| TC021 | Kiểm tra Quiz               | Phân tích video                                 | Trả về đúng 5 câu hỏi trắc nghiệm                   | Cao            | Chưa thực thi |
| TC022 | Kiểm tra đáp án Quiz        | Kiểm tra các lựa chọn của từng câu              | Mỗi câu có 4 lựa chọn                               | Cao            | Chưa thực thi |
| TC023 | Chọn đáp án đúng            | Chọn đáp án chính xác                           | Hệ thống hiển thị phản hồi đúng                     | Cao            | Chưa thực thi |
| TC024 | Chọn đáp án sai             | Chọn đáp án không chính xác                     | Hiển thị đáp án đúng và giải thích                  | Cao            | Chưa thực thi |
| TC025 | Tính điểm Quiz              | Hoàn thành toàn bộ câu hỏi                      | Hệ thống tính điểm chính xác                        | Trung bình     | Chưa thực thi |
| TC026 | Kiểm tra Pydantic Schema    | Kiểm tra dữ liệu Gemini trả về                  | Dữ liệu tuân thủ cấu trúc đã định nghĩa             | Cao            | Chưa thực thi |
| TC027 | Kiểm tra giao diện          | Kiểm tra các khu vực kết quả                    | Nội dung hiển thị chính xác và rõ ràng              | Trung bình     | Chưa thực thi |
| TC028 | Gemini API gặp lỗi          | Mô phỏng lỗi từ Gemini API                      | Ứng dụng xử lý lỗi phù hợp                          | Cao            | Chưa thực thi |
| TC029 | Kiểm tra bảo mật API Key    | Kiểm tra giao diện và cấu hình source           | Không để lộ API Key trong giao diện hoặc repository | Cao            | Chưa thực thi |
| TC030 | Phân tích video dài         | Nhập video có thời lượng dài                    | Xử lý thành công hoặc thông báo giới hạn phù hợp    | Trung bình     | Chưa thực thi |

## 3. Các nhóm kiểm thử

### 3.1. Kiểm thử chức năng (Functional Testing)

- Kiểm tra tính hợp lệ của YouTube URL.
- Kiểm tra chức năng lấy transcript.
- Kiểm tra tạo Summary.
- Kiểm tra trích xuất Vocabulary.
- Kiểm tra tạo Key Sentences.
- Kiểm tra tạo và chấm điểm Quiz.

### 3.2. Kiểm thử tích hợp (Integration Testing)

- Kiểm tra tích hợp YouTube Transcript API.
- Kiểm tra tích hợp Gemini API.
- Kiểm tra dữ liệu đầu ra thông qua Pydantic.

### 3.3. Kiểm thử giao diện (UI Testing)

- Kiểm tra khởi chạy ứng dụng.
- Kiểm tra thông báo lỗi.
- Kiểm tra hiển thị kết quả học tập.
- Kiểm tra thao tác làm Quiz.

### 3.4. Kiểm thử bảo mật (Security Testing)

- Kiểm tra quản lý Gemini API Key.
- Kiểm tra biến môi trường.
- Kiểm tra khả năng để lộ thông tin nhạy cảm.

### 3.5. Kiểm thử hiệu năng (Performance Testing)

- Kiểm tra thời gian lấy transcript.
- Kiểm tra thời gian phản hồi của Gemini API.
- Kiểm tra khả năng xử lý video dài.

## 4. Tổng hợp kết quả kiểm thử

| Tiêu chí              | Kết quả       |
| --------------------- | ------------- |
| Tổng số Test Cases    | 30            |
| Số lượng Passed       | Chưa đánh giá |
| Số lượng Failed       | Chưa đánh giá |
| Số lượng Blocked      | Chưa đánh giá |
| Số lượng Not Executed | 30            |

**Lưu ý:** Đây là các kịch bản kiểm thử được xây dựng dựa trên chức năng của source code. Chỉ cập nhật Passed hoặc Failed sau khi thực thi kiểm thử thực tế.
