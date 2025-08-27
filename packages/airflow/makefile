# Makefile

PYTHON_VERSION := $(shell python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
AIRFLOW_VERSION := 3.0.4
CONSTRAINT_URL := https://raw.githubusercontent.com/apache/airflow/constraints-$(AIRFLOW_VERSION)/constraints-$(PYTHON_VERSION).txt

install: constraints.txt
	uv pip install -c constraints.txt .

# Download Airflow constraint file
constraints.txt:
	curl -sSL $(CONSTRAINT_URL) -o constraints.txt

clean:
	rm -f constraints.txt
