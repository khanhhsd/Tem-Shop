from pathlib import Path


class ImageService:
    def __init__(self, query_service, file_storage, vector_index, static_directory):
        self.query_service = query_service
        self.file_storage = file_storage
        self.vector_index = vector_index
        self.static_directory = Path(static_directory)

    def search(self, uploaded_file, filters=None, customer_id=None):
        saved_path = self.file_storage.save_image(uploaded_file)
        image_url = str(saved_path.relative_to(self.static_directory)).replace("\\", "/")
        feature_vector = self.vector_index.extract(saved_path)
        result = self.query_service.image_query(
            image_url, feature_vector, filters, customer_id
        )
        return result, image_url
