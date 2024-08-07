FROM ubuntu:latest

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"


# Install required dependencies
RUN apt-get update && \
    apt-get install -y psmisc bsdmainutils cron && \
    apt-get install -y bash sudo python3 python3-pip python3-venv && \
    apt-get install -y imagemagick dnsutils git tree && \
    apt-get install -y net-tools iputils-ping coreutils && \
    apt-get install -y curl cpio jq vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install libreoffice
RUN apt-get update && \
    apt-get install -y libreoffice && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Tessaract
RUN apt-get update && \
    apt-get install -y tesseract-ocr && \
    apt-get install -y libtesseract-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# Install Miniconda on x86 or ARM platforms
RUN arch=$(uname -m) && \
    if [ "$arch" = "x86_64" ]; then \
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"; \
    elif [ "$arch" = "aarch64" ]; then \
    MINICONDA_URL="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh"; \
    else \
    echo "Unsupported architecture: $arch"; \
    exit 1; \
    fi && \
    curl -o miniconda.sh $MINICONDA_URL && \
    mkdir -p /root/.conda && \
    bash miniconda.sh -b -p /root/miniconda3 && \
    rm -f miniconda.sh

RUN conda --version

# Install dependencies
COPY ./docker/requirements.txt /
COPY ./docker/setup_py.sh /
RUN chmod +x /setup_py.sh
RUN sh ./setup_py.sh
RUN rm /setup_py.sh /requirements.txt

# Create custom file structure
COPY ./gemini_key.txt /
COPY ./qwen_key.txt /

# Commit custom file system to determine diffs
COPY ./docker/docker.gitignore /
RUN mv docker.gitignore .gitignore
RUN git config --global user.email "office_agent_bench@universityofcalifornia.edu"
RUN git config --global user.name "office_agent_bench@universityofcalifornia.edu"
RUN git init
RUN git add -A
RUN git commit -m 'initial commit'

WORKDIR /
