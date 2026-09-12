# Power BI Page 1 — bàn giao hiện trạng

Ngày bàn giao: 2026-09-13  
Phạm vi: **Page 1 — Executive Overview (chỉ Page 1)**. Không triển khai Page 2.

## 1. File làm việc chính

- PBIP: `outputs/Marketplace_Growth_Seller_Intelligence_Page1_V2/Marketplace_Growth_Seller_Intelligence_Page1_V2.pbip`
- Report definition: `Marketplace_Growth_Seller_Intelligence_Page1_V2.Report/report.json`
- Semantic model: `Marketplace_Growth_Seller_Intelligence_Page1_V2.SemanticModel/definition/`
- Governed release: `outputs/Marketplace_Growth_Seller_Intelligence_Page1/data/release_v3_final/`
- Plan tham chiếu: `PowerBI_Page1_Premium_Repair_Plan.md`

## 2. Những phần đã làm

### Nền tảng và bố cục

- Canvas Page 1 đã đặt đúng **1920 × 1080**, tỷ lệ 16:9.
- Đã dựng nền full-page và sidebar MarketLens; nội dung chính bắt đầu quanh x=245.
- Sidebar có Overview, Acquisition, Activation & Retention, Commercial, Customer Experience, Root Cause và Decision Center; Overview là trạng thái active.
- Đã bỏ object header thừa `Historical Oli...`.
- Header có Page 1 of 7, title và subtitle theo plan; có Date, Category và Seller State slicer.
- Các panel chính đã được bố trí theo hàng KPI / trend-concentration-insights / category-state-map-highlights.

### KPI và số liệu đã kiểm tra

Các KPI vẫn là measure lấy từ model, không hard-code theo ảnh tham chiếu. Kết quả runtime sau refresh:

| KPI | Giá trị kiểm tra |
|---|---:|
| GMV Proxy | R$13,591,643.70 |
| Orders | 98,666 |
| Active Sellers | 3,095 |
| Average Order Value | R$137.7541 |
| Late Delivery Rate | 8.1117% |
| Seller Gini | 0.791515 |
| Top 20% seller GMV share | 82.6917% |

Active Sellers 3,095 đang được tính từ dữ liệu seller quan sát được trong model, không gán số tĩnh.

### Chart native từ số liệu

Các chart chính không phải ảnh:

- `v016`: `lineClusteredColumnComboChart`, trục tháng `MMM yy`, hai measure `Trend GMV Proxy (R$M)` và `Trend Orders (K)`.
- `v017`: `lineChart` Lorenz, dùng `Lorenz[Cumulative % of Sellers]`, `Lorenz[Seller GMV Proxy]` và `Lorenz[Line of Equality]`.
- `v019`: native clustered bar cho Top 5 Categories.
- `v020`: native clustered bar cho Top 5 States.

Trong lượt sửa cuối, đã thêm hai measure:

```DAX
Trend GMV Proxy (R$M) =
IF (
    ISBLANK ( SELECTEDVALUE ( DimMonth[MonthStart] ) ),
    BLANK (),
    [GMV Proxy (R$M)]
)

Trend Orders (K) =
IF (
    ISBLANK ( SELECTEDVALUE ( DimMonth[MonthStart] ) ),
    BLANK (),
    [Orders (K)]
)
```

Hai measure này xử lý blank member phát sinh khi fact có các tháng không thuộc tập executive-complete. Sau refresh, trend không còn hiển thị dòng `(Blank)` và chỉ còn các tháng hợp lệ từ Oct 16 đến Aug 18.

### Seller concentration

- Bảng `Lorenz` đã được tạo theo seller rank tăng dần theo GMV.
- Đường Lorenz và line of equality đều là series native trong chart.
- Gini và Top-20 share được lấy từ `ConcentrationStats`.
- Có title cards và các tab visual `Lorenz Curve`, `Top Share`, `Gini Trend` để giữ đúng hướng thiết kế.

### Insights, highlights và hình ảnh

- Key Insights đã chuyển từ bảng nhỏ thành bốn card xếp dọc.
- Recent Highlights đã chuyển thành các signal row/card dùng Gini, Top-20 share, activation và late-review gap.
- Nền và seller map là hình ảnh source-backed/fallback; các chart định lượng vẫn native.
- Theo yêu cầu gần đây, chưa chèn bộ icon KPI mới; các ô/icon có thể bổ sung sau khi có asset cuối.

## 3. Các lỗi đã xử lý

- Đã xử lý lỗi model duplicate measure `GMV` bằng cách giữ tên measure duy nhất.
- Đã xử lý cyclic reference của `Geo` bằng measure `Seller Count` độc lập.
- Đã đổi các measure tổng category/state bị trùng tên sang tên riêng.
- Đã khôi phục theme collection để report render đúng visual containers.
- Đã sửa mapping trend để Orders là columns và GMV là line.
- Đã sửa blank month member ở trend bằng measure native nêu ở trên.
- Sau refresh gần nhất, Power BI không còn visible error dialog; kiểm tra helper trả về `fixButtons=0`.

## 4. Những phần còn thiếu / cần làm tiếp

Đây là các gap còn lại so với Definition of Done trong plan, không che giấu:

1. **Reset Filters bookmark/button**: đã thử tạo trong Desktop nhưng thao tác UI chưa được ghi bền vào `report.json`; file hiện vẫn có card chữ `Reset Filters`, chưa có action button được lưu chắc chắn. Cần tạo lại và bấm Save trong Desktop, sau đó mở lại để xác minh.
2. **Map**: `v021` hiện là `image` map fallback source-backed vì native map bị hạn chế trong Desktop hiện tại. Bảng `Geo` vẫn có dữ liệu để thay bằng Shape Map/Azure Maps khi bật được visual map.
3. **KPI icons**: chưa dùng asset icon cuối theo yêu cầu của bạn; file `kpi_icons.png` trên đĩa không được tham chiếu vào report hiện tại.
4. **Visual QA cuối**: cần chụp clean view sau khi đóng Filters/Visualizations/Data panes và Fit to Page; ảnh kiểm tra hiện tại chủ yếu chứng minh report đã render và data đã nạp.
5. **Portability**: Power Query trong TMDL đang trỏ tới đường dẫn tuyệt đối trên máy này. Nếu clone sang máy khác, cần đổi các `File.Contents(...)` sang đường dẫn mới.

## 5. Cách mở lại và làm tiếp

1. Mở file `.pbip` trong thư mục `Marketplace_Growth_Seller_Intelligence_Page1_V2`.
2. Nếu xuất hiện banner `Refresh now`, bấm **một lần** và chờ hoàn tất.
3. Kiểm tra KPI phải quanh các giá trị trong bảng trên; Active Sellers phải là 3,095 ở mặc định All.
4. Chọn View → Fit to Page, đóng ba pane authoring và chụp riêng cửa sổ Power BI.
5. Làm tiếp Reset Filters bookmark/button trước; sau đó mới thay map native hoặc chèn icon.

Không chạy nhiều refresh đồng thời. Banner `Some of the tables have incomplete or no data` có thể xuất hiện ở lần mở đầu trước khi import cache được nạp; sau refresh phải biến mất khỏi trạng thái lỗi thực tế.

## 6. Danh sách model tables chính

`bi_fact_marketplace_item`, `Category`, `CategoryTop5`, `ConcentrationStats`, `DimCategory`, `DimMonth`, `DimState`, `Geo`, `Highlights`, `Insights`, `Lorenz`, `Monthly`, `Pillars`, `SellerLifetime`, `Snapshot`, `StateTop5`.

Toàn bộ DAX measure và Power Query expression nằm trực tiếp trong các file `.tmdl` của thư mục semantic model; file `DAX_MEASURES.dax` trong gói bàn giao là bản trích xuất dễ đọc.

