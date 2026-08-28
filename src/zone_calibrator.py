import os
import yaml
import cv2

CFG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.yaml')

class RectDrawer:
    def __init__(self, name, color=(0, 255, 255)):
        self.name = name
        self.color = color
        self.start = None
        self.end = None
        self.drawing = False
        self.rect = None

    def on_mouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start = (x, y)
            self.end = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.end = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.end = (x, y)
            x1, y1 = self.start
            x2, y2 = self.end
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)
            self.rect = [x1, y1, x2, y2]

    def draw(self, frame):
        if self.start and self.end:
            cv2.rectangle(frame, self.start, self.end, self.color, 2)
        if self.rect:
            x1, y1, x2, y2 = self.rect
            cv2.rectangle(frame, (x1, y1), (x2, y2), self.color, 2)
            cv2.putText(frame, self.name, (x1+5, y1+20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.color, 2)


def calibrate(source=None):
    # Load config to match video resolution and existing line
    with open(CFG_PATH, 'r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)
    vcfg = cfg.get('video', {})
    width = int(vcfg.get('width', 640))
    height = int(vcfg.get('height', 480))
    
    # Use camera source from config if not specified
    if source is None:
        source = vcfg.get('source', 1)
    
    print(f"Opening camera source: {source}")
    cap = cv2.VideoCapture(int(source) if str(source).isdigit() else source)
    
    if not cap.isOpened():
        print(f"ERROR: Could not open camera {source}")
        print("Trying alternative camera indices...")
        for alt in [1, 0, 2]:
            print(f"  Trying camera {alt}...")
            cap = cv2.VideoCapture(alt)
            if cap.isOpened():
                ret, test_frame = cap.read()
                if ret and test_frame is not None and test_frame.max() > 1:
                    print(f"  SUCCESS: Using camera {alt}")
                    source = alt
                    break
                cap.release()
        
        if not cap.isOpened():
            print("ERROR: Could not open any camera!")
            print("Please ensure:")
            print("  1. Camera is connected")
            print("  2. No other application is using the camera")
            print("  3. Camera drivers are installed")
            return
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    print(f"Camera opened successfully: {source}")
    print(f"Resolution: {width}x{height}")
    cv2.namedWindow('Calibrate Zones')

    shelf = RectDrawer('shelf', (255, 255, 0))
    checkout = RectDrawer('checkout', (255, 0, 255))
    exitz = RectDrawer('exit', (0, 255, 255))

    # Preload existing rectangles
    try:
        zs = cfg.get('zones', {})
        if 'shelf' in zs:
            shelf.rect = list(map(int, zs['shelf']))
        if 'checkout' in zs:
            checkout.rect = list(map(int, zs['checkout']))
        if 'exit' in zs:
            exitz.rect = list(map(int, zs['exit']))
    except Exception:
        pass

    # Checkout line management
    checkout_line = None
    lcfg = cfg.get('lines', {})
    if isinstance(lcfg.get('checkout'), list) and len(lcfg['checkout']) == 4:
        x1, y1, x2, y2 = lcfg['checkout']
        checkout_line = ((int(x1), int(y1)), (int(x2), int(y2)))

    active = 'shelf'
    cv2.setMouseCallback('Calibrate Zones', shelf.on_mouse)

    print('\n' + '='*50)
    print('ZONE CALIBRATION INSTRUCTIONS:')
    print('='*50)
    print('Draw zones by CLICK and DRAG on the video window')
    print('')
    print('KEYBOARD SHORTCUTS:')
    print('  1 = Draw SHELF zone (yellow)')
    print('  2 = Draw CHECKOUT zone (magenta)')
    print('  3 = Draw EXIT zone (cyan)')
    print('  l = Set checkout line at left edge of checkout zone')
    print('  r = Remove checkout line')
    print('  s = SAVE zones to config (MUST DO THIS!)')
    print('  q = Quit without saving')
    print('')
    print('TIPS:')
    print('  - Start with key "1" to draw SHELF zone')
    print('  - Press "2" then draw CHECKOUT zone')
    print('  - Press "3" then draw EXIT zone')
    print('  - Press "s" to SAVE before quitting!')
    print('='*50)
    print('\nCurrently drawing: SHELF (yellow)')
    print('Press "1", "2", or "3" to switch zones\n')

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # switch callbacks based on active
        if active == 'shelf':
            cv2.setMouseCallback('Calibrate Zones', shelf.on_mouse)
        elif active == 'checkout':
            cv2.setMouseCallback('Calibrate Zones', checkout.on_mouse)
        else:
            cv2.setMouseCallback('Calibrate Zones', exitz.on_mouse)

        shelf.draw(frame)
        checkout.draw(frame)
        exitz.draw(frame)

        # draw checkout line if present
        if checkout_line is not None:
            cv2.line(frame, checkout_line[0], checkout_line[1], (0, 0, 255), 2)

        cv2.imshow('Calibrate Zones', frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('1'):
            active = 'shelf'
            print('Now drawing: SHELF zone (yellow)')
        elif k == ord('2'):
            active = 'checkout'
            print('Now drawing: CHECKOUT zone (magenta)')
        elif k == ord('3'):
            active = 'exit'
            print('Now drawing: EXIT zone (cyan)')
        elif k == ord('l'):
            # set checkout line to left edge of checkout rect
            if checkout.rect:
                x1, y1, x2, y2 = checkout.rect
                checkout_line = ((x1, y1), (x1, y2))
                print('✓ Checkout line set to left edge of checkout zone.')
            else:
                print('✗ Draw checkout zone first (press "2" then draw)')
        elif k == ord('r'):
            checkout_line = None
            print('✓ Checkout line removed.')
        elif k == ord('s'):
            # save to config
            if not shelf.rect or not checkout.rect or not exitz.rect:
                print('✗ ERROR: You must draw all 3 zones before saving!')
                print(f'  Shelf: {"✓" if shelf.rect else "✗ MISSING"}')
                print(f'  Checkout: {"✓" if checkout.rect else "✗ MISSING"}')
                print(f'  Exit: {"✓" if exitz.rect else "✗ MISSING"}')
                continue
            
            with open(CFG_PATH, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f)
            cfg.setdefault('zones', {})
            if shelf.rect:
                cfg['zones']['shelf'] = shelf.rect
            if checkout.rect:
                cfg['zones']['checkout'] = checkout.rect
            if exitz.rect:
                cfg['zones']['exit'] = exitz.rect
            # lines.checkout optional
            cfg.setdefault('lines', {})
            if checkout_line is not None:
                (cx1, cy1), (cx2, cy2) = checkout_line
                cfg['lines']['checkout'] = [int(cx1), int(cy1), int(cx2), int(cy2)]
            else:
                # remove if exists
                if 'checkout' in cfg.get('lines', {}):
                    del cfg['lines']['checkout']
            with open(CFG_PATH, 'w', encoding='utf-8') as f:
                yaml.safe_dump(cfg, f)
            print('\n' + '='*50)
            print('✓ SUCCESS! Zones saved to config/config.yaml')
            print('='*50)
            print('Saved zones:')
            print(f'  Shelf: {shelf.rect}')
            print(f'  Checkout: {checkout.rect}')
            print(f'  Exit: {exitz.rect}')
            if checkout_line:
                print(f'  Checkout line: Yes')
            print('\nYou can now close this window and restart the detection system.')
            print('='*50)
        elif k == ord('q'):
            print('\nQuitting without saving...')
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    calibrate()
