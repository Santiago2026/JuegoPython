import cv2
import os
import time
from pathlib import Path

# ========== Config ==========
DATA_DIR = Path("dataset")          # carpeta raíz del dataset
CAMERA_INDEX = 0                    # 0 suele ser la cámara principal
ROI_SIZE = 320                      # tamaño del recorte central (cuadrado)
SAVE_EVERY_N_FRAMES = 3             # guarda 1 imagen cada N frames cuando está en modo grabación
JPEG_QUALITY = 95

CLASSES = ["arriba", "abajo", "derecha", "izquierda"]  # Mis 2 figuras
# ============================


##Este metodo nos ayuda para ver si el directorio esta creado o no en caso de que no lo crea
def ensure_dirs():
    for c in CLASSES:
        (DATA_DIR / c).mkdir(parents=True, exist_ok=True)


##Ubicacion del recuadro de la camara
def center_crop(frame, size):
    h, w = frame.shape[:2]
    size = min(size, h, w)
    x1 = (w - size) // 2
    y1 = (h - size) // 2
    return frame[y1:y1+size, x1:x1+size], (x1, y1, x1+size, y1+size)

##Nombre de las fotos 
def next_filename(class_name):
    class_dir = DATA_DIR / class_name
    class_dir.mkdir(parents=True, exist_ok=True)
    # nombre con timestamp para evitar colisiones
    ts = int(time.time() * 1000)
    return class_dir / f"{class_name}_{ts}.jpg"

def main():
    ensure_dirs()

    ##Abrimos la camara 
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        raise RuntimeError("No pude abrir la cámara. Prueba cambiando CAMERA_INDEX a 1 o 2.")

    active_class = CLASSES[0]
    recording = False
    frame_count = 0
    saved_count = {c: 0 for c in CLASSES}

    #INstrucciones de consola
    print("Controles:")
    print("  1 -> clase: arriba")
    print("  2 -> clase: abajo")
    print("  3 -> clase: derecha")
    print("  4 -> clase: izquierda")
    print("  r -> iniciar/detener captura automática (múltiples imágenes)")
    print("  c -> capturar UNA imagen ahora")
    print("  q -> salir")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("No pude leer frame de la cámara.")
            break

        frame_count += 1

        # ROI (recorte central) + rectángulo visual
        roi, (x1, y1, x2, y2) = center_crop(frame, ROI_SIZE)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # HUD (texto en pantalla)
        hud = f"Clase: {active_class} | Rec: {'ON' if recording else 'OFF'} | Guardadas: " + \
              " ".join([f"{c}={saved_count[c]}" for c in CLASSES])
        cv2.putText(frame, hud, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (50, 255, 50), 2)

        cv2.imshow("Recolector de dataset (ROI en verde)", frame)

        # Guardado automático cada N frames si está grabando
        if recording and (frame_count % SAVE_EVERY_N_FRAMES == 0):
            out_path = next_filename(active_class)
            cv2.imwrite(str(out_path), roi, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            saved_count[active_class] += 1

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
        elif key == ord('r'):
            recording = not recording
        elif key == ord('c'):
            out_path = next_filename(active_class)
            cv2.imwrite(str(out_path), roi, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            saved_count[active_class] += 1

    cap.release()
    cv2.destroyAllWindows()
    print("Listo. Dataset guardado en:", DATA_DIR.resolve())

if __name__ == "__main__":
    main()