import requests, aiohttp

class WandboxAsync:
    baseUrl = "https://wandbox.org/api"

    async def get(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(WandboxAsync.baseUrl + url) as response:
                return await response.json()

    async def post(url, data = None):
        async with aiohttp.ClientSession() as session:
            async with session.post(WandboxAsync.baseUrl + url, json = data) as response:
                return await response.json()

    async def getList():
        return await WandboxAsync.get("/list.json")

    async def compileCode(compiler, code):
        response = await WandboxAsync.post("/compile.json", {
            "compiler": compiler,
            "code": code
        })
        print(response)

        if response.get("status"):
            if response["status"] == "0":
                return {
                    "status": "success",
                    "message": response.get("program_message", "") + response.get("compiler_message", "")
                }
            else:
                return {
                    "status": "fail",
                    "message": response.get("program_message", "") + response.get("compiler_message", "")
                }
        elif response.get("signal"):
            if response["signal"] == "Killed":
                return {
                    "status": "killed",
                    "message": response.get("program_message", "") + response.get("compiler_message", "")
                }
