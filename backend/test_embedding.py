from app.rag.embedding_service import EmbeddingService


def main() -> None:
    service = EmbeddingService()
    embedding = service.create_embedding(
        "SOAP modernization using REST APIs"
    )

    print(f"Embedding dimension: {len(embedding)}")
    print("Sample:")
    print(embedding[:5])


if __name__ == "__main__":
    main()
