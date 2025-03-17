FROM docker.arvancloud.ir/python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install tzdata package
RUN apt-get update && apt-get install -y tzdata

# Set timezone to Tehran
RUN ln -sf /usr/share/zoneinfo/Asia/Tehran /etc/localtime
ENV TZ=Asia/Tehran

WORKDIR /app

RUN pip config --user set global.index https://pypi.tuna.tsinghua.edu.cn/simple &&  \
    pip config --user set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple &&  \
    pip config --user set global.trusted-host pypi.tuna.tsinghua.edu.cn

RUN apt-get update && \
    apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
