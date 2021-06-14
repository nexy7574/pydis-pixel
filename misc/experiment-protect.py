import asyncio
import traceback
from asyncio import Queue, get_event_loop, iscoroutine
from lib import api, query_params, render, Pixel, arguments, Fore

start_x, start_y, end_x, end_y, image_width, image_height = query_params()
pilImage, pixels_map, pixels_array = render(image_width, image_height)
loop = get_event_loop()
queue = Queue((image_width+image_height)//2)


async def queue_worker():
    while True:
        work = await queue.get()
        try:
            if iscoroutine(work):
                await work
            else:
                work()
        except Exception:
            traceback.print_exc()
        finally:
            queue.task_done()
worker = loop.create_task(queue_worker())


async def paint(x, y, colour):
    print(Fore.LIGHTBLUE_EX + "[WORKER] " + Fore.LIGHTYELLOW_EX + "Painting ({},{}) #{}.".format(x, y, colour))
    await loop.run_in_executor(
        None,
        api.blind_set_pixel, x, y, colour
    )
    print(Fore.LIGHTBLACK_EX + "[WORKER]" + Fore.LIGHTGREEN_EX + " Painted ({},{}).".format(x, y))


async def main_async():
    # Slow and steady method
    for x, y in pixels_map.keys():
        cursor = (x + start_x, y + start_y)
        pixel: Pixel = await loop.run_in_executor(None, api.get_pixel, x, y)

        if pixel.hex != pixels_map[(x, y)]:
            print(Fore.YELLOW + "[CURSOR] " + Fore.LIGHTRED_EX + f"{cursor} is {pixel.hex} (not {pixels_map[(x,y)]})."
                                                                 f" Adding to queue.")
            if queue.qsize() > queue.maxsize - (queue.maxsize // 4):
                print(Fore.LIGHTBLUE_EX + "[WORKER] " + Fore.YELLOW + f"Queue is getting a bit full "
                                                                      f"({queue.qsize()}/{queue.maxsize}).")
            await queue.put(paint(*cursor, pixels_map[(x, y)]))
            # We run_in_executor because otherwise the time.sleep() in the ratelimit handler would block the loop.
            # Blocking the loop = slower.
        else:
            print(Fore.YELLOW + "[CURSOR] " + Fore.LIGHTGREEN_EX + f"{cursor} is painted correctly.")
    await queue.join()
    return


def main():
    try:
        loop.run_until_complete(main_async())
    except (KeyboardInterrupt, EOFError):
        return


try:
    if arguments.loop is True:
        while True:
            main()
    elif isinstance(arguments.loop, int):
        for i in range(arguments.loop):
            main()
    else:
        main()
except Exception:
    coro = asyncio.wait_for(queue.join(), 10.0)
    try:
        loop.run_until_complete(coro)
    except asyncio.TimeoutError:
        pass
    raise
finally:
    worker.cancel()
