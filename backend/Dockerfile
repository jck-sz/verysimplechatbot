# Lambda-compatible Python base image
FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/main.py main.py
  
# Set the Lambda handler
CMD ["main.handler"]
