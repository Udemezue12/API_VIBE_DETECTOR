from asgiref.sync import sync_to_async
async def run_sync(func, *args, **kwargs):
   
    return await sync_to_async(func)(*args, **kwargs)