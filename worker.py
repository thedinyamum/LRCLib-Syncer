from concurrent.futures import ThreadPoolExecutor, as_completed

from tqdm import tqdm


def process_batch(
    files,
    process,
    missing,
    instrumentals,
    stats,
    workers=8,
    interactive=False,
):
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                process,
                f,
                missing,
                instrumentals,
                stats,
                interactive,
            )
            for f in files
        ]

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            unit="song",
        ):
            future.result()
