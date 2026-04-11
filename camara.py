import cv2
from pathlib import Path

# ========== Config ==========
DATA_DIR = Path("dataset")          
CAMERA_INDEX = 0                    
ROI_SIZE = 320                      
SAVE_EVERY_N_FRAMES = 3             
JPEG_QUALITY = 95

CLASSES = ["arriba", "abajo", "derecha", "izquierda", "nada"]
# ============================


def ensure_dirs():
    for c in CLASSES:
        (DATA_DIR / c).mkdir(parents=True, exist_ok=True)


def center_crop(frame, size):
    h, w = frame.shape[:2]
    size = min(size, h, w)
    x1 = (w - size) // 2
    y1 = (h - size) // 2
    return frame[y1:y1+size, x1:x1+size], (x1, y1, x1+size, y1+size)


def get_next_number(class_name):
    class_dir = DATA_DIR / class_name
    class_dir.mkdir(parents=True, exist_ok=True)

    existing_files = list(class_dir.glob(f"{class_name}_*.jpg"))
    numbers = []

    for file in existing_files:
        stem = file.stem
        parts = stem.split("_")
        if len(parts) >= 2 and parts[-1].isdigit():
            numbers.append(int(parts[-1]))

    if numbers:
        return max(numbers) + 1
    return 1


def next_filename(class_name):
    class_dir = DATA_DIR / class_name
    next_num = get_next_number(class_name)
    return class_dir / f"{class_name}_{next_num:04d}.jpg"


def count_images_per_class():
    counts = {}
    for c in CLASSES:
        class_dir = DATA_DIR / c
        counts[c] = len(list(class_dir.glob("*.jpg")))
    return counts


def main():
    ensure_dirs()

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError("No pude abrir la cámara. Prueba cambiando CAMERA_INDEX a 1 o 2.")

    active_class = CLASSES[0]
    recording = False
    frame_count = 0
    saved_count = count_images_per_class()

    print("Controles:")
    print("  1 -> clase: arriba")
    print("  2 -> clase: abajo")
    print("  3 -> clase: derecha")
    print("  4 -> clase: izquierda")
    print("  5 -> clase: nada")
    print("  r -> iniciar/detener captura automática")
    print("  c -> capturar UNA imagen ahora")
    print("  q -> salir")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("No pude leer frame de la cámara.")
            break

        frame_count += 1

        roi, (x1, y1, x2, y2) = center_crop(frame, ROI_SIZE)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        hud = f"Clase: {active_class} | Rec: {'ON' if recording else 'OFF'} | " + \
              " ".join([f"{c}={saved_count[c]}" for c in CLASSES])

        cv2.putText(frame, hud, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (50, 255, 50), 2)

        max_count = max(saved_count.values()) if saved_count else 0
        balance_text = "Balance: " + " ".join(
            [f"{c}: faltan {max_count - saved_count[c]}" for c in CLASSES]
        )
        cv2.putText(frame, balance_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

        cv2.imshow("Recolector de dataset (ROI en verde)", frame)

        if recording and (frame_count % SAVE_EVERY_N_FRAMES == 0):
            out_path = next_filename(active_class)
            cv2.imwrite(str(out_path), roi, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            saved_count[active_class] += 1
            print(f"Guardada: {out_path.name}")

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('1'):
            active_class = "arriba"
        elif key == ord('2'):
            active_class = "abajo"
        elif key == ord('3'):
            active_class = "derecha"
        elif key == ord('4'):
            active_class = "izquierda"
        elif key == ord('5'):
            active_class = "nada"
        elif key == ord('r'):
            recording = not recording
            print(f"Grabación {'activada' if recording else 'desactivada'} para clase: {active_class}")
        elif key == ord('c'):
            out_path = next_filename(active_class)
            cv2.imwrite(str(out_path), roi, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            saved_count[active_class] += 1
            print(f"Guardada: {out_path.name}")

    cap.release()
    cv2.destroyAllWindows()
    print("Listo. Dataset guardado en:", DATA_DIR.resolve())


if __name__ == "__main__":
    main()