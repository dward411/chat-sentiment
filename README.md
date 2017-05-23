# Chat Sentiment

Chat Sentiment are sentiment analysis tools.

## Installation

### Conda

For complete documentation, refer to https://conda.io/. Otherwise, for macOS, continue reading.

### macOS - Python 2.7

Accept defaults when prompted,

```
curl "https://repo.continuum.io/miniconda/Miniconda2-latest-MacOSX-x86_64.sh" -o "Miniconda2-latest-MacOSX-x86_64.sh"
bash Miniconda3-latest-MacOSX-x86_64.sh
```

Restart your Terminal.

### Python Environment

```
conda create --name chat-sentiment python=2.7
conda install --name chat-sentiment pandas
conda install --name chat-sentiment xlrd
conda install --name chat-sentiment openpyxl
```

### Download

```
git clone https://github.com/dward411/chat-sentiment.git
```

### Configure

1. Copy lookup files /chat-sentiment/data/lookup
2. Copy chats.xlsx /chat-sentiment/data/raw

NOTE: These files are excluded from Github. Examples will be provided in near future...

### Test Run

```
source activate chat-sentiment
cd chat-sentiment
python load.py
```
