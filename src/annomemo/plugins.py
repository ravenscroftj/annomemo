import aiohttp
import os
import base64

from urllib.parse import urljoin, urlparse

from typing import List


class BotPlugin:

    async def amend_final_response(self, image_url: str, response: str):
        """Plugin is passed the response so far and is allowed to edit the string"""


def load_plugins() -> List[BotPlugin]:
    """Load all applicable plugins"""

    plugins = []

    if os.getenv("MEMOS_URL"):
        plugins.append(MemosPlugin())

    return plugins


class MemosPlugin(BotPlugin):
    """Add the processed data to a memo and append the link to the response"""

    async def memos_add_memo(self, image_url: str, annotation: str):
        """Add a new memo with the image and the corresponding transcription"""

        filename = os.path.basename(urlparse(image_url).path)

        async with aiohttp.ClientSession() as client:

            img_response = await client.get(image_url)
            bytearray = await img_response.read()
            b64img = base64.b64encode(bytearray).decode("utf-8")

            # create the file
            resource_resp = await client.post(
                urljoin(os.getenv("MEMOS_URL"), "/api/v1/resources"),
                headers={"Authorization": f'Bearer {
                    os.getenv("MEMOS_TOKEN")}'},
                json={
                    "content": b64img,
                    "filename": filename,
                },
            )

            resource_json = await resource_resp.json()

            resource_url = urljoin(
                os.getenv("MEMOS_URL"),
                f"/file/{resource_json['name']}/{resource_json['filename']}",
            )

            content = f"""## Image \n\n ![image]({resource_url}) \n\n## Transcription \n\n{
                annotation}\n\n"""

            if os.getenv("MEMOS_TAG"):
                content += f"#{os.getenv('MEMOS_TAG')}\n\n"

            # create the memo
            resp = await client.post(
                urljoin(os.getenv("MEMOS_URL"), "/api/v1/memos"),
                headers={"Authorization": f'Bearer {
                    os.getenv("MEMOS_TOKEN")}'},
                json={
                    "content": content,
                    "filename": filename,
                    "resources": [resource_json],
                },
            )

            note_json = await resp.json()

            return urljoin(os.getenv("MEMOS_URL"), f"/m/{note_json['uid']}")

    async def amend_final_response(self, image_url: str, response: str) -> str:

        post_url = await self.memos_add_memo(image_url, response)

        response += f"\n\n[View the memo]({post_url})"

        return response
