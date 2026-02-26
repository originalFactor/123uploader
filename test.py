# Copyright (c) 2026 deskt
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import pan123
import json
import typing
import logging
import random
import string

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

with open("secret.json", "r") as f:
    secrets = typing.cast(dict[str, str], json.load(f))

client_id = secrets["client_id"]
client_secret = secrets["client_secret"]

RANDOM_POOL = string.ascii_letters + string.digits


def summon_random_file(size: int = 32 * 1024) -> str:
    filename = f"{''.join(random.choices(RANDOM_POOL, k=8))}.bin"
    with open(filename, "wb") as f:
        for a in range(0, size, 1024):
            _ = f.write(random.randbytes(min(size - a, 1024)))
    return filename


async def test_userinfo(client: pan123.Pan123):
    user = await client.user.info()
    print(user.model_dump_json(indent=2))


async def test_mkdir(client: pan123.Pan123):
    mkdir = await client.files.mkdir(
        parent_id=0,
        name="test",
    )
    print(mkdir.model_dump_json(indent=2))


async def test_upload(client: pan123.Pan123):
    filename = summon_random_file()
    fileid = await client.files.upload(
        local_path=filename,
        remote_path=f"/test2/{filename}",
        parent_id=0,
        do_cover=True,
    )
    print(fileid)


async def test_rename(client: pan123.Pan123):
    rename = await client.files.rename(
        files={
            32521359: "test2.bin",
        },
    )
    print(rename.model_dump_json(indent=2))


async def test_trash(client: pan123.Pan123):
    await client.files.trash(
        file_ids=[32521359],
    )


async def test_copy(client: pan123.Pan123):
    copy = await client.files.copy(
        file_id=32521375,
        target_dir_id=0,
    )
    print(copy.model_dump_json(indent=2))


async def test_copy_async(client: pan123.Pan123):
    copy = await client.files.copy_async(
        file_ids=[32521375],
        target_dir_id=0,
    )
    print(copy.model_dump_json(indent=2))
    while True:
        progress = await client.files.copy_progress(
            task_id=copy.taskId,
        )
        print(progress.model_dump_json(indent=2))
        enum = pan123.file.enums.CopyProgressEnum
        if progress.status in [enum.COMPLETED, enum.FAILED]:
            break
        await asyncio.sleep(1)


async def test_recover(client: pan123.Pan123):
    recover = await client.files.recover(
        file_ids=[32521359],
    )
    print(recover.model_dump_json(indent=2))


async def test_reover_by_path(client: pan123.Pan123):
    await client.files.recover_by_path(
        file_ids=[32521359],
        target_dir_id=0,
    )


async def test_infos(client: pan123.Pan123):
    infos = await client.files.infos(
        file_ids=[32521359],
    )
    print(infos.model_dump_json(indent=2))


async def test_search(client: pan123.Pan123):
    search = await client.files.search(
        dir_id=0,
    )
    print(search.model_dump_json(indent=2))


async def test_move(client: pan123.Pan123):
    move = await client.files.move(
        file_ids=[32521375],
        target_dir_id=0,
    )


async def test_download(client: pan123.Pan123):
    download = await client.files.download(file_id=32308613, local_path="test.bin")


async def main():
    async with pan123.Pan123(
        client_id=client_id, client_secret=client_secret
    ) as client:
        # await test_userinfo(client)
        # await test_mkdir(client)
        # await test_upload(client)
        # await test_rename(client)
        # await test_trash(client)
        # await test_copy(client)
        # await test_recover(client)
        # await test_reover_by_path(client)
        # await test_infos(client)
        # await test_search(client)
        # await test_move(client)
        await test_download(client)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
