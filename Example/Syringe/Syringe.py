
import os
import shutil
import subprocess
import time
import configparser
import psutil
import msvcrt

def read_config():
    config = configparser.ConfigParser()
    config.read('Path.ini')
    return config['Ext']['ClientPath'].strip('"')

def backup_files(src_dir, backup_dir):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    for file in ['ra2md.ini', 'spawn.ini', 'extramap.ini']:
        src = os.path.join(src_dir, file)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(backup_dir, file))

def restore_files(src_dir, backup_dir):
    for file in ['ra2md.ini', 'spawn.ini', 'extramap.ini']:
        src = os.path.join(backup_dir, file)
        if os.path.exists(src):
            shutil.move(src, os.path.join(src_dir, file))
    if os.path.exists(backup_dir):
        shutil.rmtree(backup_dir)

def launch_game(client_path):
    os.chdir(client_path)
    subprocess.Popen(
        'Syringe.exe "gamemd.exe" -SPAWN -CD -NOLOGO -AI -CONTROL',
        shell=True,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP
    )

def process_monitor(process_name, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if any(p.name().lower() == process_name.lower() 
              for p in psutil.process_iter(['name'])):
            return True
        time.sleep(5)
    return False

def terminate_process(process_name):
    try:
        subprocess.run(f'taskkill /f /im {process_name}', shell=True)
        time.sleep(2)
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == process_name.lower():
                proc.kill()
        return True
    except Exception as e:
        print(f"进程终止失败: {str(e)}")
        return False

def main_loop():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backup_dir = os.path.join(script_dir, 'backup_temp')
    client_path = read_config()

    while True:
        print("按S开始游戏，Q退出: ")
        choice = input().strip().upper()
        
        if choice == 'Q':
            break
            
        if choice == 'S':
            backup_files(client_path, backup_dir)
            launch_game(client_path)
            
            if process_monitor('gamemd.exe'):
                print("游戏已启动，按E终止...")
                while True:
                    if msvcrt.kbhit():
                        if msvcrt.getch().decode().upper() == 'E':
                            if terminate_process('gamemd.exe'):
                                print("游戏已终止")
                            break
                    if not any(p.info['name'] == 'gamemd.exe' 
                              for p in psutil.process_iter(['name'])):
                        print("游戏已退出")
                        break
                    time.sleep(1)
            
            restore_files(client_path, backup_dir)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"发生错误: {str(e)}")
