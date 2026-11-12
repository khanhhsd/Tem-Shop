class SpeechService:
    """Accept browser-transcribed text and route it through the common query service."""

    def __init__(self, query_service=None):
        self.query_service = query_service

    @staticmethod
    def transcribe(transcript):
        return str(transcript or "").strip()

    def search(self, transcript, filters=None, customer_id=None):
        if self.query_service is None:
            raise RuntimeError("SpeechService requires a QueryService to run searches.")
        return self.query_service.voice_query(
            self.transcribe(transcript), filters, customer_id
        )
