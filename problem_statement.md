Problem Statement: Build a Retrieval-Augmented Generation (RAG) Application Using Azure and FastAPI.
 
Objective
Build a Retrieval-Augmented Generation (RAG) application using Azure services & FastAPI framework. Demonstrate your skills in document processing, vector store setup, LLM integration, and end-to-end question-answering pipelines. The RAG system should be able to answer queries based on uploaded documents.

Finally, create an API which ingests the files and another API which performs Q&A based on the document. The interaction with the documents needs to be shown via a app(free to use react,streamlit)
 
Prerequisites
Before starting, ensure you have the following:
•	Access to Azure services such as AI foundry, search index etc
•	Sample document for ingestion. Please refer to the attached documents within this folder. 
Assessment Tasks
1. Document Loading
Ingest documents of different types for RAG processing:
•	Load documents from local.
•	Handle basic preprocessing like removing unnecessary whitespace or metadata.
 
2. Text Splitting
Perform chunking and splitting of the data:
•	Chunk the processed data, ensure overlapping is applied for context preservation.
•	Experiment with chunk sizes and overlap values for optimal performance.
 
3. Vector DB Setup
Store document embeddings in Azure search index:
•	Create an index called “final_assessment” in the Azure portal and add the necessary metadata of your choice.
•	Generate embeddings for all document chunks using an LLM embedding model.
•	Upload the embeddings into the index and using for retrieval later. 
 
4. Retriever
Implement a retriever to fetch relevant document chunks based on a query.
•	Configure the retriever to query the vector db efficiently.
•	Test retrieval with sample queries and ensure relevant chunks are returned.
 
5. Prompt Template
Create a prompt template for the LLM to generate answers.
•	Use retrieved document chunks as context.
•	Include a clear instruction template for the LLM, e.g., “Answer the user’s query using the following context.”
•	Ensure the prompt is structured to reduce hallucinations, provide examples if required.
 
6. LLM Integration
Integrate the prompt template with an LLM for answer generation.
•	Pass the context from retrieved chunks and the user query to the LLM.
•	Generate coherent, accurate answers based on the documents.
•	Prepare a fallback if the document doesn’t contain the answer to the query. Create a template for the same, e.g., “I couldn’t find the answer to your query, however according to my knowledge … ”
 
7. End-to-End Q&A Pipeline and execute it on a app
Build a seamless pipeline from document ingestion to query answering.
•	Integrate all components: Ingestion → chunking → azure search index → retriever → Prompt → LLM → Output.
•	Test the pipeline with multiple sample queries.
•	Ensure the system returns contextually accurate answers.

