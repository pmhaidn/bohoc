# Student Management API

## Features

1. Dự đoán rủi ro bỏ học: 
- Xây dựng mô hình: Xây dựng mô hình dự đoán dựa trên các yếu tố như điểm số, lịch sử tham gia các hoạt động, kết quả khảo sát, tương tác với giảng viên,… 
- Phát hiện sớm: Nhận diện sinh viên có nguy cơ bỏ học sớm để kịp thời đưa ra các biện pháp hỗ trợ. 
- Cá nhân hóa hỗ trợ: Cung cấp các chương trình hỗ trợ học tập, tư vấn tâm lý phù hợp với từng sinh viên. 
2. Tối ưu hóa trải nghiệm sinh viên: 
- Cá nhân hóa thông tin: Cung cấp thông tin về các hoạt động, sự kiện, cơ hội học tập phù hợp với sở thích và năng lực của từng sinh viên. 
- Tư vấn chọn môn học hoặc chuyên ngành: Sử dụng thuật toán gợi ý để giúp sinh viên lựa chọn môn học hoặc chuyên ngành học phù hợp với năng lực và mục tiêu nghề nghiệp. 
- Quản lý lịch học: Tự động sắp xếp lịch học linh hoạt, tối ưu hóa thời gian cho sinh viên. 
3. Nâng cao hiệu quả tuyển sinh: 
- Phân tích dữ liệu ứng viên: Xây dựng hồ sơ ứng viên chi tiết, phân tích xu hướng lựa chọn ngành học, từ đó điều chỉnh chiến lược tuyển sinh. 
- Dự đoán kết quả học tập: Dự đoán khả năng thành công của ứng viên trong quá trình học tập để đưa ra quyết định tuyển sinh chính xác. 
- Tương tác với ứng viên: Tự động hóa quá trình tương tác với ứng viên, cung cấp thông tin nhanh chóng và chính xác. 
4. Quản lý hoạt động ngoại khóa: 
- Phân tích sự tham gia: Đánh giá mức độ tham gia của sinh viên vào các hoạt động ngoại khóa, từ đó đưa ra các chương trình phù hợp. 
- Xây dựng cộng đồng: Kết nối sinh viên có cùng sở thích, tạo ra các cộng đồng học tập và làm việc hiệu quả. 
- Đánh giá tác động: Đánh giá tác động của các hoạt động ngoại khóa đến sự phát triển toàn diện của sinh viên. 
5. Đánh giá hiệu quả giảng dạy: 
- Phân tích phản hồi: Thu thập và phân tích phản hồi của sinh viên về chất lượng giảng dạy, từ đó cải thiện phương pháp giảng dạy. 
- Đánh giá hiệu quả học tập: Đánh giá hiệu quả học tập của sinh viên thông qua các bài kiểm tra, dự án, từ đó đánh giá hiệu quả của chương trình đào tạo.

## Setup

1. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation: http://localhost:8000/docs
- ReDoc documentation: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST `/api/v1/auth/token` - Login to get access token
- POST `/api/v1/auth/logout` - Logout

### Students
- GET `/api/v1/students/` - List all students
- GET `/api/v1/students/{student_id}` - Get student by ID
- POST `/api/v1/students/` - Create new student
- PUT `/api/v1/students/{student_id}` - Update student
- DELETE `/api/v1/students/{student_id}` - Delete student

## Authentication

To use the API, you need to:

1. Login using the default admin account:
   - Username: admin
   - Password: admin

2. Get the access token from the login response

3. Include the token in the Authorization header for all subsequent requests:
   ```
   Authorization: Bearer <your_access_token>
   ```

## Example Usage

1. Login to get token:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin"
```

2. Create a new student:
```bash
curl -X POST "http://localhost:8000/api/v1/students/" \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "student_code": "ST001",
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "address": "123 Main St"
  }'
```
### DEPLOY
```bash
gcloud run deploy bohoc --source . --env-vars-file env.yaml --region asia-southeast1 --allow-unauthenticated
```