from fastapi import APIRouter
from pydantic import BaseModel

from backend.api.routes.local_agent_routes import send_local_command

router = APIRouter()


class VoiceLocalRequest(BaseModel):
    user_id: str
    command: str
    params: dict = {}


@router.post("/voice/tool/local")
async def voice_tool_local(request: VoiceLocalRequest):
    result = await send_local_command(
        request.user_id,
        request.command,
        request.params,
    )
    if not result.get("success"):
        return {"result": result.get("error", "Command failed")}

    if request.command == "list_files":
        items = result.get("items", [])
        folders = [i["name"] for i in items if i["type"] == "folder"][:5]
        files = [i["name"] for i in items if i["type"] == "file"][:5]
        summary = []
        if folders:
            summary.append(f"Folders: {', '.join(folders)}")
        if files:
            summary.append(f"Files: {', '.join(files)}")
        return {"result": "\n".join(summary) or "Empty folder"}

    elif request.command == "search_files":
        results = result.get("results", [])
        if not results:
            return {"result": "No files found matching that search"}
        found = [f"{r['name']} ({r['path']})" for r in results[:5]]
        return {"result": "Found:\n" + "\n".join(found)}

    elif request.command == "read_file":
        content = result.get("content", "")
        return {"result": content[:1000] if content else "File is empty"}

    else:
        return {"result": result.get("message", "Done")}
