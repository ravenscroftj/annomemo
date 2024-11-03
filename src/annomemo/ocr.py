"""Code for execution of OCR functions"""

from abc import ABC

import mimetypes
import base64
import aiohttp
import litellm
import os



from loguru import logger

TRANSCRIBE_PROMPT = """Transcribe the hand written notes in the attached image and present them as markdown inside a fence like so

```markdown
<Content>
```

If any words or letters are unclear, denote them  with a '?<word>?'. For example if you were not sure whether a word is blow or blew you would transcribe it as '?blow?'
"""


class ImageProcessException(Exception):
    """Base exception thrown by image processing routines"""

    pass

class ImageProcessorConfigurationException(ImageProcessException):
    """Thrown if the image processor is misconfigured after call to validate()"""


class ImageProcessor(ABC):
    """Base class for image processor"""

    def validate(self):
        """Check if all required params are present in environment, throws exception if not present"""

    async def process_image(self, image_url: str) -> str:
        """Process image and return text"""
        raise NotImplementedError
    

def get_image_processor() -> ImageProcessor:
    """Get image processor based on environment variable"""
    processor = os.getenv('IMAGE_PROCESSOR', 'litellm')
    if not processor or processor == 'qwenv2':
        return QwenV2ImageProcessor()
    elif processor == 'litellm':
        return LiteLLMImageProcessor()
    else:
        raise ImageProcessException(f'Invalid image processor {processor}')

class QwenV2ImageProcessor(ImageProcessor):
    """Implementation of image processor using QwenV2 for local VLM inference"""

    def validate(self):
        pass

    async def process_image(self, image_url: str) -> str:
        pass


class LiteLLMImageProcessor(ImageProcessor):
    """Implementation of image processor using LiteLLM for remote VLM inference"""

    def validate(self):
        logger.info("Checking model params")
        model_name = os.getenv("MODEL", "openai/gpt-4o")
        result = litellm.validate_environment(model_name)

        if not result["keys_in_environment"]:

            if len(result["missing_keys"]) > 0:
                raise ImageProcessorConfigurationException(
                    f"Missing the following environment variables: {result['missing_keys']}"
                )
            else:
                raise ImageProcessorConfigurationException(
                    f"Failed to validate model environment with MODEL={model_name}"
                )

        if not litellm.supports_vision(model="gpt-4-vision-preview"):
            raise ImageProcessorConfigurationException(f"Vision not supported by {model_name}")

        logger.info("AI API connection is ready")

    async def process_image(image_url: str):
        """Process the given image and respond with the result from the model"""

        mtype, _ = mimetypes.guess_type(image_url)
        if mtype is None:
            raise ImageProcessException(f"Failed to detect mime type for file {mtype}")

        async with aiohttp.ClientSession() as client:
            img_response = await client.get(image_url)
            bytearray = await img_response.read()
            b64img = base64.b64encode(bytearray).decode("utf-8")

        logger.info(f"Sending image with mimetype {mtype}")

        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": TRANSCRIBE_PROMPT},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mtype};base64,{b64img}"},
                },
            ],
        }

        litellm.api_base = os.environ.get("OPENAI_API_BASE")

        response = await litellm.acompletion(
            model=os.getenv("MODEL", "openai/gpt-4o"),
            messages=[message],
        )

        return response.choices[0].message["content"] 
