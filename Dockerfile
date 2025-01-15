# Use the official AWS Lambda Python 3.9 base image
FROM public.ecr.aws/lambda/python:3.9

# Copy function code
COPY handler.py requirements.txt ./

# Install dependencies locally into the container
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the command to your handler name (i.e., file_name.function_name)
CMD [ "handler.lambda_handler" ]
