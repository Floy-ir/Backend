FROM docker.arvancloud.ir/python:3.10-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip config --user set global.index https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config --user set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip config --user set global.trusted-host pypi.tuna.tsinghua.edu.cn

WORKDIR /app

RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

FROM docker.arvancloud.ir/python:3.10-slim

ENV TZ=Asia/Tehran
ENV PATH="/venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Tehran /etc/localtime && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /venv /venv
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
