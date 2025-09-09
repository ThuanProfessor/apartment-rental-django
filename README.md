# 🏠 Website Quản Lý Cho Thuê Căn Hộ

## 📌 Giới thiệu
Đây là dự án cá nhân với mục tiêu xây dựng một nền tảng website quản lý cho thuê căn hộ/phòng trọ.  
Hệ thống cho phép người cho thuê đăng tin và người thuê có thể tìm kiếm, xem thông tin chi tiết, hình ảnh, vị trí bản đồ và liên hệ trực tiếp với chủ nhà.  
Ngoài ra, website cung cấp giao diện quản trị cho admin để quản lý toàn bộ hệ thống một cách thuận tiện.

---

## 🎯 Mục tiêu
- Xây dựng website hỗ trợ **cho thuê căn hộ/phòng** trực tuyến.  
- Hỗ trợ **người thuê** tìm kiếm, lọc và xem chi tiết căn hộ.  
- Cho phép **người cho thuê** quản lý danh sách bài đăng dễ dàng.  
- **Admin** quản lý toàn bộ hệ thống thông qua **Django Admin Site**.  
- Đảm bảo **bảo mật và phân quyền** người dùng.  

---

## 🛠️ Công nghệ sử dụng
- **Backend**: Django + Django Rest Framework  
- **Frontend**: ReactJS  
- **Cơ sở dữ liệu**: MySQL  
- **Triển khai**: PythonAnywhere / Railway / Render  
- **API bên thứ 3**: Google Maps API (hiển thị bản đồ)  
- **Realtime Chat**: Firebase (tích hợp trò chuyện giữa người thuê và người cho thuê)  
- **Xác thực & Bảo mật**: OAuth2
  <img width="1270" height="679" alt="image" src="https://github.com/user-attachments/assets/42ee8acf-8f9d-4713-b103-7e2ae7e4de00" />


---

## ⚙️ Chức năng chính

### 👤 Người dùng
- **Đăng ký / Đăng nhập** (Người thuê, Người cho thuê, Admin).  
- **Quản lý tài khoản cá nhân**: cập nhật tên, ảnh đại diện, số điện thoại,…  
- **Xem chi tiết bài đăng**: mô tả, hình ảnh, bản đồ Google Maps, thông tin liên hệ.  
- **Liên hệ chủ nhà**: qua thông tin liên hệ hoặc chat realtime.  

### 🏘️ Người cho thuê
- **Đăng bài cho thuê**: tiêu đề, mô tả, hình ảnh, giá thuê, vị trí, tiện ích,…  
- **Quản lý bài đăng**: thêm, sửa, xóa, ẩn/hiện khi phòng đã cho thuê.  

### 🔍 Người thuê
- **Tìm kiếm** theo từ khóa: địa chỉ, loại phòng,…  
- **Lọc bài đăng** theo nhiều tiêu chí: giá thuê, diện tích, khu vực, tiện ích,…  

### 🛡️ Quản trị viên (Admin)
- Quản lý toàn bộ **người dùng** và **bài đăng** qua Django Admin.  
- Khóa tài khoản / xóa bài đăng vi phạm.  
- **Thống kê hệ thống**: vẽ biểu đồ tổng quan.

- 

---

## 📊 Kiến trúc hệ thống
![ReactJS](https://github.com/user-attachments/assets/fa871d99-dcb9-4385-977e-ee0602b2105c)


---

## 🚀 Cài đặt & Chạy thử

### 1. Clone project
```bash
git clone https://github.com/ThuanProfessor/apartment-rental-django.git
cd apartment-rental-django
```
### 2. Khởi tạo môi trường ảo
```bash
python -m venv thuanvenv
```
### 3. Kích hoạt môi trường ảo - venv
```bash
source thuanvenv/bin/activate   # (Windows: venv\Scripts\activate)
```
### 4. Cài các thư viện cần thiết
```bash
pip install -r requirements.txt
```
### 5. Khởi tạo Models xuống database
```bash
python manage.py migrate
python manage.py runserver
```
## 🔒Bảo mật 
- Sử dụng **OAuth2** cho xác thực và phân quyền
- Mã hóa mật khẩu người dùng bằng bcrypt/argon2 (Django default).
- Chống SQL Injection, CSRF, XSS.
## 📈 Kết quả mong đợi
- Nền tảng website hoàn chỉnh, đáp ứng nhu cầu thuê căn hộ/phòng.
- Giao diện thân thiện, dễ sử dụng cho cả người thuê và người cho thuê.
- Hệ thống bảo mật tốt, quản lý dữ liệu hiệu quả
## 👥 Contributors

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/thuanprofessor">
        <img src="https://github.com/thuanprofessor.png" width="100" height="100" style="border-radius: 50%; object-fit: cover;"><br>
        <sub><b>Thuan Professor</b></sub>
      </a>
    </td>
  </tr>
</table>

## 📝 License

This project is licensed under multiple open source licenses:

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://opensource.org/licenses/)
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](http://www.gnu.org/licenses/agpl-3.0)

## 📞 Support

For support and inquiries, please contact:
- 📧 Email: [hoangthuandev04@gmail.com](mailto:hoangthuandev04@gmail.com)
- 💬 Issues: [GitHub Issues](https://github.com/ThuanProfessor/apartment-retal-django/issues)

