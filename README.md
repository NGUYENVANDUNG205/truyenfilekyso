![image](https://github.com/user-attachments/assets/e7da1816-8e52-4e7c-8bbf-54eb7b54ce2a)
![image](https://github.com/user-attachments/assets/1bd54050-9b06-42c0-8ae0-de375e5ffffa)
![image](https://github.com/user-attachments/assets/899bd0bb-7b23-4851-a488-d810c6a9a171)
Tên: Ứng dụng Truyền File với Chữ Ký Số RSA
 Chức năng chính
Quản lý khóa RSA

Tạo cặp khóa RSA (Private key và Public key).

Hiển thị, tải về hoặc import khóa từ file .pem.

Người gửi (Ký nội dung)

Nhập văn bản hoặc chọn file cần ký.

Sử dụng private key để tạo chữ ký số (RSA-PSS).

Tạo gói dữ liệu .json chứa nội dung + chữ ký + hash.

Tải xuống gói file đã ký để gửi cho người nhận.

Người nhận (Xác thực chữ ký)

Tải gói file đã ký và public key người gửi.

Hệ thống xác minh chữ ký số và tính toàn vẹn của nội dung.

Hiển thị thông tin xác thực (hash, thời gian, trạng thái).

Cho phép tải lại file gốc nếu chữ ký hợp lệ.

Giao diện web thân thiện

Chia tab rõ ràng: Quản lý key, Người gửi, Người nhận.

Thiết kế đẹp mắt, chủ đề hiện đại.

Tương thích mọi trình duyệt, hỗ trợ responsive.

⚙ Công nghệ sử dụng
Thành phần	Công nghệ
Frontend (giao diện)	HTML, CSS, JavaScript
Backend (xử lý)	Python + Flask
Bảo mật	Thư viện cryptography của Python
Thuật toán	RSA (2048 bit), SHA-256, PSS Padding
Lưu trữ tạm	Biến storage trong Python (RAM)
Tệp đầu ra	Gói dữ liệu .json, khóa .pem
