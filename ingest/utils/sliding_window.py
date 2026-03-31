def window_update(message, sliding_window, max_size):
    if len(sliding_window) < max_size:
        sliding_window.append(message)
    else:
        sliding_window.pop(0)
        sliding_window.append(message)

def window_alarm(sliding_window, alarm_threshold:float, data:str):
    if data == 'temperatura':
        if sum(sliding_window)/len(sliding_window) > float(alarm_threshold):
            print(f"Warning: valor de {data} excede los límites de seguridad")
    if data == 'presion':
        if sum(sliding_window)/len(sliding_window) < float(alarm_threshold):
            print(f"Warning: valor de {data} por debajo de los límites")