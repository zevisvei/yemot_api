```python
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Request, responses

from yemot_api.api_model import ApiModel
from yemot_api.api_response import IdListMessageType, id_list_message, join, routing_yemot
from yemot_api.input_types import FileAction
from yemot_api.yemot_api import Yemot


def verify_yemot(request: Request) -> Literal[True]:
    user_agent = request.headers.get("user-agent")
    if user_agent != "yemot-core-api/1.0":
        raise HTTPException(status_code=403, detail=f"Access denied: {user_agent}")
    return True


class ApiModelExample(ApiModel):
    path: str
    token: str


# app = FastAPI(dependencies=[Depends(verify_yemot)])
app = FastAPI()


@app.get("/foo")
def foo(q: Annotated[ApiModelExample, Depends()]) -> responses.PlainTextResponse:
    yemot_ins = Yemot(f"{q.api_did}:{q.token}")
    if not yemot_ins.check_if_file_exists(q.path):
        return responses.PlainTextResponse("ERROR", 404)
    content = yemot_ins.download_file(q.path)
    with open("testtt.wav", "wb") as f:
        f.write(content)
    yemot_ins.file_action(FileAction.MOVE, q.path, "1")
    res_1 = id_list_message(IdListMessageType.Text, "הנך מועבר למערכת אחרת")
    res_2 = routing_yemot("0773137770")
    res = join([res_1, res_2])
    return responses.PlainTextResponse(res, 200)
```