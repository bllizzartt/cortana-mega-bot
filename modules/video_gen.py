"""
Video Generation Module - Seedance API integration.
Handles AI video generation from photos.
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import httpx

from config import get_config

logger = logging.getLogger(__name__)


class VideoGenerator:
    """Video generation using Seedance API."""

    def __init__(self):
        self.config = get_config()
        self.mock_mode = self.config.mock_mode

    async def generate_video(
        self,
        user_id: int,
        prompt: str,
        photos: List[str],
        job_id: str = None
    ) -> Dict:
        """
        Generate an AI video from photos.
        
        Args:
            user_id: Telegram user ID
            prompt: Video description prompt
            photos: List of photo file paths
            job_id: Optional job ID for tracking
            
        Returns:
            Dict with job_id, status, and video_path/error
        """
        if job_id is None:
            job_id = f"vid_{uuid.uuid4().hex[:12]}"
        
        logger.info(f"Starting video generation job {job_id} for user {user_id}")
        
        if self.mock_mode:
            return await self._mock_generate(job_id, prompt, photos)
        
        return await self._real_generate(job_id, prompt, photos)

    async def _mock_generate(
        self,
        job_id: str,
        prompt: str,
        photos: List[str]
    ) -> Dict:
        """Mock video generation for testing."""
        logger.info(f"Mock mode: Simulating video generation for {job_id}")
        
        # Simulate processing time
        await asyncio.sleep(2)
        
        # Create a placeholder video path
        videos_dir = Path(self.config.video_storage_path)
        videos_dir.mkdir(exist_ok=True)
        
        video_filename = f"{job_id}.mp4"
        video_path = videos_dir / video_filename
        
        # Create empty placeholder file
        video_path.touch()
        
        return {
            "job_id": job_id,
            "status": "completed",
            "video_path": str(video_path),
            "prompt": prompt,
            "message": "Video generated (mock mode - until Feb 24)"
        }

    async def _real_generate(
        self,
        job_id: str,
        prompt: str,
        photos: List[str]
    ) -> Dict:
        """Real video generation using Seedance API."""
        api_key = self.config.seedance_api_key
        api_url = self.config.seedance_api_url
        
        if not api_key:
            return {
                "job_id": job_id,
                "status": "failed",
                "error": "Seedance API key not configured"
            }
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Step 1: Upload photos
                uploaded_photos = []
                for photo_path in photos:
                    with open(photo_path, "rb") as f:
                        response = await client.post(
                            f"{api_url}/upload",
                            files={"file": f},
                            headers={"Authorization": f"Bearer {api_key}"}
                        )
                        if response.status_code == 200:
                            uploaded_photos.append(response.json()["file_id"])
                
                if not uploaded_photos:
                    return {
                        "job_id": job_id,
                        "status": "failed",
                        "error": "Failed to upload photos"
                    }
                
                # Step 2: Submit generation job
                job_response = await client.post(
                    f"{api_url}/generate",
                    json={
                        "prompt": prompt,
                        "reference_images": uploaded_photos,
                        "options": {
                            "duration": 5,
                            "resolution": "1080p"
                        }
                    },
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                
                if job_response.status_code != 200:
                    return {
                        "job_id": job_id,
                        "status": "failed",
                        "error": job_response.text
                    }
                
                remote_job_id = job_response.json()["job_id"]
                
                # Step 3: Poll for completion
                result = await self._poll_for_completion(
                    client, api_key, api_url, remote_job_id
                )
                
                if result["status"] == "completed":
                    # Download video
                    video_url = result["video_url"]
                    videos_dir = Path(self.config.video_storage_path)
                    videos_dir.mkdir(exist_ok=True)
                    
                    video_filename = f"{job_id}.mp4"
                    video_path = videos_dir / video_filename
                    
                    video_response = await client.get(video_url)
                    video_path.write_bytes(video_response.content)
                    
                    result["video_path"] = str(video_path)
                
                return result
                
        except Exception as e:
            logger.error(f"Video generation error: {e}")
            return {
                "job_id": job_id,
                "status": "failed",
                "error": str(e)
            }

    async def _poll_for_completion(
        self,
        client: httpx.AsyncClient,
        api_key: str,
        api_url: str,
        remote_job_id: str,
        max_wait: int = 300
    ) -> Dict:
        """Poll Seedance API for job completion."""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < max_wait:
            response = await client.get(
                f"{api_url}/jobs/{remote_job_id}",
                headers={"Authorization": f"Bearer {api_key}"}
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "pending")
                
                if status == "completed":
                    return {
                        "job_id": remote_job_id,
                        "status": "completed",
                        "video_url": data.get("video_url")
                    }
                elif status == "failed":
                    return {
                        "job_id": remote_job_id,
                        "status": "failed",
                        "error": data.get("error", "Unknown error")
                    }
            
            await asyncio.sleep(5)
        
        return {
            "job_id": remote_job_id,
            "status": "failed",
            "error": "Timeout waiting for video generation"
        }


# Video generation state management
class VideoSession:
    """Manages video generation session state."""
    
    def __init__(self):
        self.state = "idle"  # idle, collecting_photos, waiting_for_prompt, processing
        self.photos = []
        self.prompt = ""
    
    def reset(self):
        """Reset session to initial state."""
        self.state = "idle"
        self.photos = []
        self.prompt = ""
    
    def add_photo(self, photo_path: str) -> bool:
        """Add a photo to the session."""
        if self.state == "idle":
            self.state = "collecting_photos"
        if self.state == "collecting_photos":
            if len(self.photos) < 4:
                self.photos.append(photo_path)
                return True
        return False
    
    def set_prompt(self, prompt: str):
        """Set the generation prompt."""
        self.prompt = prompt
        self.state = "waiting_for_prompt"
    
    def start_processing(self):
        """Mark as processing."""
        self.state = "processing"
    
    def is_ready(self) -> bool:
        """Check if ready to generate."""
        return len(self.photos) >= 1 and self.prompt and self.state == "waiting_for_prompt"


def create_video_session() -> VideoSession:
    """Create a new video session."""
    return VideoSession()


# Template prompts for video generation
VIDEO_TEMPLATES = {
    "dance": "Professional dance video, smooth movements, energetic atmosphere",
    "walk": "Cinematic walking shot, natural lighting, urban environment",
    "nature": "Nature documentary style, breathtaking landscapes, peaceful",
    "action": "Action movie style, dynamic camera movements, intense atmosphere",
    "fashion": "Fashion runway walk, studio lighting, high-end aesthetic",
    "travel": "Travel vlog style, adventure, exploration, scenic locations",
    "celebration": "Celebration party, joyful moments, festive atmosphere",
    "workout": "Fitness workout video, dynamic energy, gym environment",
}
