class AudioProcessingError(Exception):
    """Base exception for audio processing errors."""
    pass

class LargeFileError(AudioProcessingError):
    """Exception raised for audio files that are too large."""
    pass

class UnsupportedAudioFormatError(AudioProcessingError):
    """Exception raised for unsupported audio formats."""
    pass

class UnsupportedAudioCodecError(AudioProcessingError):
    """Exception raised for unsupported audio codecs."""
    pass

class CorruptAudioError(AudioProcessingError):
    """Exception raised for corrupt audio files."""
    pass

class OutputProcessingError(Exception):
    """Base exception for output processing errors."""
    pass

class InvalidOutputFormatError(OutputProcessingError):
    """Exception raised for invalid output format."""
    pass
