### Note: 

---

This folder contains the source code for data ingestion and processing. It includes loading data, splitting it into chunks, generating vector embeddings, and storing them in a vectorstore.

Files prefixed with "template" are consolidated versions of data_loader.py and process.py. They serve as interchangeable templates for vector embedding pipelines.
To use a template, simply replace references to data_loader and process in your main script with the desired template.py file.

These templates are designed to make it easy to switch between different vectorstore implementations—whether you're embedding text offline, using models hosted on the web, or relying on serverless APIs.

---