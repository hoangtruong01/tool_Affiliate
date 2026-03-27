# 📖 Hướng Dẫn Vận Hành Hệ Thống (Operator Guide)

Tài liệu này hướng dẫn chi tiết quy trình làm việc trên công cụ Tự động hóa Video TikTok Affiliate, từ bước tạo nội dung đến khi phân tích hiệu quả.

---

## 🔄 Luồng Công Việc Tổng Quan (End-to-End Workflow)

Quy trình chuẩn gồm 6 bước chính:

### Bước 1: Quản lý Sản phẩm & Yêu cầu Script
Hệ thống sẽ tự động tạo script hàng ngày (9:00 AM UTC) cho các sản phẩm đang hoạt động (**Active**).
- **Người dùng cần làm**: Đảm bảo các sản phẩm tiềm năng đã được thêm vào mục **Products** và đặt trạng thái là **Active**.

### Bước 2: Phê duyệt Script (Script Approval)
Truy cập: `Giao diện Dashboard` -> `Approvals` (Tab Scripts)
- Kiểm tra nội dung script AI đã tạo (Hook, nội dung, lời kêu gọi hành động).
- **Thao tác**: Click **Approve** (Đồng ý) hoặc **Reject** (Từ chối). Script được duyệt mới có thể chuyển sang bước dựng video.

### Bước 3: Khởi tạo Tiến trình Dựng Video (Video Rendering)
Truy cập: `Giao diện Video Jobs` -> Nút **New Render Job**
- **Chọn Script**: Chọn script đã được phê duyệt ở Bước 2.
- **Chọn Hình ảnh**: Chọn các hình ảnh sản phẩm tương ứng từ thư viện **Assets**.
- **Thao tác**: Click **Start Rendering Pipeline**. Hệ thống sẽ đưa vào hàng đợi và FFmpeg sẽ tự động dựng video.

### Bước 4: Kiểm tra & Phê duyệt Video
Truy cập: `Giao diện Approvals` -> `Tab Video Jobs`
- Xem video bản thô đã dựng.
- **Thao tác**:
    - **Play**: Xem thử video.
    - **Approve**: Nếu video đạt chất lượng.
    - **Reject**: Nếu cần dựng lại (sẽ cho phép retry).
- **Lấy Asset Bundle**: Sau khi Approve, click vào Job để copy **Caption**, **Hashtags** và các thông tin đi kèm để chuẩn bị đăng.

### Bước 5: Đăng bài & Theo dõi (Publish Tracking)
Đây là bước **Bán thủ công** (Semi-manual).
- **Người dùng cần làm**: Tải video về máy, đăng lên TikTok/Reels/Shorts.
- **Cập nhật hệ thống**: Quay lại trang **Jobs**, tìm video vừa đăng, click biểu tượng **Share** (Track Publishing).
    - Dán **Link bài viết (Post URL)**.
    - Chọn nền tảng (TikTok/Internal...).
    - Lưu lại để chuyển trạng thái sang **Published**.

### Bước 6: Nhập Chỉ số Hiệu quả & Học máy (Learning Loop)
Sau 24h - 48h khi bài đăng có chỉ số.
- **Thao tác**: Click biểu tượng biểu đồ (**Add Metrics**) trên video đã đăng.
- **Nhập dữ liệu**: Lượt xem (Views), CTR, Chuyển đổi (Conversions) và **Đánh giá của bạn (1-5 sao)**.
- **Kết quả**: Hệ thống sẽ tổng hợp tại trang **Learning & Reports** để cho bạn biết:
    - Sản phẩm nào đang hái ra tiền (**Top Products**).
    - Câu Hook nào bắt trend tốt nhất (**Top Hooks**).
    - Những video nào cần tối ưu lại hoặc nên dừng bỏ.

---

## 📊 Giải thích các Trạng thái (Status)

| Trạng thái | Ý nghĩa |
|:---|:---|
| **Queued** | Đang chờ đến lượt xử lý. |
| **Processing** | Hệ thống đang dựng video (FFmpeg đang chạy). |
| **Needs Review** | Video đã dựng xong, chờ bạn xem và duyệt. |
| **Approved** | Video đã sẵn sang để tải về và đăng máy. |
| **Published** | Video đã được bạn xác nhận đã đăng lên mạng xã hội. |
| **Failed** | Gặp lỗi trong quá trình dựng (do thiếu file, lỗi AI...). Hãy click **Retry**. |

---

## 💡 Mẹo cho Người vận hành
1. **Kiểm tra Bottlenecks**: Nếu thấy video ở trạng thái `Processing` quá 30 phút, hãy vào `Reports` xem mục **Stuck Jobs** để xử lý.
2. **Asset Bundle**: Luôn dùng tính năng Copy Asset Bundle để đảm bảo SEO bài viết đồng nhất.
3. **Thường xuyên xem Learning**: Đừng đăng mù quáng, hãy xem Dashboard Learning để biết góc quay (Angle) nào đang hiệu quả thục sự.

---
*Cập nhật lần cuối: 27/03/2026*
