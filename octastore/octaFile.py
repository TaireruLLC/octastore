import requests
import base64
import io
import tempfile
import wave
import pyaudio
import cv2
import numpy as np
from moviepy import VideoFileClip
from typing import Optional, Dict

class OctaFile:
    """
    OctaFile allows streaming of remote files stored in a GitHub repository
    without downloading them.
    """

    def __init__(self, repo_owner: str, repo_name: str, token: str, branch: Optional[str] = 'main'):
        self.repo_owner: str = repo_owner
        self.repo_name: str = repo_name
        self.token: str = token
        self.branch: Optional[str] = branch
        self.headers: Dict[str, str] = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3.raw"
        }

    def _get_file_url(self, path: str) -> str:
        """Constructs the GitHub API URL for a given file path."""
        return f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/{path}?ref={self.branch}"

    def _fetch_file(self, path: str) -> bytes:
        """Fetches a file's content as bytes from GitHub without downloading."""
        url: str = self._get_file_url(path)
        response: requests.Response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return base64.b64decode(response.json()["content"])  # Decode base64 content
        else:
            raise Exception(f"Error fetching file: {response.status_code} - {response.text}")

    def get_file(self, remote_path: str) -> io.BytesIO:
        """
        Fetches any file from GitHub and returns it as an in-memory stream.

        Args:
            remote_path (str): The path to the file in the GitHub repo.

        Returns:
            io.BytesIO: The file as a stream.
        """
        file_bytes: bytes = self._fetch_file(remote_path)
        return io.BytesIO(file_bytes)

    def play_audio(self, remote_path: str) -> None:
        """
        Streams and plays an audio file (WAV format) from GitHub without downloading.

        Args:
            remote_path (str): Path to the audio file in the repository.
        """
        try:
            audio_stream: io.BytesIO = self.get_file(remote_path)
            wf: wave.Wave_read = wave.open(audio_stream, 'rb')

            p: pyaudio.PyAudio = pyaudio.PyAudio()
            stream: pyaudio.Stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            data: bytes = wf.readframes(1024)
            while data:
                stream.write(data)
                data = wf.readframes(1024)

            stream.stop_stream()
            stream.close()
            p.terminate()

            print(f"Audio played successfully from {remote_path}")

        except Exception as e:
            print(f"Error playing audio: {e}")

    def play_video(self, remote_path: str) -> None:
        """
        Streams and plays a video file (MP4 format) from GitHub without downloading.

        Args:
            remote_path (str): Path to the video file in the repository.
        """
        try:
            video_stream: io.BytesIO = self.get_file(remote_path)

            # Use a temporary file to store video data
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
                temp_video.write(video_stream.read())
                temp_video_path: str = temp_video.name  # Store the temp file path

            # Open and play the video
            cap: cv2.VideoCapture = cv2.VideoCapture(temp_video_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow("Video Stream", frame)
                if cv2.waitKey(25) & 0xFF == ord("q"):
                    break

            cap.release()
            cv2.destroyAllWindows()

            print(f"Video played successfully from {remote_path}")

        except Exception as e:
            print(f"Error playing video: {e}")