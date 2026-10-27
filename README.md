# ArgoCD Lab — FastAPI Backend

Backend đơn giản để làm lab triển khai, gồm app FastAPI, Dockerfile và CI build/push image.

## API

| Endpoint | Chức năng |
| --- | --- |
| `GET /` | Trả lời chào và version |
| `GET /health` | Kiểm tra app hoạt động, trả về `{"status": "ok"}` |
| `GET /info` | Xem tên app, version, môi trường và hostname |
| `GET /docs` | Swagger UI để thử API |

## Chạy local

Yêu cầu [uv](https://docs.astral.sh/uv/getting-started/installation/). Chạy từ thư mục gốc repo:

```bash
cd backend
uv sync --locked
uv run --locked uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

`uv` tự tạo `.venv` và tải Python 3.13 nếu máy chưa có, theo `.python-version`.
Dependencies được quản lý bằng `pyproject.toml` và khóa phiên bản trong `uv.lock`.
Mở <http://localhost:8000/docs> để thử API. Dừng server bằng `Ctrl+C`.

## Chạy bằng Docker

Yêu cầu Docker đang chạy. Build từ thư mục gốc repo:

```bash
docker build -t argocd-lab-api:1.0.0 ./backend
docker run --rm --name argocd-lab-api -p 127.0.0.1:8000:8000 \
  -e APP_ENV=dev \
  -e APP_VERSION=1.0.0 \
  argocd-lab-api:1.0.0
```

Mở terminal khác để kiểm tra:

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/info
```

Dockerfile dùng `uv sync --locked` để cài đúng dependencies từ `uv.lock`.
Container chạy bằng user thường và có health check gọi `/health`.

## GitHub Actions: Build & Push

Workflow `.github/workflows/backend-ci.yml` chạy khi có push vào nhánh `release`,
bao gồm push do merge pull request. PR đang mở và push vào các nhánh khác không kích hoạt CI.
Muốn chỉ cho phép thay đổi qua merge PR, bật branch protection/ruleset cho `release`
trên GitHub và yêu cầu pull request trước khi merge.

Luồng hiện tại:

```text
Merge PR vào release → Build Docker bằng uv → Push image lên GHCR
```

Image có tên `ghcr.io/<owner>/<repo>:sha-<full-commit-sha>` (owner và repo viết thường).
Với repo này: `ghcr.io/haourgot123/argocd:sha-<full-commit-sha>`.
Mỗi commit dùng tag riêng để chọn chính xác bản triển khai. Image hỗ trợ cả `linux/amd64`
và `linux/arm64`, dùng được với máy Intel/AMD và Apple Silicon.

Workflow đăng nhập GHCR bằng `GITHUB_TOKEN` do GitHub cấp sẵn, với quyền `packages: write`;
không cần tạo thêm registry secret. Xem tiến trình ở tab **Actions** và image ở **Packages**.
Workflow phải có trong nhánh `release` để được kích hoạt khi nhánh này thay đổi.
Bước cập nhật manifest và deploy bằng ArgoCD sẽ làm sau.

## Biến môi trường

| Biến | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `APP_VERSION` | `1.0.0` | Version trả về qua API và hiển thị trong Swagger |
| `APP_ENV` | `local` | Môi trường đang chạy |
| `APP_MESSAGE` | `Hello from FastAPI!` | Lời chào ở endpoint `/` |

App đọc biến môi trường khi khởi động; cần khởi động lại sau khi thay đổi.
Tag Docker image và `APP_VERSION` được đặt riêng; khi tạo bản mới, cập nhật cả hai để dễ theo dõi.
