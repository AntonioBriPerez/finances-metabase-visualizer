# Builder stage
FROM python:3.12 AS builder
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c 'from docling.document_converter import DocumentConverter; from docling.datamodel.base_models import InputFormat; from docling.document_converter import DocumentConverter, PdfFormatOption; from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode;  pipeline_options = PdfPipelineOptions(do_table_structure=True); pipeline_options.table_structure_options.mode = (TableFormerMode.ACCURATE); converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)}); result = converter.initialize_pipeline(InputFormat.PDF)'
# Final stage
FROM python:3.12
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY config.ini .
COPY .env .
COPY imap.py .
COPY ./src/ ./src

CMD ["python3", "imap.py"]