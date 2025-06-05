import mss
from PIL import Image
import time
from video_feed import screen_ocr, video_embedder, chroma_client, vision_captioner

interval_sec = 1  # capture interval in seconds

print("=== Screen Capture (Per-Monitor) ===")
print(f"Interval: {interval_sec} seconds")
print("Press Ctrl+C to stop.\n")

with mss.mss() as sct:
    monitors = sct.monitors[1:]  # skip index 0 (virtual), get actual monitors

    print("Available monitors:")
    for i, monitor in enumerate(monitors, start=1):
        print(f"Monitor {i}: {monitor}")
    print("")

    frame_num = 0
    try:
        while True:
            for i, monitor in enumerate(monitors, start=1):
                # Capture this monitor
                screenshot = sct.grab(monitor)

                # Convert to PIL image (in-memory)
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)

               # Generate caption
                caption = vision_captioner.generate_caption(img)

                # Extract screen text (OCR)
                screen_text = screen_ocr.extract_text(img)

                # print(f"[Frame {frame_num:04d} | Monitor {i}] Caption: {caption}")
                # print(f"[Frame {frame_num:04d} | Monitor {i}] OCR Text: {screen_text}")

                # Embed image
                embedding = video_embedder.embed_pil_image(img)

                # Save embedding + metadata to Chroma
                chroma_client.save_embedding(
                    id=f"frame_{frame_num:04d}_mon{i}",
                    embedding=embedding,
                    metadata={
                        "frame_num": frame_num,
                        "timestamp": time.time(),
                        "monitor_id": i,
                        "caption": caption,
                        "screen_text": screen_text
                    }
                )

            frame_num += 1
            time.sleep(interval_sec)

    except KeyboardInterrupt:
        print("\nStopping screen capture.")